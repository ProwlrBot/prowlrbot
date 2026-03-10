# ROAR Layer 1 — Identity

## Purpose

Provide a decentralized, verifiable identity for every participant in the ROAR ecosystem — agents, tools, humans, and IDEs. Identity is the foundation that all other layers depend on for authentication, authorization, and message routing.

## Data Models

### AgentIdentity

| Field          | Type       | Default          | Description                                 |
|----------------|------------|------------------|---------------------------------------------|
| `did`          | `str`      | auto-generated   | W3C DID in format `did:roar:<type>:<slug>`  |
| `display_name` | `str`      | `""`             | Human-readable name                         |
| `agent_type`   | `str`      | `"agent"`        | One of: `agent`, `tool`, `human`, `ide`     |
| `capabilities` | `list[str]`| `[]`             | Declared capability identifiers             |
| `version`      | `str`      | `"1.0"`          | Protocol version this agent supports        |

DID auto-generation: if `did` is empty on creation, it is set to `did:roar:<agent_type>:<slug>-<uuid8>` where `<slug>` is derived from `display_name` (lowercased, spaces replaced with hyphens, truncated to 20 chars) and `<uuid8>` is 8 hex characters from a v4 UUID.

### AgentCapability

| Field           | Type              | Description                              |
|-----------------|-------------------|------------------------------------------|
| `name`          | `str`             | Unique capability identifier             |
| `description`   | `str`             | Human-readable description               |
| `input_schema`  | `dict[str, Any]`  | JSON Schema for expected input           |
| `output_schema` | `dict[str, Any]`  | JSON Schema for expected output          |

### AgentCard

| Field                  | Type                    | Description                          |
|------------------------|-------------------------|--------------------------------------|
| `identity`             | `AgentIdentity`         | The agent's identity                 |
| `description`          | `str`                   | What this agent does                 |
| `skills`               | `list[str]`             | Named skills (e.g. `"pdf"`, `"cron"`)|
| `channels`             | `list[str]`             | Supported channels                   |
| `endpoints`            | `dict[str, str]`        | Transport-type to URL mapping        |
| `declared_capabilities`| `list[AgentCapability]` | Structured capability declarations   |
| `metadata`             | `dict[str, Any]`        | Arbitrary extension data             |

## Operations

- **Create identity**: Instantiate `AgentIdentity` with a display name; the DID is generated automatically.
- **Create card**: Wrap an identity in an `AgentCard` with description, skills, and endpoints.
- **Verify identity**: Resolve the DID to confirm the agent exists in a directory.

## Security Considerations

- DIDs must be unique within a directory. Collision detection is handled at registration time.
- The `agent_type` field is informational; authorization decisions should use capabilities, not type.
- Agent cards should not contain secrets. Signing keys are stored separately.

## Example

```python
from prowlrbot.protocols.sdk import AgentIdentity, AgentCard, AgentCapability

identity = AgentIdentity(
    display_name="code-reviewer",
    agent_type="agent",
    capabilities=["code-review", "pr-summary"],
)
# identity.did => "did:roar:agent:code-reviewer-a1b2c3d4"

cap = AgentCapability(
    name="code-review",
    description="Review code for bugs and style",
    input_schema={"type": "object", "properties": {"files": {"type": "array"}}},
)

card = AgentCard(
    identity=identity,
    description="Reviews pull requests",
    skills=["code-review"],
    endpoints={"http": "http://localhost:8089"},
    declared_capabilities=[cap],
)
```
