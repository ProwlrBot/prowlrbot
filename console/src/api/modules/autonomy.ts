import { request } from "../request";

export function getPolicy(agentId: string) { return request(`/autonomy/policies/${agentId}`); }
export function setPolicy(agentId: string, data: any) { return request(`/autonomy/policies/${agentId}`, { method: "PUT", body: JSON.stringify(data) }); }
export function listPolicies() { return request("/autonomy/policies"); }
export function evaluateAction(data: any) { return request("/autonomy/evaluate", { method: "POST", body: JSON.stringify(data) }); }
export function listEscalations(agentId: string) { return request(`/autonomy/escalations/${agentId}`); }
