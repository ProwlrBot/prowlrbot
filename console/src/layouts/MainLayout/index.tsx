import React from "react";
import { Layout } from "antd";
import { useEffect, useState } from "react";
import { Routes, Route, useLocation, useNavigate } from "react-router-dom";
import api from "../../api";
import type { ConsolePluginManifest } from "../../api";
import Sidebar from "../Sidebar";
import Header from "../Header";
import ConsoleCronBubble from "../../components/ConsoleCronBubble";
import Dashboard from "../../pages/Dashboard";
import Chat from "../../pages/Chat";
import ChannelsPage from "../../pages/Control/Channels";
import SessionsPage from "../../pages/Control/Sessions";
import CronJobsPage from "../../pages/Control/CronJobs";
import AgentConfigPage from "../../pages/Agent/Config";
import SkillsPage from "../../pages/Agent/Skills";
import WorkspacePage from "../../pages/Agent/Workspace";
import MCPPage from "../../pages/Agent/MCP";
import ModelsPage from "../../pages/Settings/Models";
import EnvironmentsPage from "../../pages/Settings/Environments";
import MarketplacePage from "../../pages/Marketplace";
import ListingDetailPage from "../../pages/Marketplace/ListingDetail";
import AgentVersePage from "../../pages/AgentVerse";
import SecurityPage from "../../pages/Settings/Security";
import PrivacyPage from "../../pages/Settings/Privacy";
import AppearancePage from "../../pages/Settings/Appearance";
import WarRoomPage from "../../pages/WarRoom";
import MonitoringPage from "../../pages/Monitoring";
import MemoryPage from "../../pages/Memory";
import SwarmPage from "../../pages/Swarm";
import TeamBuilderPage from "../../pages/Agent/TeamBuilder";
import CreditsPage from "../../pages/Credits";
import StatusLine from "../../components/StatusLine";
import ReplayPage from "../../pages/Replay";
import TerminalPage from "../../pages/Terminal";
import AnalyticsPage from "../../pages/Analytics";
import HardwareAdvisorPage from "../../pages/HardwareAdvisor";
import LeaderboardPage from "../../pages/Leaderboard";
import UIGallery from "../../pages/UIGallery";

const { Content } = Layout;

const STATIC_PATH_TO_KEY: Record<string, string> = {
  "/dashboard": "dashboard",
  "/chat": "chat",
  "/channels": "channels",
  "/sessions": "sessions",
  "/cron-jobs": "cron-jobs",
  "/skills": "skills",
  "/mcp": "mcp",
  "/workspace": "workspace",
  "/models": "models",
  "/environments": "environments",
  "/agent-config": "agent-config",
  "/marketplace": "marketplace",
  "/agentverse": "agentverse",
  "/security": "security",
  "/privacy": "privacy",
  "/appearance": "appearance",
  "/monitoring": "monitoring",
  "/memory": "memory",
  "/swarm": "swarm",
  "/team-builder": "team-builder",
  "/credits": "credits",
  "/replay": "replay",
  "/terminal": "terminal",
  "/analytics": "analytics",
  "/hardware": "hardware",
  "/leaderboard": "leaderboard",
  "/ui-gallery": "ui-gallery",
};

/** Built-in entry keys map to console components (for plugin-driven routes). */
const BUILTIN_PLUGIN_ENTRIES: Record<string, React.ComponentType> = {
  warroom: WarRoomPage,
  monitoring: MonitoringPage,
};

function PluginFrame({ url }: { url: string }) {
  return (
    <iframe
      title="Plugin"
      src={url}
      style={{ width: "100%", height: "100%", minHeight: "calc(100vh - 120px)", border: 0 }}
    />
  );
}

export default function MainLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const currentPath = location.pathname;
  const [plugins, setPlugins] = useState<ConsolePluginManifest[]>([]);

  useEffect(() => {
    api.getPlugins().then(setPlugins).catch(() => setPlugins([]));
  }, []);

  const pathToKey: Record<string, string> = {
    ...STATIC_PATH_TO_KEY,
    ...Object.fromEntries(
      plugins.map((p) => [p.path, p.path.replace(/^\//, "").replace(/\//g, "-")])
    ),
  };
  const selectedKey = pathToKey[currentPath] || "dashboard";

  useEffect(() => {
    if (currentPath === "/") {
      navigate("/dashboard", { replace: true });
    }
  }, [currentPath, navigate]);

  return (
    <Layout style={{ height: "100vh" }}>
      <Sidebar selectedKey={selectedKey} plugins={plugins} />
      <Layout>
        <Header selectedKey={selectedKey} />
        <Content className="page-container">
          <ConsoleCronBubble />
          <div className="page-content">
            <Routes>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/chat" element={<Chat />} />
              <Route path="/channels" element={<ChannelsPage />} />
              <Route path="/sessions" element={<SessionsPage />} />
              <Route path="/cron-jobs" element={<CronJobsPage />} />
              <Route path="/skills" element={<SkillsPage />} />
              <Route path="/mcp" element={<MCPPage />} />
              <Route path="/workspace" element={<WorkspacePage />} />
              <Route path="/models" element={<ModelsPage />} />
              <Route path="/environments" element={<EnvironmentsPage />} />
              <Route path="/agent-config" element={<AgentConfigPage />} />
              <Route path="/marketplace" element={<MarketplacePage />} />
              <Route path="/marketplace/:id" element={<ListingDetailPage />} />
              <Route path="/agentverse" element={<AgentVersePage />} />
              <Route path="/security" element={<SecurityPage />} />
              <Route path="/privacy" element={<PrivacyPage />} />
              <Route path="/appearance" element={<AppearancePage />} />
              {plugins.length > 0
                ? plugins.map((p) => {
                    const Component =
                      p.entry.startsWith("http") || p.entry.startsWith("/")
                        ? () => <PluginFrame url={p.entry} />
                        : BUILTIN_PLUGIN_ENTRIES[p.entry];
                    return Component ? (
                      <Route
                        key={p.path}
                        path={p.path}
                        element={React.createElement(Component)}
                      />
                    ) : null;
                  })
                : (
                    <>
                      <Route path="/warroom" element={<WarRoomPage />} />
                      <Route path="/monitoring" element={<MonitoringPage />} />
                    </>
                  )}
              <Route path="/memory" element={<MemoryPage />} />
              <Route path="/swarm" element={<SwarmPage />} />
              <Route path="/team-builder" element={<TeamBuilderPage />} />
              <Route path="/credits" element={<CreditsPage />} />
              <Route path="/replay" element={<ReplayPage />} />
              <Route path="/terminal" element={<TerminalPage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/hardware" element={<HardwareAdvisorPage />} />
              <Route path="/leaderboard" element={<LeaderboardPage />} />
              <Route path="/ui-gallery" element={<UIGallery />} />
              <Route path="/" element={<Dashboard />} />
            </Routes>
          </div>
        </Content>
        <StatusLine />
      </Layout>
    </Layout>
  );
}
