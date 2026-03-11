import { Tooltip } from "antd";
import type { Agent, Task } from "../../api/warroom";
import styles from "./AgentCards.module.less";

interface AgentCardsProps {
  agents: Agent[];
  tasks?: Task[];
  onAgentSelect?: (agent: Agent) => void;
}

const CAP_STYLES: Record<string, string> = {
  python: styles.tagPython,
  testing: styles.tagPython,
  security: styles.tagSecurity,
  security_audit: styles.tagSecurity,
  frontend: styles.tagFrontend,
  react: styles.tagFrontend,
  typescript: styles.tagFrontend,
  css: styles.tagFrontend,
  docs: styles.tagDocs,
  documentation: styles.tagDocs,
  devops: styles.tagDevops,
  docker: styles.tagDevops,
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
  if (!lastHeartbeat)
    return { label: "unknown", className: styles.heartbeatDead };
  const age = Date.now() - new Date(lastHeartbeat).getTime();
  const mins = Math.floor(age / 60000);
  if (mins < 1) return { label: "just now", className: styles.heartbeatFresh };
  if (mins < 3)
    return { label: `${mins}m ago`, className: styles.heartbeatFresh };
  if (mins < 5)
    return { label: `${mins}m ago`, className: styles.heartbeatStale };
  return { label: `${mins}m ago`, className: styles.heartbeatDead };
}

function platformIcon(agentId: string): string | null {
  // Detect platform from agent name/id conventions
  const lower = agentId.toLowerCase();
  if (lower.includes("mac") || lower.includes("darwin")) return "macOS";
  if (lower.includes("linux")) return "Linux";
  if (lower.includes("wsl")) return "WSL";
  if (lower.includes("win")) return "Windows";
  return null;
}

function AgentCard({
  agent,
  currentTask,
  onSelect,
}: {
  agent: Agent;
  currentTask?: Task;
  onSelect?: (a: Agent) => void;
}) {
  const hb = heartbeatAge(agent.last_heartbeat);
  const platform = platformIcon(agent.agent_id);
  const isDisconnected = agent.status === "disconnected";

  return (
    <div
      className={`${styles.card} ${isDisconnected ? styles.cardDisconnected : ""}`}
      onClick={() => onSelect?.(agent)}
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
      {currentTask && (
        <Tooltip title={currentTask.description || currentTask.title}>
          <div className={styles.taskLink}>
            Working on: {currentTask.title}
          </div>
        </Tooltip>
      )}
      {agent.current_task_id && !currentTask && (
        <div className={styles.taskLink}>
          Working on: {agent.current_task_id.slice(0, 16)}...
        </div>
      )}
      <div className={styles.cardFooter}>
        <span className={`${styles.heartbeat} ${hb.className}`}>
          {hb.label}
        </span>
        {platform && (
          <span className={styles.platformBadge}>{platform}</span>
        )}
      </div>
    </div>
  );
}

export default function AgentCards({
  agents,
  tasks,
  onAgentSelect,
}: AgentCardsProps) {
  const active = agents.filter((a) => a.status !== "disconnected");
  const disconnected = agents.filter((a) => a.status === "disconnected");

  // Build task lookup for showing task titles on agent cards
  const taskMap = new Map<string, Task>();
  if (tasks) {
    for (const t of tasks) {
      taskMap.set(t.task_id, t);
    }
  }

  return (
    <div>
      <div className={styles.grid}>
        {active.length === 0 && disconnected.length === 0 && (
          <div className={styles.empty}>No agents connected</div>
        )}
        {active.map((agent) => (
          <AgentCard
            key={agent.agent_id}
            agent={agent}
            currentTask={
              agent.current_task_id
                ? taskMap.get(agent.current_task_id)
                : undefined
            }
            onSelect={onAgentSelect}
          />
        ))}
      </div>
      {disconnected.length > 0 && (
        <>
          <div className={styles.sectionLabel}>
            Disconnected ({disconnected.length})
          </div>
          <div className={styles.grid}>
            {disconnected.map((agent) => (
              <AgentCard
                key={agent.agent_id}
                agent={agent}
                onSelect={onAgentSelect}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
