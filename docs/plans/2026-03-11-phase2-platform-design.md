# ProwlrBot Phase 2: Protocols, Marketplace, and Platform Features

**Date**: 2026-03-11
**Status**: Approved
**Goal**: Ship ACP + A2A protocol support, community marketplace, monitoring integration, tiered agent memory, swarm deployment, and full console UI — then formalize ROAR as the unified protocol spec.

---

## 1. Protocol Stack — ACP + A2A first, then ROAR

### ACP Server (`src/prowlrbot/protocols/acp_server.py`)
- JSON-RPC 2.0 over stdio, exposing ProwlrBot as an IDE-usable agent
- Commands: `initialize`, `session/new`, `session/prompt`, `session/cancel`
- CLI: `prowlr acp` starts the ACP server
- Any IDE with ACP support (VS Code, Zed, JetBrains) can use ProwlrBot as their coding agent

### A2A Server + Client (`src/prowlrbot/protocols/a2a_server.py`, `a2a_client.py`)
- HTTP endpoints for Agent Cards (capability discovery), task delegation, context sharing
- Agent Card at `/.well-known/agent.json` — standard A2A discovery
- Task lifecycle: create, assign, execute, complete/fail
- Client discovers external A2A agents and can delegate subtasks to them

### ROAR Protocol Spec (`docs/roar-protocol/`)
- 5-layer spec: Identity, Discovery, Connect, Exchange, Stream
- Python SDK wrapping MCP + ACP + A2A into unified ROAR messages
- Adapters: `mcp-adapter.py`, `a2a-adapter.py`, `acp-adapter.py`
- Backward-compatible — speaks all three protocols via adapters

---

## 2. Community Marketplace (separate repo: `ProwlrBot/marketplace`)

### Registry
- GitHub-backed registry — JSON index with metadata for all listings
- 12 categories: Skills, Agent Templates, System Prompts, Prompt Specs, MCP Configs, Channel Plugins, Workflows, Knowledge Bases, Benchmark Suites, AgentVerse Assets, Dashboard Themes, Team Configs
- Each listing: name, version, description, author, category, downloads, rating, dependencies
- mcpcentral content migrates into this registry

### CLI Commands (in prowlrbot core)
- `prowlr market search <query>` — search registry with FTS
- `prowlr market install <name>` — download and install to `~/.prowlrbot/marketplace/`
- `prowlr market publish <path>` — package and submit to registry
- `prowlr market list` — show installed marketplace items
- `prowlr market update` — update registry index + installed items

### Package Format
- Zip archive with `manifest.json` (name, version, category, description, dependencies)
- Sandboxed installation — skills go to `active_skills/`, MCP configs merge, agents register
- Integrity: SHA256 checksums in registry, verified on install

---

## 3. Monitoring Integration — Surface existing engine in UI + channels

### Console Page (`console/src/pages/Monitoring/`)
- Status grid showing all configured monitors (green/yellow/red)
- History chart per monitor (change frequency over time)
- Diff viewer — side-by-side content changes with highlighting
- Configure new monitors from UI (URL, interval, notification channels)

### Channel Integration
- Alert routing: monitor alerts -> configured channels (Discord, Telegram, console)
- Severity levels: info, warning, critical — each routes to different channels
- Quiet hours: suppress non-critical alerts during configured windows

### Cron Integration
- Wire monitors into APScheduler for scheduled checks
- Currently monitors are CLI-triggered; this makes them automatic

---

## 4. Agent Memory — Tiered Persistence

### Three Tiers

| Tier | Storage | Lifetime | Size |
|------|---------|----------|------|
| Short-term | In-memory (`ProwlrBotInMemoryMemory`) | Session only | Token budget with compaction |
| Medium-term | SQLite + FTS5 (`LearningDB`) | Cross-session | Per-agent, searchable |
| Long-term | New `ArchiveDB` — summarized knowledge | Permanent | Auto-promoted from medium-term |

### New Components (`src/prowlrbot/agents/memory/`)
- `MemoryTierManager` — orchestrates promotion/demotion between tiers
- Auto-promotion: learnings used 3+ times or marked important -> long-term archive
- Auto-decay: medium-term entries unused for 30 days -> archived or pruned
- `archive_db.py` — SQLite with FTS5, stores compressed summaries
- Per-agent memory isolation with optional sharing

### Memory Injection
- Before each agent response, query medium + long-term memory for relevant context
- Inject top-K results into system prompt
- Extends existing `MemoryManager` compaction with persistent retrieval

---

## 5. Swarm Mode — Docker Compose + Bridge Polish

### Deliverables
- `docker/docker-compose.yml` — bridge + N worker agents, configurable via `.env`
- `docker/Dockerfile.worker` — lightweight agent container
- `docker/Dockerfile.bridge` — bridge server with SQLite volume mount
- Workers auto-register on startup, heartbeat every 30s

### Console Page (`console/src/pages/Swarm/`)
- Worker grid: name, host, status, current task, capabilities, last heartbeat
- Health indicators based on heartbeat freshness
- Network topology view

### Bridge Improvements
- Worker auto-cleanup via `sweep_dead_agents` (already built)
- Reconnection with exponential backoff

---

## 6. Console Enhancements — Agent Builder + New Pages + Polish

### New Pages

| Page | Key Components |
|------|---------------|
| Monitoring | Status grid, history charts, diff viewer, config form |
| Marketplace | Browse/search registry, install/uninstall, ratings, category filters |
| Swarm | Worker grid, health indicators, topology view |
| Memory | Per-agent memory browser, search across tiers |

### Agent Builder (enhance existing Agent page)
- Visual form: name, personality, model, tools, skills, channels, autonomy level
- Soul editor: edit SOUL.md/PROFILE.md with live preview
- Team builder: drag agents into teams, set coordination mode
- Avatar picker (predefined set)

### Polish
- Consistent styling across all pages (Ant Design tokens)
- Loading states, error boundaries, empty states
- Reuse WebSocket connection status indicator from War Room

---

## Repo Structure

| Repo | Purpose |
|------|---------|
| `ProwlrBot/prowlrbot` | Core platform — protocols, memory, monitoring, swarm, console |
| `ProwlrBot/marketplace` | Registry + packages (merges mcpcentral) |
| `docs/roar-protocol/` | ROAR spec (in prowlrbot repo for now, own repo later) |

---

## Implementation Order

1. Protocol Stack (ACP + A2A)
2. ROAR spec + SDK + adapters
3. Marketplace (registry repo + CLI client + console page)
4. Monitoring integration (console page + channel routing + cron)
5. Agent Memory (tiered persistence)
6. Swarm Mode (docker compose + console page)
7. Console Enhancements (agent builder + polish)
