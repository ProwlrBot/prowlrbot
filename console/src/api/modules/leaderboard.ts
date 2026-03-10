import { request } from "../request";

export function getModelRankings(category?: string) {
  const params = category ? `?category=${category}` : "";
  return request(`/leaderboard/rankings${params}`);
}
export function getModelHistory(model: string) { return request(`/leaderboard/model/${model}/history`); }
export function getLeaderboardCategories() { return request("/leaderboard/categories"); }
