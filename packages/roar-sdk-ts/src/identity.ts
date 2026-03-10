import * as crypto from "crypto";
import { AgentCapability, AgentIdentity } from "./types";

/**
 * Generate a unique ROAR agent identifier.
 * Format: roar_ followed by 16 hex characters.
 */
export function generateAgentId(): string {
  return `roar_${crypto.randomBytes(8).toString("hex")}`;
}

/**
 * Create a new agent identity.
 *
 * @param displayName - Human-readable name for the agent.
 * @param capabilities - Optional list of capabilities this agent provides.
 * @returns A fully populated AgentIdentity.
 */
export function createIdentity(
  displayName: string,
  capabilities: AgentCapability[] = [],
): AgentIdentity {
  return {
    agent_id: generateAgentId(),
    display_name: displayName,
    capabilities,
    created_at: new Date().toISOString(),
  };
}
