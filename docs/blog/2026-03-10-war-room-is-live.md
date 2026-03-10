---
title: "The War Room Is Live — Multi-Agent Coordination Ships Today"
date: 2026-03-10
author: ProwlrBot Team
tags: [launch, update]
summary: "We shipped ProwlrHub — a shared mission board that lets multiple Claude Code agents coordinate in real-time without stepping on each other."
---

# The War Room Is Live

## The Moment It Clicked

Picture this: you have three Claude Code terminals open. One is building the API. One is writing tests. One is refactoring the database layer.

Terminal 2 edits `models.py`. Terminal 3 edits `models.py`. They both commit. Git conflict. Wasted work. Frustrated developer.

We built the war room to kill that problem forever.

## What ProwlrHub Does

ProwlrHub is an MCP server that gives every connected agent 13 coordination tools:

| What you can do | How |
|----------------|-----|
| See all tasks | `check_mission_board` |
| Claim work + lock files | `claim_task` |
| Post progress | `update_task` |
| Finish up | `complete_task` |
| Prevent conflicts | `check_conflicts` |
| Talk to the team | `broadcast_status` |
| Share discoveries | `share_finding` |

The magic is in **advisory file locking**. When Agent A claims a task and lists its file scope (`src/api/routes.py`, `src/api/models.py`), those files are locked. If Agent B tries to edit `models.py`, a hook fires and warns it off.

No merge conflicts. No wasted work. No chaos.

## How It Works Under the Hood

```
Agent A (Terminal 1)              ProwlrHub (SQLite WAL)
─────────────────────             ─────────────────────
claim_task("Build API",           → Creates task record
  files=["src/api/*"])            → Locks file patterns
                                  → Returns task ID
edit src/api/routes.py            → Hook checks lock → OK (yours)
share_finding("API needs auth")   → Stores for other agents
complete_task()                   → Releases all locks

Agent B (Terminal 2)
─────────────────────
claim_task("Write tests",         → Creates task record
  files=["tests/*"])              → Locks test files
edit tests/test_api.py            → Hook checks lock → OK (yours)
edit src/api/routes.py            → Hook checks lock → BLOCKED (Agent A)
get_shared_context()              → Sees "API needs auth"
```

SQLite with WAL mode handles concurrent access beautifully. No Redis. No Postgres. No infrastructure to manage.

## Cross-Machine? No Problem.

Agents don't have to be on the same machine. We built an HTTP bridge:

```bash
# On your Mac (the host)
PYTHONPATH=src python3 -m prowlrbot.hub.bridge
# → Listening on port 8099

# On your WSL machine
claude mcp add prowlr-hub -s local \
  -e PROWLR_HUB_URL="http://192.168.12.21:8099" \
  -e PROWLR_AGENT_NAME="wsl-agent" \
  -- python3 -m prowlrbot.hub
```

Different networks? We support Tailscale, Cloudflare Tunnel, ngrok, and SSH tunnels. See the [cross-network setup guide](../guides/cross-network-setup.md).

## The Plugin

ProwlrHub ships as a Claude Code plugin with the full stack:

- **5 slash commands** — `/board`, `/claim`, `/team`, `/broadcast`, `/warroom`
- **1 auto-activating skill** — War Room Protocol (7 Iron Rules for agent behavior)
- **2 hooks** — Pre-edit conflict check, session-start registration
- **1 agent** — War Room Coordinator for task planning
- **13 MCP tools** — The coordination primitives

Install once, restart Claude Code, and every terminal is connected.

## Real Numbers

From today's session running 6 agents across 2 machines:

- **7 tasks** on the mission board simultaneously
- **0 file conflicts** (the hooks caught everything)
- **12 shared findings** between agents
- **23 status broadcasts**

The war room works. Ship it.

## Set Up In 60 Seconds

```bash
# In your project directory
git clone https://github.com/prowlrbot/prowlrbot.git
cd prowlrbot
pip install -e .
```

Then tell Claude Code: *"Set up the war room using the INSTALL.md"*

Your agent handles the rest.

---

*War room documentation: [Hub Architecture](../../src/prowlrbot/hub/README.md) | [War Room Protocol](../../plugins/prowlr-hub/skills/war-room-protocol/SKILL.md)*
