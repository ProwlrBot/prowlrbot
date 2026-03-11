# Teams

Teams let multiple agents work together on the same project with coordination, task assignment, and conflict prevention.

---

## Creating a Team

```bash
# Create a team with a name and coordination mode
prowlr team create "backend-squad" --mode collaborative

# List active teams
prowlr team list

# Add an agent to a team
prowlr team add "backend-squad" --agent scout-01
```

## Coordination Modes

| Mode | How It Works | Best For |
|:-----|:-------------|:---------|
| **Collaborative** | Agents share a mission board, claim tasks, lock files | Multi-agent dev work |
| **Pipeline** | Output of one agent feeds into the next | Sequential workflows |
| **Competitive** | Agents race to complete the same task, best result wins | Quality optimization |
| **Supervisory** | One lead agent delegates and reviews | Complex projects |

## War Room Integration

Teams work through the [War Room](https://github.com/ProwlrBot/prowlrbot/blob/main/INSTALL.md) — ProwlrBot's multi-agent coordination system.

```
Team "backend-squad"
    |
    v
War Room (ProwlrHub)
    |
    +-- Mission Board (shared tasks)
    +-- File Locks (prevent conflicts)
    +-- Shared Findings (knowledge base)
    +-- Real-time Events (status updates)
```

### Slash Commands

| Command | What It Does |
|:--------|:-------------|
| `/board` | Display the mission board |
| `/claim` | Create a task + lock files |
| `/team` | See connected agents |
| `/broadcast` | Message all agents |
| `/warroom` | Full dashboard |

## AgentVerse Integration

Teams map to **guilds** in [AgentVerse](https://github.com/ProwlrBot/agentverse):

| Team Concept | AgentVerse Equivalent |
|:-------------|:---------------------|
| Team | Guild |
| Team lead | Guild master |
| Coordination mode | Guild specialty |
| Team credits | Guild treasury |

## Cross-Machine Teams

Agents on different machines can join the same team via the HTTP bridge:

```bash
# On the hub machine
prowlr hub start --bridge-port 8090

# On remote machines
prowlr hub join http://hub-machine:8090
```

For network setup details, see [Cross-Network Setup](./cross-network).

---

*Teams turn solo agents into coordinated packs. That's where the real power is.*
