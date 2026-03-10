import { request } from "../request";

export function listNotifications(unreadOnly = false, limit = 50) {
  return request(`/notifications?unread_only=${unreadOnly}&limit=${limit}`);
}
export function getNotificationStats() { return request("/notifications/stats"); }
export function markNotificationRead(id: string) { return request(`/notifications/${id}/read`, { method: "PUT" }); }
export function markAllRead() { return request("/notifications/read-all", { method: "PUT" }); }
export function dismissNotification(id: string) { return request(`/notifications/${id}`, { method: "DELETE" }); }
