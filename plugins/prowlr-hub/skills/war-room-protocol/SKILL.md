---
name: war-room-protocol
description: Use when connected to ProwlrHub war room. Enforces coordination rules for multi-agent collaboration — check board before working, claim before editing, share findings, complete when done.
---

# War Room Coordination Protocol

You are connected to a ProwlrHub war room. Other Claude Code agents are working on the same codebase simultaneously. Follow these rules to avoid conflicts and coordinate effectively.

## 7 Iron Rules

1. **ALWAYS check before working.** Call `check_mission_board` before starting any task.
2. **If someone claimed it, don't touch it.** Check the board. If another agent owns a task or has locked the files, help them or pick something else.
3. **Claim before you code.** Call `claim_task` with file scopes BEFORE editing any file. This atomically locks the files.
4. **If claim fails, back off.** A failed claim means another agent has those files locked. Never force through a failed claim. Pick different files or wait.
5. **Lock before you edit.** If you need to edit files outside your task's file scopes, call `lock_file` first.
6. **Share what you find.** Use `share_finding` when you discover something useful (API endpoints, architecture decisions, bugs found, etc.). Other agents check findings before starting research.
7. **Complete when done.** Call `complete_task` when finished. This releases all your file locks so others can use those files.

## Workflow

Every task follows this flow:

```
check_mission_board()         → See what's available
get_agents()                  → See who's working on what
check_conflicts(my_files)     → Verify files are free
claim_task(title, files)      → Lock files, claim work
... do the work ...
update_task(id, "progress")   → Keep team informed
share_finding(key, value)     → Share discoveries
complete_task(id, "summary")  → Release locks, mark done
```

## Before Editing Any File

Before using the Edit, Write, or MultiEdit tool on any file:

1. Check if you have claimed a task that includes that file in its `file_scopes`
2. If not, call `check_conflicts` on that file path
3. If the file is locked by another agent, DO NOT edit it
4. If the file is free, either add it to your task's scope or call `lock_file`

## Sharing Findings

When you discover something that other agents would benefit from knowing:

```
share_finding("api-endpoints", "Found 12 REST endpoints in src/app/routers/")
share_finding("db-schema", "Users table has 15 columns, see src/models/user.py")
share_finding("test-failures", "3 tests failing in tests/test_auth.py — auth middleware issue")
```

Before starting research on any topic, check if another agent already shared findings:

```
get_shared_context("api-endpoints")  → Check before exploring API
get_shared_context("")               → See ALL shared findings
```

## Broadcasting

Use `broadcast_status` to communicate with all agents:

- **Blockers:** "Blocked on database migration — need help with Alembic"
- **Milestones:** "API endpoints are done, ready for frontend integration"
- **Warnings:** "Don't touch src/config.py — I'm refactoring it"
- **Coordination:** "Starting security audit of auth system"

## When Tasks are Done

Always call `complete_task` with a summary of what was accomplished:

```
complete_task(task_id, "Implemented 5 REST endpoints for user CRUD, added input validation and tests")
```

This:
- Releases all file locks from your task
- Updates the mission board for other agents
- Logs the completion in the event history

## When Tasks Fail

If you can't complete a task, call `fail_task` with a reason:

```
fail_task(task_id, "Dependency conflict — need pydantic v2 but project uses v1")
```

This releases locks and returns the task to the board so others can attempt it.
