/**
 * ROAR Protocol — Core type definitions.
 *
 * Canonical source of truth: Python SDK (src/prowlrbot/protocols/roar.py).
 * This file MUST stay in sync with the Python types.
 */

// ---------------------------------------------------------------------------
// Layer 1: Identity
// ---------------------------------------------------------------------------

/** A declared capability that an agent can perform. */
export interface AgentCapability {
  name: string;
  description: string;
  input_schema: Record<string, unknown>;
  output_schema: Record<string, unknown>;
}

/** W3C DID-based agent identity. */
export interface AgentIdentity {
  /** W3C DID, e.g. "did:roar:agent:my-agent-a1b2c3d4" */
  did: string;
  display_name: string;
  /** One of: agent, tool, human, ide */
  agent_type: string;
  /** Simple capability identifiers */
  capabilities: string[];
  /** Protocol version this agent supports */
  version: string;
  /** Optional Ed25519 public key (hex-encoded) */
  public_key?: string;
}

/** A discoverable agent card published to the directory. */
export interface AgentCard {
  identity: AgentIdentity;
  description: string;
  skills: string[];
  channels: string[];
  /** Transport-type to URL mapping, e.g. { http: "http://localhost:8089" } */
  endpoints: Record<string, string>;
  declared_capabilities: AgentCapability[];
  metadata: Record<string, unknown>;
}

// ---------------------------------------------------------------------------
// Layer 2: Discovery
// ---------------------------------------------------------------------------

/** Entry in the agent discovery directory. */
export interface DiscoveryEntry {
  agent_card: AgentCard;
  registered_at: number;
  last_seen: number;
  hub_url: string;
}

// ---------------------------------------------------------------------------
// Layer 3: Connect
// ---------------------------------------------------------------------------

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
  url: string;
  /** Authentication method: hmac, jwt, mtls, none */
  auth_method: string;
  secret: string;
  timeout_ms: number;
}

// ---------------------------------------------------------------------------
// Layer 4: Exchange
// ---------------------------------------------------------------------------

/**
 * The semantic intent of a ROAR message.
 *
 * MUST match Python's MessageIntent enum exactly (7 values).
 */
export enum MessageIntent {
  /** Agent → Tool: invoke a tool or function */
  EXECUTE = "execute",
  /** Agent → Agent: hand off a task to another agent */
  DELEGATE = "delegate",
  /** Agent → IDE: push a status or result update */
  UPDATE = "update",
  /** Agent → Human: request human input or approval */
  ASK = "ask",
  /** Any → Any: reply to any of the above intents */
  RESPOND = "respond",
  /** Any → Any: one-way informational notification */
  NOTIFY = "notify",
  /** Any → Directory: request agent discovery */
  DISCOVER = "discover",
}

/** A message exchanged between agents via the ROAR protocol. */
export interface ROARMessage {
  /** Protocol version */
  roar: string;
  /** Unique message ID (format: msg_<hex10>) */
  id: string;
  /** Sender identity */
  from_identity: AgentIdentity;
  /** Receiver identity */
  to_identity: AgentIdentity;
  /** What the sender wants */
  intent: MessageIntent;
  /** Message content (intent-specific) */
  payload: Record<string, unknown>;
  /** Metadata (session, thread, protocol) */
  context: Record<string, unknown>;
  /** Authentication data (signature, signer, timestamp) */
  auth: Record<string, unknown>;
  /** Unix timestamp of creation */
  timestamp: number;
}

// ---------------------------------------------------------------------------
// Layer 5: Stream
// ---------------------------------------------------------------------------

/**
 * Types of events emitted during streaming.
 *
 * MUST match Python's StreamEventType enum exactly (8 values).
 */
export enum StreamEventType {
  TOOL_CALL = "tool_call",
  MCP_REQUEST = "mcp_request",
  REASONING = "reasoning",
  TASK_UPDATE = "task_update",
  MONITOR_ALERT = "monitor_alert",
  AGENT_STATUS = "agent_status",
  CHECKPOINT = "checkpoint",
  WORLD_UPDATE = "world_update",
}

/** A single event within a streaming exchange. */
export interface StreamEvent {
  type: StreamEventType;
  /** DID of the event source */
  source: string;
  session_id: string;
  data: Record<string, unknown>;
  /** Unix timestamp */
  timestamp: number;
}
