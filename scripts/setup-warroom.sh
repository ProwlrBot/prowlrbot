#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════╗
# ║           ProwlrHub War Room — Setup Wizard                  ║
# ║   Connect multiple Claude Code terminals as one team         ║
# ╚══════════════════════════════════════════════════════════════╝
set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

PROWLR_DIR="${HOME}/.prowlrbot"
DB_PATH="${PROWLR_DIR}/warroom.db"
TOTAL_STEPS=7
NETWORK_MODE="local"
HUB_URL=""

# ── Banner ──────────────────────────────────────────────────
banner() {
    echo ""
    echo -e "${CYAN}${BOLD}"
    echo "  ╔═══════════════════════════════════════════╗"
    echo "  ║                                           ║"
    echo "  ║     🐾  ProwlrHub War Room Setup  🐾      ║"
    echo "  ║                                           ║"
    echo "  ║   Always watching. Always coordinating.   ║"
    echo "  ║                                           ║"
    echo "  ╚═══════════════════════════════════════════╝"
    echo -e "${NC}"
}

# ── Step display ────────────────────────────────────────────
step() {
    echo ""
    echo -e "${GREEN}${BOLD}[$1/$TOTAL_STEPS]${NC} ${BOLD}$2${NC}"
    echo -e "${DIM}────────────────────────────────────────${NC}"
}

ok() {
    echo -e "  ${GREEN}✓${NC} $1"
}

warn() {
    echo -e "  ${YELLOW}!${NC} $1"
}

fail() {
    echo -e "  ${RED}✗${NC} $1"
}

info() {
    echo -e "  ${DIM}$1${NC}"
}

# ── Main ────────────────────────────────────────────────────
banner

# Step 1: Detect environment
step "1" "Detecting environment"

# Find project root (where this script lives)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

if [ -f "$PROJECT_ROOT/src/prowlrbot/hub/mcp_server.py" ]; then
    ok "Found ProwlrHub at: $PROJECT_ROOT"
else
    fail "Cannot find ProwlrHub source. Run this from the prowlrbot repo."
    exit 1
fi

# Find Python
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PY_VERSION=$("$cmd" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
        PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
        PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
        if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 10 ]; then
            PYTHON="$(command -v "$cmd")"
            ok "Python: $PYTHON ($(${cmd} --version 2>&1))"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    fail "Python 3.10+ required. Install from https://python.org"
    exit 1
fi

# Detect platform
PLATFORM="$(uname -s)"
HOSTNAME="$(hostname -s 2>/dev/null || hostname)"
ok "Platform: $PLATFORM ($HOSTNAME)"

# Step 2: Install dependencies
step "2" "Checking dependencies"

if PYTHONPATH="$PROJECT_ROOT/src" "$PYTHON" -c "import prowlrbot.hub" 2>/dev/null; then
    ok "prowlrbot.hub module found"
else
    warn "Installing prowlrbot in dev mode..."
    cd "$PROJECT_ROOT"
    "$PYTHON" -m pip install -e ".[dev]" --quiet 2>/dev/null || {
        warn "pip install failed, using PYTHONPATH fallback"
    }
    ok "Dependencies ready"
fi

# Step 3: Initialize database
step "3" "Initializing war room database"

mkdir -p "$PROWLR_DIR"

PYTHONPATH="$PROJECT_ROOT/src" "$PYTHON" -c "
from prowlrbot.hub.db import init_db
conn = init_db('$DB_PATH')
conn.close()
print('  ✓ Database initialized at: $DB_PATH')
" 2>/dev/null

