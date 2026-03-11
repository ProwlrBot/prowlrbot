import { useMemo, useState } from "react";
import type { Agent, Finding } from "../../api/warroom";
import styles from "./FindingsWall.module.less";

interface FindingsWallProps {
  findings: Finding[];
  agents?: Agent[];
}

function formatTime(ts: string): string {
  try {
    return new Date(ts).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "--:--";
  }
}

export default function FindingsWall({ findings, agents }: FindingsWallProps) {
  const [search, setSearch] = useState("");
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  // Build agent name lookup
  const agentNames = useMemo(() => {
    const map = new Map<string, string>();
    if (agents) {
      for (const a of agents) {
        map.set(a.agent_id, a.name);
      }
    }
    return map;
  }, [agents]);

  const filtered = useMemo(() => {
    if (!search) return findings;
    const lower = search.toLowerCase();
    return findings.filter(
      (f) =>
        f.key.toLowerCase().includes(lower) ||
        f.value.toLowerCase().includes(lower) ||
        (agentNames.get(f.agent_id) || "").toLowerCase().includes(lower),
    );
  }, [findings, search, agentNames]);

  const toggleExpand = (key: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className={styles.title}>
          Shared Findings
          <span className={styles.count}>{findings.length}</span>
        </span>
        <input
          type="text"
          placeholder="Search findings..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className={styles.searchInput}
        />
      </div>
      <div className={styles.grid}>
        {filtered.length === 0 && (
          <div className={styles.empty}>
            {search ? "No findings match your search" : "No findings shared yet"}
          </div>
        )}
        {filtered.map((finding) => {
          const isExpanded = expanded.has(finding.key);
          const agentLabel =
            agentNames.get(finding.agent_id) ||
            finding.agent_id?.slice(0, 12) ||
            "unknown";

          return (
            <div
              key={finding.key}
              className={styles.card}
              onClick={() => toggleExpand(finding.key)}
            >
              <div className={styles.cardKey}>{finding.key}</div>
              <div
                className={
                  isExpanded ? styles.cardValueExpanded : styles.cardValue
                }
              >
                {finding.value}
              </div>
              <div className={styles.cardFooter}>
                <span>{agentLabel}</span>
                <span>{formatTime(finding.updated_at)}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
