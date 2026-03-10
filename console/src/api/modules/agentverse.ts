import { request } from "../request";

export function listOnlineAgents() { return request("/agentverse/agents"); }
export function getAgentverseAgent(id: string) { return request(`/agentverse/agents/${id}`); }
export function registerAgent(data: any) { return request("/agentverse/agents", { method: "POST", body: JSON.stringify(data) }); }
export function moveAgent(id: string, zone: string) { return request(`/agentverse/agents/${id}/move`, { method: "PUT", body: JSON.stringify(zone) }); }
export function listZones() { return request("/agentverse/zones"); }
export function listGuilds() { return request("/agentverse/guilds"); }
export function createGuild(data: any) { return request("/agentverse/guilds", { method: "POST", body: JSON.stringify(data) }); }
export function createBattle(data: any) { return request("/agentverse/battles", { method: "POST", body: JSON.stringify(data) }); }
