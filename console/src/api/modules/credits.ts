import { request } from "../request";

export function getCreditBalance(userId = "default") {
  return request(`/marketplace/credits/${userId}`);
}

export function getCreditTransactions(userId = "default", limit = 20) {
  return request(`/marketplace/credits/${userId}/transactions?limit=${limit}`);
}

export function getMarketplaceTiers() {
  return request("/marketplace/tiers");
}
