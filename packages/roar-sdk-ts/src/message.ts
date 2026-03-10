import * as crypto from "crypto";
import { MessageIntent, ROARMessage } from "./types";

/**
 * Create a new ROAR message.
 *
 * @param from - The sender's agent ID.
 * @param to - The recipient's agent ID.
 * @param intent - The semantic intent of the message.
 * @param content - The message payload.
 * @returns A new ROARMessage with a unique ID and timestamp.
 */
export function createMessage(
  from: string,
  to: string,
  intent: MessageIntent,
  content: unknown,
): ROARMessage {
  return {
    id: crypto.randomUUID(),
    from_agent: from,
    to_agent: to,
    intent,
    content,
    timestamp: new Date().toISOString(),
  };
}

/**
 * Compute the canonical string representation of a message for signing.
 * Excludes the signature field itself.
 */
function canonicalize(message: ROARMessage): string {
  return JSON.stringify({
    id: message.id,
    from_agent: message.from_agent,
    to_agent: message.to_agent,
    intent: message.intent,
    content: message.content,
    timestamp: message.timestamp,
  });
}

/**
 * Sign a ROAR message using HMAC-SHA256.
 *
 * @param message - The message to sign.
 * @param secretKey - The shared secret key.
 * @returns A new ROARMessage with the signature field populated.
 */
export function signMessage(
  message: ROARMessage,
  secretKey: string,
): ROARMessage {
  const payload = canonicalize(message);
  const hmac = crypto.createHmac("sha256", secretKey);
  hmac.update(payload);
  const signature = hmac.digest("hex");
  return { ...message, signature };
}

/**
 * Verify the HMAC-SHA256 signature on a ROAR message.
 *
 * @param message - The message to verify (must include a signature).
 * @param secretKey - The shared secret key.
 * @returns true if the signature is valid, false otherwise.
 */
export function verifyMessage(
  message: ROARMessage,
  secretKey: string,
): boolean {
  if (!message.signature) {
    return false;
  }
  const payload = canonicalize(message);
  const hmac = crypto.createHmac("sha256", secretKey);
  hmac.update(payload);
  const expected = hmac.digest("hex");
  return crypto.timingSafeEqual(
    Buffer.from(message.signature, "hex"),
    Buffer.from(expected, "hex"),
  );
}
