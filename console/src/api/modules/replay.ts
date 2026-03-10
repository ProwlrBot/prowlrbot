import { request } from "../request";

export function listReplaySessions(limit = 50) { return request(`/replay/sessions?limit=${limit}`); }
export function getReplaySession(id: string) { return request(`/replay/${id}`); }
export function getReplayEvents(id: string, startMs = 0, endMs = 0) {
  return request(`/replay/${id}/events?start_ms=${startMs}&end_ms=${endMs}`);
}
export function deleteReplaySession(id: string) { return request(`/replay/${id}`, { method: "DELETE" }); }
