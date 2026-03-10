import { Tooltip, Tag } from "antd";
import {
  Building,
  ShoppingCart,
  Hammer,
  Swords,
  BookOpen,
  ClipboardList,
  Home,
  Store,
} from "lucide-react";
import type { ReactNode } from "react";
import styles from "../index.module.less";

// ── Types ──
export interface AgentInfo {
  id: string;
  name: string;
  avatar: string;
  status: "online" | "idle" | "offline";
  zone?: string;
}

export interface ZoneInfo {
  id: string;
  name: string;
  description: string;
  icon: string;
  agents_online: number;
  premium?: boolean;
  color: string;
}

// ── Zone icon map ──
const ZONE_ICONS: Record<string, ReactNode> = {
  town_square: <Building size={20} />,
  trading_post: <ShoppingCart size={20} />,
  workshop: <Hammer size={20} />,
  arena: <Swords size={20} />,
  academy: <BookOpen size={20} />,
  mission_board: <ClipboardList size={20} />,
  home: <Home size={20} />,
  marketplace_mall: <Store size={20} />,
};

// ── Avatar colors ──
const AVATAR_COLORS: Record<string, string> = {
  cat: "#00E5FF",
  dog: "#4CAF50",
  fox: "#FF9800",
  owl: "#9C27B0",
  robot: "#607D8B",
  dragon: "#F44336",
};

const AVATAR_EMOJI: Record<string, string> = {
  cat: "\u{1F431}",
  dog: "\u{1F436}",
  fox: "\u{1F98A}",
  owl: "\u{1F989}",
  robot: "\u{1F916}",
  dragon: "\u{1F409}",
};

interface ZoneCardProps {
  zone: ZoneInfo;
  agents: AgentInfo[];
  onClick: (zone: ZoneInfo) => void;
}

export default function ZoneCard({ zone, agents, onClick }: ZoneCardProps) {
  const displayAgents = agents.slice(0, 5);
  const overflow = agents.length - 5;

  return (
    <div
      className={`${styles.zoneCard} ${agents.length > 0 ? styles.zoneActive : ""}`}
      onClick={() => onClick(zone)}
    >
      <div className={styles.zoneCardHeader}>
        <div
          className={styles.zoneIcon}
          style={{ background: zone.color, color: "#fff" }}
        >
          {ZONE_ICONS[zone.id] || <Building size={20} />}
        </div>
        {zone.premium && (
          <Tag color="gold" style={{ margin: 0, fontSize: 11 }}>
            Premium
          </Tag>
        )}
      </div>

      <div className={styles.zoneName}>{zone.name}</div>
      <div className={styles.zoneDescription}>{zone.description}</div>

      <div className={styles.agentCount}>
        {zone.agents_online > 0 && <span className={styles.agentCountDot} />}
        {zone.agents_online} agent{zone.agents_online !== 1 ? "s" : ""} online
      </div>

      {displayAgents.length > 0 && (
        <div className={styles.agentList}>
          {displayAgents.map((agent) => (
            <Tooltip key={agent.id} title={agent.name}>
              <div
                className={styles.agentAvatar}
                style={{
                  background: AVATAR_COLORS[agent.avatar] || "#607D8B",
                }}
              >
                {AVATAR_EMOJI[agent.avatar] || "\u{1F916}"}
              </div>
            </Tooltip>
          ))}
          {overflow > 0 && (
            <div className={styles.agentBubble}>+{overflow}</div>
          )}
        </div>
      )}
    </div>
  );
}