# Check if rooms exist
ROOM_COUNT=$(PYTHONPATH="$PROJECT_ROOT/src" "$PYTHON" -c "
from prowlrbot.hub.engine import WarRoomEngine
e = WarRoomEngine('$DB_PATH')
r = e.get_or_create_default_room()
agents = e.get_agents(r['room_id'])
tasks = e.get_mission_board(r['room_id'])
print(f'{len(agents)} agents, {len(tasks)} tasks on board')
e.close()
" 2>/dev/null)
ok "War room status: $ROOM_COUNT"

# Step 4: Agent identity
step "4" "Setting up agent identity"

echo ""
echo -e "  ${BOLD}What should this terminal be called?${NC}"
echo -e "  ${DIM}Examples: backend-architect, frontend-lead, security-scout${NC}"
echo -e "  ${DIM}Press Enter for auto-name: claude-${HOSTNAME}-$$${NC}"
echo ""
read -p "  Agent name: " AGENT_NAME
AGENT_NAME="${AGENT_NAME:-claude-${HOSTNAME}-$$}"
ok "Agent name: $AGENT_NAME"

echo ""
echo -e "  ${BOLD}What can this agent do?${NC} (comma-separated)"
echo -e "  ${DIM}Examples: python,api,database  |  frontend,typescript,react${NC}"
echo -e "  ${DIM}          security,testing      |  docs,git,devops${NC}"
echo -e "  ${DIM}Press Enter for: general${NC}"
echo ""
read -p "  Capabilities: " CAPABILITIES
CAPABILITIES="${CAPABILITIES:-general}"
ok "Capabilities: $CAPABILITIES"

# Step 5: Network setup
step "5" "Network configuration"

echo ""
echo -e "  ${BOLD}How are your machines connected?${NC}"
echo ""
echo -e "  ${GREEN}1)${NC} Same machine (all terminals on this computer)"
echo -e "  ${GREEN}2)${NC} Same network (Mac + WSL or multiple machines on same WiFi)"
echo -e "  ${GREEN}3)${NC} Different networks (guest WiFi, VPN, remote machines)"
echo ""
read -p "  Choose [1/2/3] (default: 1): " NETWORK_CHOICE
NETWORK_CHOICE="${NETWORK_CHOICE:-1}"

case "$NETWORK_CHOICE" in
    1)
        NETWORK_MODE="local"
        ok "Local mode — all terminals share SQLite directly"
        ;;
    2)
        NETWORK_MODE="bridge"
        echo ""
        echo -e "  ${BOLD}Is this the HOST machine (runs the database)?${NC}"
        read -p "  [y/n] (default: y): " IS_HOST
        IS_HOST="${IS_HOST:-y}"

        if [[ "$IS_HOST" =~ ^[Yy] ]]; then
            # This machine hosts the bridge
            LOCAL_IP=""
            if [ "$PLATFORM" = "Darwin" ]; then
                LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || echo "")
            else
                LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "")
            fi

            if [ -n "$LOCAL_IP" ]; then
                ok "Your local IP: $LOCAL_IP"
            else
                warn "Could not detect local IP. Find it with: ipconfig getifaddr en0 (Mac) or hostname -I (Linux)"
            fi

            echo ""
            echo -e "  ${BOLD}Start the bridge now?${NC}"
            echo -e "  ${DIM}Other machines will connect to http://${LOCAL_IP:-YOUR_IP}:8099${NC}"
            read -p "  [y/n] (default: n): " START_BRIDGE
            START_BRIDGE="${START_BRIDGE:-n}"

            if [[ "$START_BRIDGE" =~ ^[Yy] ]]; then
                echo ""
                info "Starting bridge in background..."
                PYTHONPATH="$PROJECT_ROOT/src" nohup "$PYTHON" -m prowlrbot.hub.bridge > "$PROWLR_DIR/bridge.log" 2>&1 &
                BRIDGE_PID=$!
                sleep 2

                if kill -0 $BRIDGE_PID 2>/dev/null; then
                    ok "Bridge running on port 8099 (PID: $BRIDGE_PID)"
                    ok "Log: $PROWLR_DIR/bridge.log"
                    echo ""
                    echo -e "  ${BOLD}Tell remote agents to set:${NC}"
                    echo -e "  ${CYAN}PROWLR_HUB_URL=http://${LOCAL_IP:-YOUR_IP}:8099${NC}"
                else
                    fail "Bridge failed to start. Check $PROWLR_DIR/bridge.log"
                fi
            else
                echo ""
                info "To start the bridge later:"
                echo -e "  ${CYAN}PYTHONPATH=$PROJECT_ROOT/src $PYTHON -m prowlrbot.hub.bridge${NC}"
            fi
        else
            # This machine connects to an existing bridge
            echo ""
            echo -e "  ${BOLD}Enter the bridge URL:${NC}"
            echo -e "  ${DIM}Example: http://192.168.1.100:8099${NC}"
            echo ""
            read -p "  Bridge URL: " HUB_URL

            if [ -n "$HUB_URL" ]; then
                # Test connectivity
                if curl -sf "$HUB_URL/health" >/dev/null 2>&1; then
                    ok "Connected to bridge at $HUB_URL"
                else
                    warn "Cannot reach $HUB_URL — make sure the bridge is running"
                fi
            else
                fail "No URL provided. Set PROWLR_HUB_URL manually in .mcp.json"
            fi
        fi
        ;;
    3)
        NETWORK_MODE="tunnel"
        echo ""
        echo -e "  ${BOLD}Your machines are on different networks.${NC}"
        echo -e "  ${DIM}You need a tunnel to connect them.${NC}"
        echo ""
        echo -e "  ${BOLD}Which tunnel service?${NC}"
        echo ""

        # Detect what's installed
        HAS_TAILSCALE=false
        HAS_CLOUDFLARED=false
        HAS_NGROK=false

        command -v tailscale &>/dev/null && HAS_TAILSCALE=true
        command -v cloudflared &>/dev/null && HAS_CLOUDFLARED=true
        command -v ngrok &>/dev/null && HAS_NGROK=true

        INSTALLED_LABEL=""
        echo -e "  ${GREEN}1)${NC} Tailscale — mesh VPN, stable IPs, best for ongoing dev"
        $HAS_TAILSCALE && echo -e "     ${GREEN}(installed)${NC}" || echo -e "     ${DIM}(not installed — brew install tailscale)${NC}"

        echo -e "  ${GREEN}2)${NC} Cloudflare Tunnel — instant HTTPS URL, no account needed"
        $HAS_CLOUDFLARED && echo -e "     ${GREEN}(installed)${NC}" || echo -e "     ${DIM}(not installed — brew install cloudflared)${NC}"

        echo -e "  ${GREEN}3)${NC} ngrok — tunnel to localhost"
        $HAS_NGROK && echo -e "     ${GREEN}(installed)${NC}" || echo -e "     ${DIM}(not installed — brew install ngrok)${NC}"

        echo -e "  ${GREEN}4)${NC} SSH tunnel — no third-party service"
        echo -e "  ${GREEN}5)${NC} I already have a URL (manual)"
        echo ""
        read -p "  Choose [1-5]: " TUNNEL_CHOICE

        case "$TUNNEL_CHOICE" in
            1)
                if $HAS_TAILSCALE; then
                    TS_IP=$(tailscale ip -4 2>/dev/null || echo "")
                    if [ -n "$TS_IP" ]; then
                        ok "Tailscale IP: $TS_IP"
                        echo ""
                        echo -e "  ${BOLD}Is this the HOST machine (runs the bridge)?${NC}"
                        read -p "  [y/n] (default: y): " IS_HOST
                        IS_HOST="${IS_HOST:-y}"

                        if [[ "$IS_HOST" =~ ^[Yy] ]]; then
                            HUB_URL=""
                            echo -e "  ${BOLD}Tell remote agents:${NC} ${CYAN}PROWLR_HUB_URL=http://$TS_IP:8099${NC}"

                            read -p "  Start bridge now? [y/n] (default: n): " START_BRIDGE
                            if [[ "${START_BRIDGE:-n}" =~ ^[Yy] ]]; then
                                PYTHONPATH="$PROJECT_ROOT/src" nohup "$PYTHON" -m prowlrbot.hub.bridge > "$PROWLR_DIR/bridge.log" 2>&1 &
                                sleep 2
                                ok "Bridge running. Remote URL: http://$TS_IP:8099"
                            fi
                        else
                            echo ""
                            echo -e "  ${BOLD}Enter the host's Tailscale IP:${NC}"
                            read -p "  Tailscale IP: " TS_HOST_IP
                            HUB_URL="http://${TS_HOST_IP}:8099"
                            ok "Will connect to $HUB_URL"
                        fi
                    else
                        warn "Tailscale installed but not connected. Run: sudo tailscale up"
                    fi
                else
                    echo ""
                    echo -e "  ${BOLD}Install Tailscale:${NC}"
                    echo -e "  ${CYAN}brew install tailscale${NC}  (macOS)"
                    echo -e "  ${CYAN}curl -fsSL https://tailscale.com/install.sh | sh${NC}  (Linux/WSL)"
                    echo ""
                    echo -e "  Then run: ${CYAN}sudo tailscale up${NC}"
                    echo -e "  Get your IP: ${CYAN}tailscale ip -4${NC}"
                fi
                ;;
            2)
                if $HAS_CLOUDFLARED; then
                    echo ""
                    echo -e "  ${BOLD}Is this the HOST machine?${NC}"
                    read -p "  [y/n] (default: y): " IS_HOST
                    IS_HOST="${IS_HOST:-y}"

                    if [[ "$IS_HOST" =~ ^[Yy] ]]; then
                        echo ""
                        info "Starting bridge + Cloudflare tunnel..."
                        PYTHONPATH="$PROJECT_ROOT/src" nohup "$PYTHON" -m prowlrbot.hub.bridge > "$PROWLR_DIR/bridge.log" 2>&1 &
                        sleep 2

                        # Start cloudflared and capture the URL
                        cloudflared tunnel --url http://localhost:8099 2>&1 | tee "$PROWLR_DIR/tunnel.log" &
                        TUNNEL_PID=$!
                        sleep 5

                        TUNNEL_URL=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$PROWLR_DIR/tunnel.log" | head -1)
                        if [ -n "$TUNNEL_URL" ]; then
                            ok "Tunnel URL: $TUNNEL_URL"
                            echo ""
                            echo -e "  ${BOLD}Tell remote agents:${NC}"
                            echo -e "  ${CYAN}PROWLR_HUB_URL=$TUNNEL_URL${NC}"
                        else
                            warn "Could not detect tunnel URL. Check $PROWLR_DIR/tunnel.log"
                        fi
                    else
                        echo ""
                        echo -e "  ${BOLD}Enter the Cloudflare tunnel URL:${NC}"
                        read -p "  URL: " HUB_URL
                    fi
                else
                    echo ""
                    echo -e "  ${BOLD}Install cloudflared:${NC}"
                    echo -e "  ${CYAN}brew install cloudflared${NC}  (macOS)"
                    echo -e "  ${CYAN}curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared && chmod +x /usr/local/bin/cloudflared${NC}  (Linux)"
                fi
                ;;
            3)
                if $HAS_NGROK; then
                    echo ""
                    echo -e "  ${BOLD}Is this the HOST machine?${NC}"
                    read -p "  [y/n] (default: y): " IS_HOST
                    IS_HOST="${IS_HOST:-y}"

                    if [[ "$IS_HOST" =~ ^[Yy] ]]; then
                        info "Start the bridge first, then run:"
                        echo -e "  ${CYAN}ngrok http 8099${NC}"
                        echo -e "  ${DIM}Copy the https:// URL and give it to remote agents${NC}"
                    else
                        echo ""
                        echo -e "  ${BOLD}Enter the ngrok URL:${NC}"
                        read -p "  URL: " HUB_URL
                    fi
                else
                    echo ""
                    echo -e "  ${BOLD}Install ngrok:${NC}"
                    echo -e "  ${CYAN}brew install ngrok${NC}  (macOS)"
                    echo -e "  ${CYAN}snap install ngrok${NC}  (Linux)"
                fi
                ;;
            4)
                echo ""
                echo -e "  ${BOLD}SSH Tunnel Setup:${NC}"
                echo -e "  ${DIM}On the remote machine, run:${NC}"
                echo -e "  ${CYAN}ssh -L 8099:localhost:8099 user@host-machine -N${NC}"
                echo -e "  ${DIM}Then set PROWLR_HUB_URL=http://localhost:8099${NC}"
                HUB_URL="http://localhost:8099"
                ;;
            5)
                echo ""
                read -p "  Enter bridge URL: " HUB_URL
                ;;
        esac
        ;;
