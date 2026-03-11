import { useEffect, useState, useCallback, useRef } from "react";
import { warroom, connectWarRoomWS } from "../../api/warroom";
import type { Agent, Task, WarRoomEvent, Finding } from "../../api/warroom";
import KanbanBoard from "./KanbanBoard";
import AgentCards from "./AgentCards";
import LiveFeed from "./LiveFeed";
import FindingsWall from "./FindingsWall";
import MetricsPanel from "./MetricsPanel";

export default function WarRoomPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [events, setEvents] = useState<WarRoomEvent[]>([]);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [a, t, e, f] = await Promise.all([
        warroom.agents(),
        warroom.board(),
        warroom.events(100),
        warroom.context(),
      ]);
      setAgents(a);
      setTasks(t);
      setEvents(e);
      setFindings(f);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Connection failed");
    }
  }, []);

  useEffect(() => {
    refresh();

    // WebSocket for real-time updates
    const disconnect = connectWarRoomWS(
      () => {
        // On any event, refresh all data
        refresh();
      },
      (status) => setConnected(status),
    );

    // Fallback polling every 10s
    pollRef.current = setInterval(refresh, 10000);

    return () => {
      disconnect();
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [refresh]);

  return (
    <div style={{ padding: 24, background: "#0a0a0f", minHeight: "100%" }}>
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 20,
        }}
      >
        <div>
          <h1
            style={{
              color: "#e0e0e0",
              fontSize: 22,
              fontWeight: 700,
              margin: 0,
              letterSpacing: 1,
            }}
          >
            War Room
          </h1>
          <div style={{ color: "#555", fontSize: 12, marginTop: 2 }}>
            Multi-agent coordination dashboard
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          {error && (
            <span style={{ color: "#ef4444", fontSize: 11 }}>{error}</span>
          )}
          <span
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              fontSize: 11,
              color: connected ? "#22c55e" : "#ef4444",
            }}
          >
            <span
              style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                background: connected ? "#22c55e" : "#ef4444",
                boxShadow: connected ? "0 0 8px #22c55e" : "none",
              }}
            />
            {connected ? "Live" : "Polling"}
          </span>
          <span style={{ color: "#888", fontSize: 11 }}>
            {agents.length} agents | {tasks.length} tasks
          </span>
        </div>
      </div>

      {/* Agent Cards */}
      <div style={{ marginBottom: 16 }}>
        <AgentCards agents={agents} />
      </div>

      {/* Metrics */}
      <div style={{ marginBottom: 16 }}>
        <MetricsPanel agents={agents} events={events} />
      </div>

      {/* Kanban Board */}
      <div style={{ marginBottom: 16 }}>
        <KanbanBoard tasks={tasks} onTaskSelect={() => {}} />
      </div>

      {/* Bottom row: Live Feed + Findings */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <LiveFeed events={events} />
        <FindingsWall findings={findings} />
      </div>
    </div>
  );
}
