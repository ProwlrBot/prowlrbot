import { request } from "../request";

export function getLevelInfo(entityId: string) { return request(`/gamification/level/${entityId}`); }
export function getXPHistory(entityId: string) { return request(`/gamification/xp/${entityId}/history`); }
export function getLeaderboard(limit = 20) { return request(`/gamification/leaderboard?limit=${limit}`); }
export function getAchievements(entityId: string) { return request(`/gamification/achievements/${entityId}`); }
export function listAllAchievements() { return request("/gamification/achievements"); }