esac

# Step 6: Configure MCP
step "6" "Configuring Claude Code MCP integration"

MCP_CONFIG_FILE="$PROJECT_ROOT/.mcp.json"

# Check if prowlr-hub already exists in config
if [ -f "$MCP_CONFIG_FILE" ] && grep -q "prowlr-hub" "$MCP_CONFIG_FILE" 2>/dev/null; then
    ok "MCP config already has prowlr-hub entry"
    info "Updating agent name and capabilities..."

    # Use Python to update the JSON properly
    PYTHONPATH="$PROJECT_ROOT/src" "$PYTHON" -c "
import json

with open('$MCP_CONFIG_FILE') as f:
    config = json.load(f)

config['mcpServers']['prowlr-hub']['env']['PROWLR_AGENT_NAME'] = '$AGENT_NAME'
config['mcpServers']['prowlr-hub']['env']['PROWLR_CAPABILITIES'] = '$CAPABILITIES'
config['mcpServers']['prowlr-hub']['env']['PYTHONPATH'] = '$PROJECT_ROOT/src'
config['mcpServers']['prowlr-hub']['cwd'] = '$PROJECT_ROOT'
config['mcpServers']['prowlr-hub']['command'] = '$PYTHON'

hub_url = '$HUB_URL'
if hub_url:
    config['mcpServers']['prowlr-hub']['env']['PROWLR_HUB_URL'] = hub_url
