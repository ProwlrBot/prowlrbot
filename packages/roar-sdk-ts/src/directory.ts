import { AgentCard, DiscoveryEntry } from "./types";

/**
 * In-memory agent directory for discovering and managing registered agents.
 *
 * Matches Python's AgentDirectory class. Uses DID as the key.
 */
export class AgentDirectory {
  private agents: Map<string, DiscoveryEntry> = new Map();

  /**
   * Register an agent card in the directory.
   * If an agent with the same DID already exists, it will be replaced.
   *
   * @returns The created DiscoveryEntry.
   */
  register(card: AgentCard): DiscoveryEntry {
    const now = Date.now() / 1000;
    const entry: DiscoveryEntry = {
      agent_card: card,
      registered_at: now,
      last_seen: now,
      hub_url: "",
    };
    this.agents.set(card.identity.did, entry);
    return entry;
  }

  /**
   * Remove an agent from the directory by DID.
   *
   * @returns true if the agent was found and removed.
   */
  unregister(did: string): boolean {
    return this.agents.delete(did);
  }

  /**
   * Look up a single agent by DID.
   */
  lookup(did: string): DiscoveryEntry | undefined {
    return this.agents.get(did);
  }

  /**
   * Find agents with a specific capability.
   *
   * @param capability - Capability identifier to filter by.
   * @returns All entries whose agent identity declares the given capability.
   */
  search(capability: string): DiscoveryEntry[] {
    return Array.from(this.agents.values()).filter((entry) =>
      entry.agent_card.identity.capabilities.includes(capability),
    );
  }

  /**
   * Return all registered entries.
   */
  listAll(): DiscoveryEntry[] {
    return Array.from(this.agents.values());
  }
}
