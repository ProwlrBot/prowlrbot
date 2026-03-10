// ROAR Protocol TypeScript SDK
// Unified agent communication — aligned with Python SDK

export {
  AgentCapability,
  AgentIdentity,
  AgentCard,
  DiscoveryEntry,
  TransportType,
  ConnectionConfig,
  MessageIntent,
  ROARMessage,
  StreamEventType,
  StreamEvent,
} from "./types";

export { createIdentity, generateDid } from "./identity";

export { createMessage, signMessage, verifyMessage } from "./message";

export { AgentDirectory } from "./directory";

export { ROARClient, ROARClientOptions } from "./client";

export { MCPAdapter, A2AAdapter } from "./adapters";
