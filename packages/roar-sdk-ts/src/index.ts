// ROAR Protocol TypeScript SDK
// Unified agent communication

export {
  AgentCapability,
  AgentIdentity,
  AgentCard,
  TransportType,
  ConnectionConfig,
  MessageIntent,
  ROARMessage,
  StreamEventType,
  StreamEvent,
} from "./types";

export { createIdentity, generateAgentId } from "./identity";

export { createMessage, signMessage, verifyMessage } from "./message";

export { AgentDirectory } from "./directory";

export { ROARClient, ROARClientOptions } from "./client";

export { MCPAdapter, A2AAdapter } from "./adapters";
