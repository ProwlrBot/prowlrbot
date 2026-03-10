import { request } from "../request";

export function listExternalAgents() { return request("/external-agents/agents"); }
export function registerExternalAgent(data: any) { return request("/external-agents/agents", { method: "POST", body: JSON.stringify(data) }); }
export function deleteExternalAgent(id: string) { return request(`/external-agents/agents/${id}`, { method: "DELETE" }); }
export function checkAgentHealth(id: string) { return request(`/external-agents/agents/${id}/health`); }
export function listExternalTasks(agentId?: string) {
  const params = agentId ? `?agent_id=${agentId}` : "";
  return request(`/external-agents/tasks${params}`);
}
export function executeTask(taskId: string) { return request(`/external-agents/tasks/${taskId}/execute`, { method: "POST" }); }