elif 'PROWLR_HUB_URL' in config['mcpServers']['prowlr-hub']['env']:
    del config['mcpServers']['prowlr-hub']['env']['PROWLR_HUB_URL']

with open('$MCP_CONFIG_FILE', 'w') as f:
    json.dump(config, f, indent=2)
    f.write('\n')

print('  ✓ Updated .mcp.json with agent identity')
"
else
    info "Adding prowlr-hub to MCP config..."

    PYTHONPATH="$PROJECT_ROOT/src" "$PYTHON" -c "
import json, os

config = {'mcpServers': {}}
if os.path.exists('$MCP_CONFIG_FILE'):
    with open('$MCP_CONFIG_FILE') as f:
        config = json.load(f)

env = {
    'PYTHONPATH': '$PROJECT_ROOT/src',
    'PROWLR_AGENT_NAME': '$AGENT_NAME',
    'PROWLR_CAPABILITIES': '$CAPABILITIES'
}

hub_url = '$HUB_URL'
if hub_url:
    env['PROWLR_HUB_URL'] = hub_url

config['mcpServers']['prowlr-hub'] = {
    'command': '$PYTHON',
    'args': ['-m', 'prowlrbot.hub'],
    'cwd': '$PROJECT_ROOT',
    'env': env
}

with open('$MCP_CONFIG_FILE', 'w') as f:
    json.dump(config, f, indent=2)
    f.write('\n')

