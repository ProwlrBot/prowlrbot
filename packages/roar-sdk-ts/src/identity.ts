import * as crypto from "crypto";
import { AgentIdentity } from "./types";

/**
 * Generate a W3C DID for a ROAR agent.
 *
 * Format: did:roar:<agent_type>:<slug>-<uuid8>
 * Matches Python's AgentIdentity.model_post_init logic exactly.
 *
 * @param displayName - Human-readable name (used for slug).
 * @param agentType - One of: agent, tool, human, ide.
 * @returns A DID string.
 */
export function generateDid(
  displayName: string = "",
  agentType: string = "agent",
): string {
  const uid = crypto.randomBytes(4).toString("hex"); // 8 hex chars
  const slug =
    displayName.toLowerCase().replace(/\s+/g, "-").slice(0, 20) || "agent";
  return `did:roar:${agentType}:${slug}-${uid}`;
}

/**
 * Create a new agent identity.
 *
 * @param displayName - Human-readable name for the agent.
 * @param options - Optional fields (agentType, capabilities, version, publicKey).
 * @returns A fully populated AgentIdentity with auto-generated DID.
 */
export function createIdentity(
  displayName: string,
  options: {
    agentType?: string;
    capabilities?: string[];
    version?: string;
    publicKey?: string;
  } = {},
): AgentIdentity {
  const agentType = options.agentType ?? "agent";
  return {
    did: generateDid(displayName, agentType),
    display_name: displayName,
    agent_type: agentType,
    capabilities: options.capabilities ?? [],
    version: options.version ?? "1.0",
    public_key: options.publicKey,
  };
}
