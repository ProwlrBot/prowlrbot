# ProwlrHub Installation Guide

Connect multiple Claude Code terminals into a coordinated war room.

## One-Line Setup

```bash
git clone https://github.com/mcpcentral/prowlrbot.git
cd prowlrbot
./scripts/setup-warroom.sh
```

The wizard will:
1. Detect your Python installation (3.10+ required)
2. Install dependencies
3. Initialize the shared database at `~/.prowlrbot/warroom.db`
4. Ask you to name this agent and set its capabilities
5. Configure `.mcp.json` for Claude Code
6. Verify everything works

Then restart Claude Code. Done.

## Manual Setup (if you prefer)

### Prerequisites

- Python 3.10+
- Claude Code CLI
- Git

### Step 1: Clone and install

```bash
git clone https://github.com/mcpcentral/prowlrbot.git
cd prowlrbot
pip install -e ".[dev]"
```

### Step 2: Add to `.mcp.json`

In your project's `.mcp.json` (create it if missing):

```json
{
  "mcpServers": {
    "prowlr-hub": {
      "command": "python3",
      "args": ["-m", "prowlrbot.hub"],
      "cwd": "/path/to/prowlrbot",
      "env": {
        "PYTHONPATH": "/path/to/prowlrbot/src",
        "PROWLR_AGENT_NAME": "my-agent-name",
        "PROWLR_CAPABILITIES": "python,testing"
      }
    }
  }
}
```

Replace `/path/to/prowlrbot` with your actual clone path.

### Step 3: Restart Claude Code

The MCP server starts automatically when Claude Code launches.

### Step 4: Verify

In Claude Code, the war room tools should now be available. Try:
```
check_mission_board()
```

## Multi-Terminal Setup

Run the setup wizard on **each terminal** you want to connect:

```bash
# Terminal 1
./scripts/setup-warroom.sh
# → Name: backend-architect
# → Capabilities: python,api,database

# Terminal 2
./scripts/setup-warroom.sh
# → Name: frontend-lead
# → Capabilities: typescript,react,css

# Terminal 3
./scripts/setup-warroom.sh
# → Name: security-scout
# → Capabilities: security,testing,recon

# Terminal 4
./scripts/setup-warroom.sh
# → Name: docs-writer
# → Capabilities: docs,markdown,git
```

All terminals share the same SQLite database. Changes are instant.

## Cross-Machine Setup (Mac + WSL)

For connecting agents across machines:

### On the host machine (Mac):
```bash
./scripts/setup-warroom.sh
# Database lives at ~/.prowlrbot/warroom.db
```

### On the remote machine (WSL/Linux):

Option A — **Shared filesystem** (if WSL can see Mac's home dir):
```bash
./scripts/setup-warroom.sh
# Set PROWLR_HUB_DB to point to the shared database path
export PROWLR_HUB_DB="/mnt/mac/Users/you/.prowlrbot/warroom.db"
```

Option B — **Network sync** (coming in v2):
The ROAR protocol's federation layer will enable WebSocket-based database sync between machines. For now, use a shared filesystem or copy the database.

## Troubleshooting

### "No module named prowlrbot"
```bash
# Make sure PYTHONPATH includes the src directory
export PYTHONPATH=/path/to/prowlrbot/src
python3 -m prowlrbot.hub  # should start without errors
```

### "Database is locked"
SQLite WAL mode handles most concurrency. If you see lock errors:
```bash
# Check for stale processes
ps aux | grep prowlrbot.hub
# Kill any zombies
kill <pid>
```

### "Tools not showing in Claude Code"
1. Make sure `.mcp.json` is in your project root (where you run Claude Code)
2. Restart Claude Code completely (not just the conversation)
3. Check the MCP server starts: `echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | PYTHONPATH=src python3 -m prowlrbot.hub`

### Agent not appearing on mission board
The agent auto-registers on first tool call. Just call `check_mission_board()` and you'll appear.

## What Happens Next

After setup, your Claude Code terminals can:

| Command | What it does |
|---------|-------------|
| `check_mission_board()` | See all tasks — who owns what, what's available |
| `claim_task(title, file_scopes)` | Grab a task and lock its files |
| `get_agents()` | See who's connected |
| `share_finding(key, value)` | Share discoveries with the team |
| `get_shared_context()` | Read what others found |
| `broadcast_status(msg)` | Announce what you're doing |
| `complete_task(id, summary)` | Finish up and release locks |

The full tool reference is in `src/prowlrbot/hub/README.md`.
