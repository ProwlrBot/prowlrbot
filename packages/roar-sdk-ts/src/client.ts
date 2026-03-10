import {
  AgentCard,
  AgentIdentity,
  ConnectionConfig,
  DiscoveryEntry,
  MessageIntent,
  ROARMessage,
  TransportType,
} from "./types";
import { createMessage, signMessage } from "./message";
import { AgentDirectory } from "./directory";

/** Options for constructing a ROARClient. */
export interface ROARClientOptions {
  /** URL of a remote agent directory (reserved for future use). */
  directoryUrl?: string;
  /** Shared secret key used to sign outgoing messages. */
  signingSecret?: string;
}

/**
 * High-level client for the ROAR protocol.
 *
 * Wraps identity management, message creation/signing, and agent discovery
 * into a single convenient interface. Matches Python's ROARClient API.
 */
export class ROARClient {
  readonly identity: AgentIdentity;
  private readonly directory: AgentDirectory;
  private readonly signingSecret?: string;
  private readonly directoryUrl?: string;

  constructor(identity: AgentIdentity, options: ROARClientOptions = {}) {
    this.identity = identity;
    this.directory = new AgentDirectory();
    this.signingSecret = options.signingSecret;
    this.directoryUrl = options.directoryUrl;
  }

  /**
   * Register an agent card with the local directory.
   */
  register(card: AgentCard): DiscoveryEntry {
    return this.directory.register(card);
  }

  /**
   * Find agents, optionally filtered by capability.
   */
  discover(capability?: string): DiscoveryEntry[] {
    if (capability) {
      return this.directory.search(capability);
    }
    return this.directory.listAll();
  }

  /**
   * Create, sign, and return a ROAR message.
   *
   * In a full implementation this would transmit the message over the
   * configured transport. Currently constructs and signs locally.
   *
   * @param toAgentDid - DID of the target agent.
   * @param intent - What the sender wants the receiver to do.
   * @param content - Payload dictionary.
   * @param msgContext - Optional context metadata.
   * @returns A signed ROARMessage ready for transmission.
   */
  send(
    toAgentDid: string,
    intent: MessageIntent,
    content: Record<string, unknown>,
    msgContext: Record<string, unknown> = {},
  ): ROARMessage {
    const entry = this.directory.lookup(toAgentDid);
    const toIdentity: AgentIdentity = entry
      ? entry.agent_card.identity
      : {
          did: toAgentDid,
          display_name: "unknown",
          agent_type: "agent",
          capabilities: [],
          version: "1.0",
        };

    let msg = createMessage(
      this.identity,
      toIdentity,
      intent,
      content,
      msgContext,
    );

    if (this.signingSecret) {
      msg = signMessage(msg, this.signingSecret);
    }

    return msg;
  }

  /**
   * Build a connection config for the given agent.
   *
   * Looks up the agent's registered endpoints and returns a
   * ConnectionConfig with the appropriate URL and auth details.
   */
  connect(
    agentDid: string,
    transport: TransportType = TransportType.HTTP,
  ): ConnectionConfig {
    const entry = this.directory.lookup(agentDid);
    let url = "";
    if (entry) {
      const endpoints = entry.agent_card.endpoints;
      url = endpoints[transport] ?? endpoints["http"] ?? "";
    }

    return {
      transport,
      url,
      auth_method: "hmac",
      secret: this.signingSecret ?? "",
      timeout_ms: 30000,
    };
  }

  /**
   * Get the underlying directory instance.
   */
  getDirectory(): AgentDirectory {
    return this.directory;
  }
}
