---
title: "Setting Up Your First Agent Swarm"
date: 2026-03-10
author: ProwlrBot Team
tags: [guide]
summary: "A no-nonsense walkthrough for getting multiple AI agents working together on the same project without stepping on each other."
---

# Setting Up Your First Agent Swarm

## What You'll Have When You're Done

Three Claude Code terminals, each with a named agent, all sharing a mission board. Agent A claims the backend. Agent B claims the frontend. Agent C claims the tests. Nobody touches each other's files.

Takes about 5 minutes.

## Prerequisites

- Python 3.10+
- Claude Code installed
- A project you want to work on

## Step 1: Install ProwlrBot

```bash
git clone https://github.com/prowlrbot/prowlrbot.git
cd prowlrbot
pip install -e .
```

## Step 2: Register Your First Agent

Open Terminal 1. This will be your backend agent.

```bash
claude mcp add prowlr-hub -s local \
  -e PYTHONPATH="$(pwd)/src" \
  -e PROWLR_AGENT_NAME="backend" \
  -e PROWLR_CAPABILITIES="python,api,database" \
  -- python3 -m prowlrbot.hub
```

Restart Claude Code completely (quit and reopen, not just a new conversation).

## Step 3: Register Agent Two

Open Terminal 2. This is your frontend agent.

```bash
claude mcp add prowlr-hub -s local \
  -e PYTHONPATH="/path/to/prowlrbot/src" \
  -e PROWLR_AGENT_NAME="frontend" \
  -e PROWLR_CAPABILITIES="react,typescript,css" \
  -- python3 -m prowlrbot.hub
```

Restart Claude Code.

## Step 4: Register Agent Three

Open Terminal 3. Your test agent.

```bash
claude mcp add prowlr-hub -s local \
  -e PYTHONPATH="/path/to/prowlrbot/src" \
  -e PROWLR_AGENT_NAME="tester" \
  -e PROWLR_CAPABILITIES="pytest,testing,qa" \
  -- python3 -m prowlrbot.hub
```

Restart Claude Code.

## Step 5: Verify

In any terminal, type `/board`. You should see:

```
╔══════════════════════════════════════════╗
║           MISSION BOARD                 ║
╠══════════════════════════════════════════╣
║  No active tasks.                       ║
║  Use /claim to create one.              ║
╚══════════════════════════════════════════╝
```

Type `/team` to see all connected agents:

```
Connected Agents:
  backend   — python, api, database
  frontend  — react, typescript, css
  tester    — pytest, testing, qa
```

## Step 6: Start Working

In Terminal 1 (backend):
```
/claim Build user authentication API
Files: src/api/auth.py, src/api/models.py, src/api/middleware.py
```

In Terminal 2 (frontend):
```
/claim Build login page
Files: src/components/Login.tsx, src/components/AuthProvider.tsx
```

In Terminal 3 (tester):
```
/claim Write auth tests
Files: tests/test_auth.py, tests/test_login.py
```

Each agent now owns its files. If the frontend agent accidentally tries to edit `src/api/auth.py`, the war room will warn it.

## The 7 Iron Rules

Once connected, your agents automatically follow the War Room Protocol:

1. **Check the board** before starting any work
2. **Claim before editing** — no unclaimed file modifications
3. **Lock your files** — declare what you'll touch
4. **Check conflicts** before every edit
5. **Share findings** — if you discover something useful, post it
6. **Broadcast blockers** — if you're stuck, tell the team
7. **Complete tasks** — mark done when finished, release locks

## Cross-Machine Setup

If your agents are on different machines (Mac + WSL, two laptops, etc.), you need the HTTP bridge.

On the host machine:
```bash
cd prowlrbot
PYTHONPATH=src python3 -m prowlrbot.hub.bridge
# Listening on :8099
```

On remote machines, add `-e PROWLR_HUB_URL="http://<host-ip>:8099"` to the `claude mcp add` command.

Different networks? Use Tailscale, Cloudflare Tunnel, or ngrok. See the [cross-network guide](../guides/cross-network-setup.md).

## Tips

- **Name agents by role**, not by terminal number. `backend`, `frontend`, `docs` — not `agent-1`, `agent-2`.
- **Use specific file scopes**. `src/api/auth.py` is better than `src/`.
- **Share findings often**. When Agent A discovers the database schema is wrong, Agent B and C need to know immediately.
- **Complete tasks promptly**. Hanging locks block other agents.

## What's Next

Once you're comfortable with the basics, explore:
- The [War Room Coordinator agent](../../plugins/prowlr-hub/agents/war-room-coordinator.md) for automated task planning
- [Remote execution via the Swarm](../../README.swarm.md) for cross-machine capabilities
- The [ROAR Protocol](https://github.com/ProwlrBot/roar-protocol) for standardized agent communication

---

*Questions? [Open an issue](https://github.com/prowlrbot/prowlrbot/issues).*
