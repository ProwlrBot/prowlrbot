import { useMemo, useState } from "react";
import {
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { Agent, WarRoomEvent } from "../../api/warroom";

interface MetricsPanelProps {
  agents: Agent[];
  events: WarRoomEvent[];
}

const PIE_COLORS = {
  idle: "#22c55e",
  working: "#3b82f6",
  disconnected: "#555",
};

export default function MetricsPanel({ agents, events }: MetricsPanelProps) {
  const [collapsed, setCollapsed] = useState(false);

  // Agent utilization pie data
  const utilization = useMemo(() => {
    const counts = { idle: 0, working: 0, disconnected: 0 };
    for (const a of agents) {
      const s = a.status as keyof typeof counts;
      if (s in counts) counts[s]++;
      else counts.idle++;
    }
    return Object.entries(counts)
      .filter(([, v]) => v > 0)
      .map(([name, value]) => ({ name, value }));
  }, [agents]);

  // Task velocity — completions per hour from events
  const velocity = useMemo(() => {
    const completions = events.filter((e) => e.type === "task.completed");
    const hourMap = new Map<string, number>();

    for (const e of completions) {
      const d = new Date(e.timestamp);
      const key = `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:00`;
      hourMap.set(key, (hourMap.get(key) || 0) + 1);
    }

    // If no completions, show placeholder data
    if (hourMap.size === 0) {
      const now = new Date();
      return Array.from({ length: 6 }, (_, i) => {
        const h = new Date(now.getTime() - (5 - i) * 3600000);
        return { hour: `${h.getHours()}:00`, tasks: 0 };
      });
    }

    return [...hourMap.entries()]
      .sort()
      .slice(-12)
      .map(([hour, tasks]) => ({ hour, tasks }));
  }, [events]);

  if (collapsed) {
    return (
      <div
        onClick={() => setCollapsed(false)}
        style={{
          background: "#12121a",
          border: "1px solid #1e1e2e",
          borderRadius: 8,
          padding: "10px 16px",
          cursor: "pointer",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <span style={{ color: "#14b8a6", fontSize: 13, fontWeight: 600, textTransform: "uppercase", letterSpacing: 1 }}>
          Metrics
        </span>
        <span style={{ color: "#555", fontSize: 11 }}>Click to expand</span>
      </div>
    );
  }

  return (
    <div style={{ background: "#12121a", border: "1px solid #1e1e2e", borderRadius: 8, padding: 16 }}>
      <div
        onClick={() => setCollapsed(true)}
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 16,
          cursor: "pointer",
        }}
      >
        <span style={{ color: "#14b8a6", fontSize: 13, fontWeight: 600, textTransform: "uppercase", letterSpacing: 1 }}>
          Metrics
        </span>
        <span style={{ color: "#555", fontSize: 11 }}>Click to collapse</span>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {/* Task Velocity */}
        <div>
          <div style={{ color: "#888", fontSize: 11, marginBottom: 8, textTransform: "uppercase", letterSpacing: 1 }}>
            Task Velocity
          </div>
          <ResponsiveContainer width="100%" height={120}>
            <AreaChart data={velocity}>
              <defs>
                <linearGradient id="tealGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#14b8a6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#14b8a6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="hour" tick={{ fill: "#555", fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis hide allowDecimals={false} />
              <Tooltip
                contentStyle={{ background: "#1a1a2e", border: "1px solid #2e2e3e", borderRadius: 4, fontSize: 11 }}
                labelStyle={{ color: "#888" }}
              />
              <Area type="monotone" dataKey="tasks" stroke="#14b8a6" fill="url(#tealGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Agent Utilization */}
        <div>
          <div style={{ color: "#888", fontSize: 11, marginBottom: 8, textTransform: "uppercase", letterSpacing: 1 }}>
            Agent Utilization
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <ResponsiveContainer width={120} height={120}>
              <PieChart>
                <Pie data={utilization} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={30} outerRadius={50}>
                  {utilization.map((entry) => (
                    <Cell
                      key={entry.name}
                      fill={PIE_COLORS[entry.name as keyof typeof PIE_COLORS] || "#555"}
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ background: "#1a1a2e", border: "1px solid #2e2e3e", borderRadius: 4, fontSize: 11 }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
              {utilization.map((entry) => (
                <div key={entry.name} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11, color: "#aaa" }}>
                  <span
                    style={{
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      background: PIE_COLORS[entry.name as keyof typeof PIE_COLORS] || "#555",
                    }}
                  />
                  {entry.name}: {entry.value}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
