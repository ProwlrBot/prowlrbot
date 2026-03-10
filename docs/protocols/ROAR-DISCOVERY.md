# ROAR Layer 2 — Discovery

## Purpose

Enable agents to find each other by identity or capability without relying on a centralized registry. Discovery builds on Layer 1 Identity and provides the lookup mechanism that Layer 3 Connect uses to establish transport connections.

## Data Models

### DiscoveryEntry

| Field           | Type        | Default        | Description                                |
|-----------------|-------------|----------------|--------------------------------------------|
| `agent_card`    | `AgentCard` | required       | The registered agent's card                |
| `registered_at` | `float`     | `time.time()`  | Unix timestamp of registration             |
| `last_seen`     | `float`     | `time.time()`  | Unix timestamp of last heartbeat or update |
| `hub_url`       | `str`       | `""`           | URL of the hub that registered this entry  |

### AgentDirectory

In-memory directory that stores `DiscoveryEntry` records keyed by DID. Serves as both a local registry and a building block for federated discovery.

## Operations

### Register

```python
directory = AgentDirectory()
entry = directory.register(card)
```

Adds an agent card to the directory. If an agent with the same DID is already registered, its entry is replaced. Returns the created `DiscoveryEntry`.

### Unregister

```python
directory.unregister("did:roar:agent:my-agent-abc12345")
```

Removes an agent from the directory. Returns `True` if the agent was found and removed, `False` otherwise.

### Lookup

```python
entry = directory.lookup("did:roar:agent:my-agent-abc12345")
```

Returns the `DiscoveryEntry` for a specific DID, or `None` if not found.

### Search

```python
entries = directory.search("code-review")
```

Returns all entries whose agent identity declares the given capability.

### List All

```python
all_entries = directory.list_all()
```

Returns every registered entry.

## Federation

Multiple directories can federate by exchanging `DiscoveryEntry` records. The `hub_url` field tracks which hub originally registered an agent. A federated search queries all known hubs and merges results, preferring entries with the most recent `last_seen` timestamp.

## Security Considerations

- Registration should verify the caller owns the DID being registered (e.g. via signed registration request).
- Directories should implement rate limiting to prevent registration flooding.
- Stale entries (where `last_seen` exceeds a configurable TTL) should be pruned periodically.
- Federated queries should validate the authenticity of entries received from remote hubs.

## Example

```python
from prowlrbot.protocols.sdk import AgentIdentity, AgentCard, AgentDirectory

directory = AgentDirectory()

card = AgentCard(
    identity=AgentIdentity(
        display_name="summarizer",
        capabilities=["text-summary", "translation"],
    ),
    description="Summarizes and translates text",
    endpoints={"http": "http://localhost:9001"},
)

directory.register(card)

# Find agents that can summarize
results = directory.search("text-summary")
print(results[0].agent_card.identity.did)
```
