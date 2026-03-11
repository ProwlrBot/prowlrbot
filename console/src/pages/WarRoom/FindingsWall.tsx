import { useState } from "react";
import type { Finding } from "../../api/warroom";

interface FindingsWallProps {
  findings: Finding[];
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

export default function FindingsWall({ findings }: FindingsWallProps) {
  const [search, setSearch] = useState("");
  const [expanded, setExpanded] = useState<string | null>(null);

  const filtered = search
    ? findings.filter(
        (f) =>
          f.key.toLowerCase().includes(search.toLowerCase()) ||
          f.value.toLowerCase().includes(search.toLowerCase()),
      )
    : findings;

  return (
    <div style={{ background: "#12121a", border: "1px solid #1e1e2e", borderRadius: 8, padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <span style={{ color: "#14b8a6", fontSize: 13, fontWeight: 600, textTransform: "uppercase", letterSpacing: 1 }}>
          Shared Findings
        </span>
        <input
          type="text"
          placeholder="Search..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            background: "#1e1e2e",
            border: "1px solid #2e2e3e",
            borderRadius: 4,
            padding: "4px 8px",
            color: "#e0e0e0",
            fontSize: 11,
            outline: "none",
            width: 140,
          }}
        />
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: 8 }}>
        {filtered.length === 0 && (
          <div style={{ color: "#555", fontSize: 12, textAlign: "center", padding: 20, fontStyle: "italic", gridColumn: "1 / -1" }}>
            No findings shared yet
          </div>
        )}
        {filtered.map((finding) => (
          <div
            key={finding.key}
            onClick={() => setExpanded(expanded === finding.key ? null : finding.key)}
            style={{
              background: "#1a1a2e",
              border: "1px solid #1e1e2e",
              borderRadius: 6,
              padding: 12,
              cursor: "pointer",
              transition: "border-color 0.15s ease",
            }}
          >
            <div style={{ fontSize: 12, fontWeight: 600, color: "#e0e0e0", marginBottom: 4 }}>
              {finding.key}
            </div>
            <div
              style={{
                fontSize: 11,
                color: "#aaa",
                overflow: expanded === finding.key ? "visible" : "hidden",
                textOverflow: expanded === finding.key ? "unset" : "ellipsis",
                whiteSpace: expanded === finding.key ? "pre-wrap" : "nowrap",
                maxHeight: expanded === finding.key ? "none" : 20,
              }}
            >
              {finding.value}
            </div>
            <div style={{ fontSize: 10, color: "#555", marginTop: 6, display: "flex", justifyContent: "space-between" }}>
              <span>{finding.agent_id?.slice(0, 12)}</span>
              <span>{formatTime(finding.updated_at)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
