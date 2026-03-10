---
name: team
description: See all connected agents in the war room — names, capabilities, and current tasks
---

# Team Status

Show all connected agents in the war room.

## Instructions

1. Call the `get_agents` MCP tool
2. Display each agent with their status, capabilities, and current task
3. Also call `get_shared_context` to show recent findings

## Output Format

```
## War Room Team

| Agent | Status | Capabilities | Current Task |
|-------|--------|-------------|-------------|
| architect | working | python, api | Implement REST endpoints |
| frontend | idle | react, css | — |
| security | working | security, audit | Security scan |

**Shared Findings:**
- `api-endpoints`: Found 12 REST endpoints (by architect)
- `vuln-report`: 3 issues found (by security)
```

If no other agents are connected, say "You're the only one here. Run the setup wizard on other terminals to connect more agents."
