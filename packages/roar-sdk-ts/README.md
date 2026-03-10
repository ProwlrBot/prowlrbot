# ROAR Protocol TypeScript SDK

Unified agent communication across MCP, A2A, and native ROAR transports.

## Quick Start

```bash
npm install @roar-protocol/sdk
```

```typescript
import {
  createIdentity,
  ROARClient,
  MessageIntent,
} from "@roar-protocol/sdk";

// Create an agent identity
const identity = createIdentity("my-agent", [
  { name: "summarize", version: "1.0", description: "Summarize text" },
]);

// Create a client with message signing
const client = new ROARClient(identity, { secretKey: "shared-secret" });

// Register yourself in the local directory
client.register("http://localhost:8088/roar");

// Send a message to another agent
const response = await client.send("roar_target_agent_id", MessageIntent.QUERY, {
  text: "Summarize this document",
});
```

## API Reference

### Types

- **`AgentCapability`** — Name, version, and description of a capability.
- **`AgentIdentity`** — Unique agent ID, display name, optional public key, capabilities, and creation timestamp.
- **`AgentCard`** — Publishable card containing identity, endpoint, and supported transports.
- **`TransportType`** — Enum: `STDIO`, `HTTP`, `WEBSOCKET`, `GRPC`.
- **`ConnectionConfig`** — Transport type, endpoint, optional headers and auth token.
- **`MessageIntent`** — Enum: `QUERY`, `RESPONSE`, `TOOL_CALL`, `TOOL_RESULT`, `NEGOTIATE`, `HEARTBEAT`, `ERROR`, `STREAM_START`, `STREAM_DATA`, `STREAM_END`.
- **`ROARMessage`** — The core message envelope (id, from/to agent, intent, content, timestamp, optional signature and metadata).
- **`StreamEventType`** — Enum: `STARTED`, `DATA`, `PROGRESS`, `COMPLETED`, `ERROR`, `CANCELLED`.
- **`StreamEvent`** — Event within a streaming exchange (type, stream ID, data, sequence number, timestamp).

### Identity

- **`createIdentity(displayName, capabilities?)`** — Create a new `AgentIdentity` with an auto-generated ID.
- **`generateAgentId()`** — Generate a `roar_` prefixed hex identifier.

### Messages

- **`createMessage(from, to, intent, content)`** — Build a new `ROARMessage`.
- **`signMessage(message, secretKey)`** — Add an HMAC-SHA256 signature.
- **`verifyMessage(message, secretKey)`** — Verify the signature (timing-safe comparison).

### AgentDirectory

In-memory registry for agent discovery.

```typescript
import { AgentDirectory } from "@roar-protocol/sdk";

const dir = new AgentDirectory();
dir.register(agentCard);
const agents = dir.discover("summarize"); // filter by capability
const agent = dir.get("roar_abc123");
dir.unregister("roar_abc123");
```

### ROARClient

High-level client wrapping identity, directory, and message operations.

```typescript
const client = new ROARClient(identity, { secretKey: "key" });
client.register("http://localhost:3000");
client.registerPeer(otherAgentCard);
const results = client.discover("translation");
const msg = await client.send(targetId, MessageIntent.QUERY, { text: "hello" });
```

### Adapters

Bridge ROAR messages to/from MCP and A2A protocols.

```typescript
import { MCPAdapter, A2AAdapter } from "@roar-protocol/sdk";

// MCP
const mcp = new MCPAdapter();
const toolCall = mcp.toMCPToolCall(roarMessage);
const roarResult = mcp.fromMCPResult(mcpResult, "server_id", "client_id");

// A2A
const a2a = new A2AAdapter();
const task = a2a.toA2ATask(roarMessage);
const roarResponse = a2a.fromA2AResult(a2aResult, "agent_id", "client_id");
```

## Message Signing

All messages can be signed with HMAC-SHA256 for authentication:

```typescript
import { createMessage, signMessage, verifyMessage, MessageIntent } from "@roar-protocol/sdk";

const msg = createMessage("agent_a", "agent_b", MessageIntent.QUERY, { text: "hello" });
const signed = signMessage(msg, "my-secret-key");
const valid = verifyMessage(signed, "my-secret-key"); // true
```

## License

MIT
