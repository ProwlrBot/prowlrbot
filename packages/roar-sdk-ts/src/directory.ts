import { AgentCard } from "./types";

/**
 * In-memory agent directory for discovering and managing registered agents.
 */
export class AgentDirectory {
  private agents: Map<string, AgentCard> = new Map();

  /**
   * Register an agent card in the directory.
   * If an agent with the same ID already exists, it will be replaced.
   */
  register(card: AgentCard): void {
    this.agents.set(card.identity.agent_id, card);
  }

  /**
   * Remove an agent from the directory by ID.
   */
  unregister(agentId: string): void {
    this.agents.delete(agentId);
  }

  /**
   * Discover agents in the directory.
   *
   * @param capability - Optional capability name to filter by.
   *   When provided, only agents that advertise a matching capability are returned.
   * @returns An array of matching agent cards.
   */
  discover(capability?: string): AgentCard[] {
    const cards = Array.from(this.agents.values());
    if (!capability) {
      return cards;
    }
    return cards.filter((card) =>
      card.identity.capabilities.some((cap) => cap.name === capability),
    );
  }

  /**
   * Look up a single agent by ID.
   */
  get(agentId: string): AgentCard | undefined {
    return this.agents.get(agentId);
  }
}
