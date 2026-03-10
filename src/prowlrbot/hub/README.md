# ProwlrHub — War Room Multi-Agent Coordination

**Connect multiple Claude Code terminals into one coordinated team.**

ProwlrHub is an MCP (Model Context Protocol) server that gives every Claude Code instance in your project shared awareness: who's working on what, which files are locked, what's been discovered, and what still needs doing.

## Why?

When you run 4 Claude Code terminals on the same codebase, they can't see each other. They'll edit the same files, duplicate research, and step on each other's work. ProwlrHub fixes this with a shared SQLite database that all instances read/write through atomic transactions.

## Quick Start

### 1. It's already configured

If you cloned this repo, `.mcp.json` already includes ProwlrHub:

```json
{
  "mcpServers": {
    "prowlr-hub": {
      "command": "python3",
      "args": ["-m", "prowlrbot.hub"],
      "env": {
        "PYTHONPATH": "src",
        "PROWLR_AGENT_NAME": "",
        "PROWLR_CAPABILITIES": ""
      }
    }
  }
}
```

### 2. Restart Claude Code

Each terminal auto-spawns its own MCP server process. All share `~/.prowlrbot/warroom.db`.

### 3. Start coordinating

In any Claude Code terminal, the war room tools are now available:

```
check_mission_board     → See all tasks and who owns them
claim_task              → Atomically claim a task (locks files)
update_task             → Report progress
complete_task           → Mark done, release locks
fail_task               → Can't finish, release locks
lock_file / unlock_file → Advisory file locking
check_conflicts         → Are these files safe to edit?
get_agents              → Who's connected right now?
broadcast_status        → Tell everyone what you're doing
share_finding           → Share research/discoveries
get_shared_context      → Read what others discovered
get_events              → See recent war room activity
```

## How It Works

```
Terminal 1 (Claude Code)          Terminal 2 (Claude Code)
         │                                  │
    MCP Server 1                       MCP Server 2
    (prowlr.hub)                       (prowlr.hub)
         │                                  │
         └──────── SQLite WAL ──────────────┘
                ~/.prowlrbot/warroom.db
```

Each terminal runs its own MCP server process. SQLite's WAL (Write-Ahead Logging) mode allows concurrent reads and serialized writes. Atomic transactions prevent race conditions when two agents try to claim the same task or lock the same file.

## Architecture

### Three Layers

```
┌──────────────────────────────────┐
│   MCP Server (mcp_server.py)     │  ← JSON-RPC 2.0 over stdio
│   13 tools, auto-registration    │
├──────────────────────────────────┤
│   War Room Engine (engine.py)    │  ← All business logic
│   Rooms, Agents, Tasks, Locks    │
├──────────────────────────────────┤
│   SQLite Database (db.py)        │  ← Schema, WAL mode, indexes
│   7 tables, 5 indexes            │
└──────────────────────────────────┘
```

### Database Schema

| Table | Purpose |
|-------|---------|
| `rooms` | War room instances (usually just "default") |
| `agents` | Connected Claude Code instances with capabilities |
| `nodes` | Physical machines (for future cross-machine federation) |
| `tasks` | Mission board — all work items with status/priority/owner |
| `file_locks` | Advisory locks preventing edit conflicts |
| `events` | Audit log of everything that happens |
| `shared_context` | Key-value store for sharing discoveries |

### Atomic Task Claiming

This is the critical operation. When an agent claims a task:

```sql
BEGIN TRANSACTION;
  -- 1. Check task is still pending
  SELECT * FROM tasks WHERE task_id=? AND status='pending';
  -- 2. Check all file scopes are unlocked
  SELECT * FROM file_locks WHERE file_path IN (...) AND room_id=?;
  -- 3. If both pass: claim task + lock files + update agent status
  UPDATE tasks SET status='claimed', owner_agent_id=? WHERE task_id=?;
  INSERT INTO file_locks (...) VALUES (...);  -- one per file scope
  UPDATE agents SET status='working', current_task_id=? WHERE agent_id=?;
COMMIT;
```

If ANY step fails, the entire transaction rolls back. No partial claims, no orphan locks.

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PROWLR_AGENT_NAME` | `claude-{hostname}-{pid}` | Human-readable name for this terminal |
| `PROWLR_CAPABILITIES` | `general` | Comma-separated capabilities (e.g., `python,testing,frontend`) |
| `PROWLR_HUB_DB` | `~/.prowlrbot/warroom.db` | Custom database path |

### Naming Your Agents

Give each terminal a role by setting `PROWLR_AGENT_NAME` in the MCP config:

```json
{
  "prowlr-hub": {
    "env": {
      "PROWLR_AGENT_NAME": "backend-architect",
      "PROWLR_CAPABILITIES": "python,api,database"
    }
  }
}
```

## The War Room Protocol

Every agent follows these rules (enforced by the SKILL.md):

1. **ALWAYS check before working.** Call `check_mission_board()` first.
2. **If someone claimed it, don't touch it.** Help them or pick something else.
3. **Claim before you code.** Call `claim_task()` with file scopes BEFORE editing.
4. **If claim fails, back off.** Never force through.
5. **Lock before you edit.** Use `lock_file()` for files outside your task scope.
6. **Share what you find.** Use `share_finding()` so others don't redo research.
7. **Complete when done.** Call `complete_task()` to release locks.

## Safety Features

- **Dead agent sweep**: Agents that haven't heartbeated in 5 minutes get disconnected automatically, releasing all their locks
- **Disconnect cleanup**: When an agent disconnects, all its locks are released and in-progress tasks return to pending
- **Branch-aware locking**: File locks respect git branches — agents on different branches don't conflict
- **Event audit log**: Every action is logged with timestamps for debugging coordination issues

## Testing

```bash
# Run hub tests
PYTHONPATH=src python3 -m pytest tests/hub/ -v

# 32 tests covering:
# - Room management (4 tests)
# - Agent lifecycle (5 tests)
# - Task management (11 tests)
# - File locking (5 tests)
# - Shared context (3 tests)
# - Events (3 tests)
# - Dead agent sweep (1 test)
```

## For Developers

### Adding New Tools

1. Add tool definition to `TOOLS` dict in `mcp_server.py`
2. Add handler in `handle_tool_call()`
3. Add engine method in `engine.py`
4. Add tests in `tests/hub/test_engine.py`

### Database Migrations

The schema uses `CREATE TABLE IF NOT EXISTS` — safe to add new tables/indexes. For column changes, add a migration function in `db.py` that runs after `init_db()`.

### Future: Cross-Machine Federation

The `nodes` table already tracks hostname and platform. Future versions will support:
- WebSocket bridge between machines (Mac <-> WSL)
- HMAC-signed messages for cross-network trust
- ROAR protocol integration for agent identity (DID-based)
