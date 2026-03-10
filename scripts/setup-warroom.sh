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
    echo -e "${GREEN}${BOLD}[$1/6]${NC} ${BOLD}$2${NC}"
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

# Step 5: Configure MCP
step "5" "Configuring Claude Code MCP integration"

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

config['mcpServers']['prowlr-hub'] = {
    'command': '$PYTHON',
    'args': ['-m', 'prowlrbot.hub'],
    'cwd': '$PROJECT_ROOT',
    'env': {
        'PYTHONPATH': '$PROJECT_ROOT/src',
        'PROWLR_AGENT_NAME': '$AGENT_NAME',
        'PROWLR_CAPABILITIES': '$CAPABILITIES'
    }
}

with open('$MCP_CONFIG_FILE', 'w') as f:
    json.dump(config, f, indent=2)
    f.write('\n')

print('  ✓ Created .mcp.json with prowlr-hub entry')
"
fi

# Step 6: Verify
step "6" "Verifying installation"

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
echo -e "  ${BOLD}Database:${NC}     $DB_PATH"
echo -e "  ${BOLD}MCP Config:${NC}   $MCP_CONFIG_FILE"
echo ""
echo -e "  ${BOLD}Next steps:${NC}"
echo -e "  ${GREEN}1.${NC} Restart Claude Code in this terminal"
echo -e "  ${GREEN}2.${NC} The war room tools are now available automatically"
echo -e "  ${GREEN}3.${NC} Start with: ${CYAN}check_mission_board()${NC}"
echo ""
echo -e "  ${DIM}Run this script on each terminal to connect more agents.${NC}"
echo -e "  ${DIM}All agents share the same database — instant coordination.${NC}"
echo ""
