---
name: board
description: Check the war room mission board — see all tasks, owners, and progress
---

# Mission Board

Check the current state of the war room mission board.

## Instructions

1. Call the `check_mission_board` MCP tool
2. Display the results in a clean table format
3. Highlight any tasks that are blocked or failed
4. Show which agents own which tasks
5. If there are unclaimed tasks, mention them as available

## Output Format

Present the board as:

```
## Mission Board

| Status | Task | Owner | Priority | Files |
|--------|------|-------|----------|-------|
| ...    | ...  | ...   | ...      | ...   |

**Available:** X unclaimed tasks
**In Progress:** Y tasks being worked on
**Completed:** Z tasks done
```

If no tasks exist, say "Mission board is empty. Use `/claim` to create and claim a task."
