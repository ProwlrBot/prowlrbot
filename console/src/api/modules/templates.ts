import { request } from "../request";

export function listTemplates(category?: string) {
  const params = category ? `?category=${category}` : "";
  return request(`/templates${params}`);
}
export function getTemplate(id: string) { return request(`/templates/${id}`); }
export function searchTemplates(query: string) { return request(`/templates/search?query=${query}`); }
export function downloadTemplate(id: string) { return request(`/templates/${id}/download`, { method: "POST" }); }
