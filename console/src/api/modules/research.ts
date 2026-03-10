import { request } from "../request";

export function listResearchProjects(status?: string) {
  const params = status ? `?status=${status}` : "";
  return request(`/research/projects${params}`);
}
export function createResearchProject(data: any) { return request("/research/projects", { method: "POST", body: JSON.stringify(data) }); }
export function getResearchProject(id: string) { return request(`/research/projects/${id}`); }
export function analyzeProject(id: string) { return request(`/research/projects/${id}/analyze`, { method: "POST" }); }
export function synthesizeProject(id: string) { return request(`/research/projects/${id}/synthesize`, { method: "POST" }); }
