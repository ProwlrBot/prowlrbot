import { MessageIntent, ROARMessage } from "./types";
import { createMessage } from "./message";

/**
 * Adapter for converting between ROAR messages and
 * Model Context Protocol (MCP) tool calls / results.
 */
export class MCPAdapter {
  /**
   * Convert a ROAR TOOL_CALL message to an MCP-compatible tool call object.
   */
  toMCPToolCall(msg: ROARMessage): {
    name: string;
    arguments: Record<string, unknown>;
    call_id: string;
  } {
    const content = msg.content as {
      tool_name?: string;
      arguments?: Record<string, unknown>;
    };
    return {
      name: content.tool_name ?? "unknown",
      arguments: content.arguments ?? {},
      call_id: msg.id,
    };
  }

  /**
   * Convert an MCP tool result back into a ROAR TOOL_RESULT message.
   *
   * @param result - The MCP result payload, expected to contain call_id, content, and is_error.
   * @param fromAgent - Agent ID that produced the result.
   * @param toAgent - Agent ID that made the original call.
   */
  fromMCPResult(
    result: {
      call_id?: string;
      content?: unknown;
      is_error?: boolean;
    },
    fromAgent: string = "mcp_server",
    toAgent: string = "roar_client",
  ): ROARMessage {
    const intent = result.is_error
      ? MessageIntent.ERROR
      : MessageIntent.TOOL_RESULT;
    return createMessage(fromAgent, toAgent, intent, {
      call_id: result.call_id,
      result: result.content,
      is_error: result.is_error ?? false,
    });
  }
}

/**
 * Adapter for converting between ROAR messages and
 * Agent-to-Agent (A2A) protocol tasks / results.
 */
export class A2AAdapter {
  /**
   * Convert a ROAR QUERY message to an A2A-compatible task object.
   */
  toA2ATask(msg: ROARMessage): {
    id: string;
    message: { role: string; parts: Array<{ type: string; text: string }> };
    metadata?: Record<string, unknown>;
  } {
    const textContent =
      typeof msg.content === "string"
        ? msg.content
        : JSON.stringify(msg.content);
    return {
      id: msg.id,
      message: {
        role: "user",
        parts: [{ type: "text", text: textContent }],
      },
      metadata: msg.metadata,
    };
  }

  /**
   * Convert an A2A task result back into a ROAR RESPONSE message.
   *
   * @param result - The A2A result payload.
   * @param fromAgent - Agent ID that produced the result.
   * @param toAgent - Agent ID that made the original request.
   */
  fromA2AResult(
    result: {
      id?: string;
      status?: { state?: string; message?: unknown };
      artifacts?: Array<{ parts?: Array<{ type?: string; text?: string }> }>;
    },
    fromAgent: string = "a2a_agent",
    toAgent: string = "roar_client",
  ): ROARMessage {
    const isError = result.status?.state === "failed";
    const intent = isError ? MessageIntent.ERROR : MessageIntent.RESPONSE;

    // Extract text from artifacts if present
    let content: unknown = result.status?.message;
    if (result.artifacts && result.artifacts.length > 0) {
      const parts = result.artifacts.flatMap((a) => a.parts ?? []);
      const texts = parts
        .filter((p) => p.type === "text")
        .map((p) => p.text)
        .join("\n");
      if (texts) {
        content = texts;
      }
    }

    return createMessage(fromAgent, toAgent, intent, {
      task_id: result.id,
      result: content,
      state: result.status?.state ?? "unknown",
    });
  }
}
