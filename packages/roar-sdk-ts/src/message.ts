import * as crypto from "crypto";
import { AgentIdentity, MessageIntent, ROARMessage } from "./types";

/**
 * Create a new ROAR message.
 *
 * Matches Python's ROARMessage construction exactly.
 *
 * @param from - The sender's identity.
 * @param to - The recipient's identity.
 * @param intent - The semantic intent of the message.
 * @param payload - The message payload.
 * @param context - Optional context metadata.
 * @returns A new ROARMessage with a unique ID and timestamp.
 */
export function createMessage(
  from: AgentIdentity,
  to: AgentIdentity,
  intent: MessageIntent,
  payload: Record<string, unknown> = {},
  context: Record<string, unknown> = {},
): ROARMessage {
  return {
    roar: "1.0",
    id: `msg_${crypto.randomBytes(5).toString("hex")}`,
    from_identity: from,
    to_identity: to,
    intent,
    payload,
    context,
    auth: {},
    timestamp: Date.now() / 1000, // Unix epoch (seconds), matches Python's time.time()
  };
}

/**
 * Compute the canonical string for signing.
 *
 * MUST match Python's signing canonical body exactly:
 *   JSON.stringify({id, intent, payload}, sort_keys=True)
 *
 * Python uses json.dumps with sort_keys=True which sorts all keys
 * recursively. We replicate this with a recursive key-sorting replacer.
 */
function canonicalize(message: ROARMessage): string {
  const obj = {
    id: message.id,
    intent: message.intent,
    payload: message.payload,
  };
  return JSON.stringify(obj, sortKeysReplacer);
}

/**
 * JSON replacer that sorts object keys to match Python's sort_keys=True.
 */
function sortKeysReplacer(_key: string, value: unknown): unknown {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    const sorted: Record<string, unknown> = {};
    for (const k of Object.keys(value as Record<string, unknown>).sort()) {
      sorted[k] = (value as Record<string, unknown>)[k];
    }
    return sorted;
  }
  return value;
}

/**
 * Sign a ROAR message using HMAC-SHA256.
 *
 * Signature format: "hmac-sha256:<hex>" — matches Python exactly.
 *
 * @param message - The message to sign.
 * @param secret - The shared secret key.
 * @returns A new ROARMessage with the auth field populated.
 */
export function signMessage(
  message: ROARMessage,
  secret: string,
): ROARMessage {
  const body = canonicalize(message);
  const hmac = crypto.createHmac("sha256", secret);
  hmac.update(body);
  const sig = hmac.digest("hex");
  return {
    ...message,
    auth: {
      signature: `hmac-sha256:${sig}`,
      signer: message.from_identity.did,
      timestamp: Date.now() / 1000,
    },
  };
}

/**
 * Verify the HMAC-SHA256 signature on a ROAR message.
 *
 * @param message - The message to verify (must include auth.signature).
 * @param secret - The shared secret key.
 * @returns true if the signature is valid, false otherwise.
 */
export function verifyMessage(
  message: ROARMessage,
  secret: string,
): boolean {
  const sigValue = message.auth?.signature;
  if (typeof sigValue !== "string" || !sigValue.startsWith("hmac-sha256:")) {
    return false;
  }
  const expectedSig = sigValue.split(":")[1];
  const body = canonicalize(message);
  const hmac = crypto.createHmac("sha256", secret);
  hmac.update(body);
  const actualSig = hmac.digest("hex");
  return crypto.timingSafeEqual(
    Buffer.from(expectedSig, "hex"),
    Buffer.from(actualSig, "hex"),
  );
}
