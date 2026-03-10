import {
  AgentCard,
  AgentIdentity,
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
  secretKey?: string;
}

/**
 * High-level client for the ROAR protocol.
 *
 * Wraps identity management, message creation/signing, and agent discovery
 * into a single convenient interface.
 */
export class ROARClient {
  readonly identity: AgentIdentity;
  private readonly directory: AgentDirectory;
  private readonly secretKey?: string;
  private readonly directoryUrl?: string;

  constructor(identity: AgentIdentity, options: ROARClientOptions = {}) {
    this.identity = identity;
    this.directory = new AgentDirectory();
    this.secretKey = options.secretKey;
    this.directoryUrl = options.directoryUrl;
  }

  /**
   * Send a message to another agent.
   *
   * The message is signed when a secretKey was provided at construction time.
   * Currently performs a local round-trip (returns the constructed message).
   * Future versions will dispatch over the configured transport.
   *
   * @param toAgentId - Recipient agent ID.
   * @param intent - Semantic intent of the message.
   * @param content - Message payload.
   * @returns The constructed (and optionally signed) ROARMessage.
   */
  async send(
    toAgentId: string,
    intent: MessageIntent,
    content: object,
  ): Promise<ROARMessage> {
    let message = createMessage(
      this.identity.agent_id,
      toAgentId,
      intent,
      content,
    );
    if (this.secretKey) {
      message = signMessage(message, this.secretKey);
    }
    // Future: dispatch over HTTP / WebSocket / gRPC based on target agent's
    // transport configuration retrieved from the directory.
    return message;
  }

  /**
   * Discover agents from the local directory, optionally filtering by capability.
   */
  discover(capability?: string): AgentCard[] {
    return this.directory.discover(capability);
  }

  /**
   * Register this client's identity in the local directory.
   *
   * @param endpoint - The endpoint where this agent can be reached.
   * @param transportTypes - Transports this agent supports (defaults to HTTP).
   */
  register(
    endpoint: string = "local://self",
    transportTypes: TransportType[] = [TransportType.HTTP],
  ): void {
    const card: AgentCard = {
      identity: this.identity,
      endpoint,
      transport_types: transportTypes,
    };
    this.directory.register(card);
  }

  /**
   * Register an external agent card in the local directory.
   */
  registerPeer(card: AgentCard): void {
    this.directory.register(card);
  }

  /**
   * Get the underlying directory instance.
   */
  getDirectory(): AgentDirectory {
    return this.directory;
  }
}
