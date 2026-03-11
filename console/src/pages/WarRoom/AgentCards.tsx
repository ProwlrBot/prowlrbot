import type { Agent } from "../../api/warroom";
import styles from "./AgentCards.module.less";

interface AgentCardsProps {
  agents: Agent[];
  onAgentSelect?: (agent: Agent) => void;
}

const CAP_STYLES: Record<string, string> = {
  python: styles.tagPython,
  testing: styles.tagPython,
  security: styles.tagSecurity,
  frontend: styles.tagFrontend,
  react: styles.tagFrontend,
  typescript: styles.tagFrontend,
  docs: styles.tagDocs,
  documentation: styles.tagDocs,
  general: styles.tagGeneral,
};

function dotClass(status: string): string {
  if (status === "working") return styles.dotWorking;
  if (status === "disconnected") return styles.dotDisconnected;
  return styles.dotIdle;
}

function heartbeatAge(lastHeartbeat: string): {
  label: string;
  className: string;
} {
  if (!lastHeartbeat) return { label: "unknown", className: styles.heartbeatDead };
  const age = Date.now() - new Date(lastHeartbeat).getTime();
  const mins = Math.floor(age / 60000);
  if (mins < 1) return { label: "just now", className: styles.heartbeatFresh };
  if (mins < 3) return { label: `${mins}m ago`, className: styles.heartbeatFresh };
  if (mins < 5) return { label: `${mins}m ago`, className: styles.heartbeatStale };
  return { label: `${mins}m ago`, className: styles.heartbeatDead };
}

export default function AgentCards({ agents, onAgentSelect }: AgentCardsProps) {
  const active = agents.filter((a) => a.status !== "disconnected");

  return (
    <div className={styles.grid}>
      {active.map((agent) => {
        const hb = heartbeatAge(agent.last_heartbeat);
        return (
          <div
            key={agent.agent_id}
            className={styles.card}
            onClick={() => onAgentSelect?.(agent)}
          >
            <div className={styles.cardHeader}>
              <span className={`${styles.dot} ${dotClass(agent.status)}`} />
              <span className={styles.name}>{agent.name}</span>
              <span className={styles.status}>{agent.status}</span>
            </div>
            <div className={styles.tags}>
              {agent.capabilities.map((cap) => (
                <span
                  key={cap}
                  className={`${styles.tag} ${CAP_STYLES[cap] || styles.tagGeneral}`}
                >
                  {cap}
                </span>
              ))}
            </div>
            {agent.current_task_id && (
              <div className={styles.taskLink}>
                Working on: {agent.current_task_id.slice(0, 16)}...
              </div>
            )}
            <div className={`${styles.heartbeat} ${hb.className}`}>
              Heartbeat: {hb.label}
            </div>
          </div>
        );
      })}
    </div>
  );
}
