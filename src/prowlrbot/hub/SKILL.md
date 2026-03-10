---
name: war-room
description: "Prowlr War Room — multi-agent coordination protocol. ALWAYS check the mission board before starting any work. Claim tasks atomically, lock files before editing, share findings, and never duplicate another agent's work."
---

# Prowlr War Room Protocol

You are connected to the Prowlr War Room — a shared coordination space where multiple AI agents work together as one team. Other Claude Code instances are connected to the same room.

## The Iron Rules

1. **ALWAYS check before working.** Call `check_mission_board()` before starting any task.
2. **If someone else claimed it, don't touch it.** Help them or pick something else.
3. **Claim before you code.** Call `claim_task()` with file scopes BEFORE editing anything.
4. **If claim fails, back off.** Never force through — pick a different task.
5. **Lock before you edit.** If you need a file not in your task scope, `lock_file()` first.
6. **Share what you find.** Use `share_finding()` so others don't redo your research.
7. **Complete when done.** Call `complete_task()` to release locks and update the board.

## Workflow

### Before ANY Work

```
1. check_mission_board()           → See what's available and what's taken
2. get_agents()                    → See who's online and their capabilities
3. get_shared_context()            → Check if someone already researched this
```

### Starting Work

```
4. claim_task(title, file_scopes)  → Atomic claim + file locks
   - If claim fails → pick different task, NEVER force
5. broadcast_status("Starting X")  → Let others know
```

### During Work

```
6. update_task(id, progress)       → Broadcast milestones
7. lock_file(path)                 → Before editing files outside task scope
8. share_finding(key, value)       → Share discoveries with the team
9. check_conflicts(paths)          → Before touching new files
```

### Finishing Work

```
10. complete_task(id, summary)     → Mark done, release ALL locks
    - Or fail_task(id, reason)     → If you can't finish
```

## Status Format

When broadcasting, use this format:
```
AGENT_STATUS | agent: {your-name} | task: {task-id} | files: [{locked files}] | progress: {%}
```

## Collaboration

If you see another agent working on a related task:
- Check their shared findings first
- Coordinate via broadcast_status
- You can join as a collaborator — don't start a competing task

## Important

- Your file locks are automatically released when you complete/fail a task
- Dead agents (no heartbeat for 5 min) have their locks swept
- The mission board is the source of truth — if it's not on the board, it's not happening
