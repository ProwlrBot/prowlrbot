---
name: warroom
description: Full war room status — mission board, team, findings, and recent events
---

# War Room Overview

Show the complete war room status in one view.

## Instructions

Call these MCP tools in parallel and combine the results:

1. `check_mission_board` — all tasks
2. `get_agents` — all connected agents
3. `get_shared_context` — all shared findings
4. `get_events` with limit=10 — recent activity

## Output Format

```
## War Room Status

### Mission Board
| Status | Task | Owner | Priority |
|--------|------|-------|----------|
| ...    | ...  | ...   | ...      |

### Team (X agents connected)
| Agent | Status | Current Task |
|-------|--------|-------------|
| ...   | ...    | ...         |

### Shared Findings
- key: value (by agent)
- ...

### Recent Activity
- [12:34] architect claimed "API endpoints"
- [12:30] security shared finding "vuln-count"
- ...
```

This is the "dashboard view" — everything at a glance.