print('  ✓ Created .mcp.json with prowlr-hub entry')
"
fi

# Step 7: Verify
step "7" "Verifying installation"

# Test MCP server starts and responds
TEST_RESULT=$(echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | \
    PYTHONPATH="$PROJECT_ROOT/src" \
    PROWLR_AGENT_NAME="$AGENT_NAME" \
    PROWLR_CAPABILITIES="$CAPABILITIES" \
    PROWLR_HUB_DB="$DB_PATH" \
    "$PYTHON" -m prowlrbot.hub 2>/dev/null)

if echo "$TEST_RESULT" | grep -q "prowlr-hub"; then
    ok "MCP server responds correctly"
else
    fail "MCP server test failed"
    echo "  Output: $TEST_RESULT"
    exit 1
fi

# Test tool call
BOARD_RESULT=$(printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\n{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"check_mission_board","arguments":{}}}' | \
    PYTHONPATH="$PROJECT_ROOT/src" \
    PROWLR_AGENT_NAME="$AGENT_NAME" \
    PROWLR_CAPABILITIES="$CAPABILITIES" \
    PROWLR_HUB_DB="$DB_PATH" \
    "$PYTHON" -m prowlrbot.hub 2>/dev/null | tail -1)

if echo "$BOARD_RESULT" | grep -q "content"; then
    ok "Mission board accessible"
else
    warn "Mission board test returned unexpected result"
fi

# ── Summary ─────────────────────────────────────────────────
echo ""
echo -e "${CYAN}${BOLD}"
echo "  ╔═══════════════════════════════════════════╗"
echo "  ║         Setup Complete!                    ║"
echo "  ╚═══════════════════════════════════════════╝"
echo -e "${NC}"
echo -e "  ${BOLD}Agent:${NC}        $AGENT_NAME"
echo -e "  ${BOLD}Capabilities:${NC} $CAPABILITIES"
echo -e "  ${BOLD}Network:${NC}      $NETWORK_MODE"
if [ -n "$HUB_URL" ]; then
echo -e "  ${BOLD}Bridge URL:${NC}   $HUB_URL"
else
echo -e "  ${BOLD}Database:${NC}     $DB_PATH"
fi
echo -e "  ${BOLD}MCP Config:${NC}   $MCP_CONFIG_FILE"
echo ""
echo -e "  ${BOLD}Next steps:${NC}"
echo -e "  ${GREEN}1.${NC} Restart Claude Code in this terminal"
echo -e "  ${GREEN}2.${NC} The war room tools are now available automatically"
echo -e "  ${GREEN}3.${NC} Start with: ${CYAN}check_mission_board()${NC}"
echo ""
echo -e "  ${DIM}Run this script on each terminal to connect more agents.${NC}"
if [ "$NETWORK_MODE" = "local" ]; then
echo -e "  ${DIM}All agents share the same database — instant coordination.${NC}"
else
echo -e "  ${DIM}All agents connect through the bridge — cross-machine coordination.${NC}"
fi
echo ""
echo -e "  ${DIM}Troubleshooting: docs/guides/cross-network-setup.md${NC}"
echo ""
