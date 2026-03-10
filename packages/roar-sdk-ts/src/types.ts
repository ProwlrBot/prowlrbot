/**
 * ROAR Protocol — Core type definitions
 */

/** Describes a capability that an agent can provide. */
export interface AgentCapability {
  name: string;
  version: string;
  description: string;
}

/** The identity of an agent on the ROAR network. */
export interface AgentIdentity {
  agent_id: string;
  display_name: string;
  public_key?: string;
  capabilities: AgentCapability[];
  created_at: string;
}

/** A discoverable agent card published to the directory. */
export interface AgentCard {
  identity: AgentIdentity;
  endpoint: string;
  transport_types: TransportType[];
  metadata?: Record<string, unknown>;
}

/** Supported transport mechanisms. */
export enum TransportType {
  STDIO = "stdio",
  HTTP = "http",
  WEBSOCKET = "websocket",
  GRPC = "grpc",
}

/** Configuration for connecting to a remote agent. */
export interface ConnectionConfig {
  transport: TransportType;
  endpoint: string;
  headers?: Record<string, string>;
  auth_token?: string;
}

/** The semantic intent of a ROAR message. */
export enum MessageIntent {
  QUERY = "query",
  RESPONSE = "response",
  TOOL_CALL = "tool_call",
  TOOL_RESULT = "tool_result",
  NEGOTIATE = "negotiate",
  HEARTBEAT = "heartbeat",
  ERROR = "error",
  STREAM_START = "stream_start",
  STREAM_DATA = "stream_data",
  STREAM_END = "stream_end",
}

/** A message exchanged between agents via the ROAR protocol. */
export interface ROARMessage {
  id: string;
  from_agent: string;
  to_agent: string;
  intent: MessageIntent;
  content: unknown;
  timestamp: string;
  signature?: string;
  metadata?: Record<string, unknown>;
}

/** Types of events emitted during a streaming exchange. */
export enum StreamEventType {
  STARTED = "started",
  DATA = "data",
  PROGRESS = "progress",
  COMPLETED = "completed",
  ERROR = "error",
  CANCELLED = "cancelled",
}

/** A single event within a streaming exchange. */
export interface StreamEvent {
  event_type: StreamEventType;
  stream_id: string;
  data?: unknown;
  sequence: number;
  timestamp: string;
}
