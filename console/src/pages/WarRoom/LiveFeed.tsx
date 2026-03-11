import { useState } from "react";
import { Tag } from "antd";
import type { WarRoomEvent } from "../../api/warroom";

interface LiveFeedProps {
  events: WarRoomEvent[];
}

const EVENT_COLORS: Record<string, string> = {
  "task.created": "blue",
  "task.claimed": "cyan",
  "task.updated": "geekblue",
  "task.completed": "green",
  "task.failed": "red",
  "agent.connected": "lime",
  "agent.disconnected": "default",
  "agent.broadcast": "purple",
  "lock.acquired": "orange",
  "lock.released": "default",
  "finding.shared": "gold",
};

const FILTERS = ["all", "tasks", "locks", "broadcasts", "findings"] as const;

function matchesFilter(event: WarRoomEvent, filter: string): boolean {
  if (filter === "all") return true;
  if (filter === "tasks") return event.type.startsWith("task.");
  if (filter === "locks") return event.type.startsWith("lock.");
  if (filter === "broadcasts") return event.type === "agent.broadcast";
  if (filter === "findings") return event.type === "finding.shared";
  return true;
}

function formatTime(ts: string): string {
  try {
    return new Date(ts).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "—";
  }
}

export default function LiveFeed({ events }: LiveFeedProps) {
  const [filter, setFilter] = useState<string>("all");

  const filtered = events.filter((e) => matchesFilter(e, filter));

  return (
    <div style={{ background: "#12121a", border: "1px solid #1e1e2e", borderRadius: 8, padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <span style={{ color: "#14b8a6", fontSize: 13, fontWeight: 600, textTransform: "uppercase", letterSpacing: 1 }}>
          Live Feed
        </span>
        <div style={{ display: "flex", gap: 4 }}>
          {FILTERS.map((f) => (
            <span
              key={f}
              onClick={() => setFilter(f)}
              style={{
                fontSize: 11,
                padding: "2px 8px",
                borderRadius: 4,
                cursor: "pointer",
                background: filter === f ? "rgba(20,184,166,0.15)" : "#1e1e2e",
                color: filter === f ? "#14b8a6" : "#888",
              }}
            >
              {f}
            </span>
          ))}
        </div>
      </div>
      <div style={{ maxHeight: 400, overflowY: "auto", display: "flex", flexDirection: "column", gap: 6 }}>
        {filtered.length === 0 && (
          <div style={{ color: "#555", fontSize: 12, textAlign: "center", padding: 20, fontStyle: "italic" }}>
            No events yet
          </div>
        )}
        {filtered.map((event) => (
          <div
            key={event.event_id}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "6px 0",
              borderBottom: "1px solid #1e1e2e",
              fontSize: 12,
              animation: "slideIn 0.3s ease",
            }}
          >
            <span style={{ color: "#555", minWidth: 50, fontSize: 11 }}>
              {formatTime(event.timestamp)}
            </span>
            <Tag color={EVENT_COLORS[event.type] || "default"} style={{ fontSize: 10, margin: 0 }}>
              {event.type.split(".").pop()}
            </Tag>
            <span style={{ color: "#aaa", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
              {event.agent_id ? event.agent_id.slice(0, 12) : "system"}
              {event.task_id ? ` → ${event.task_id.slice(0, 12)}` : ""}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
