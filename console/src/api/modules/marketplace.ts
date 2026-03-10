import { request } from "../request";

export function listMarketplaceListings(query?: string, category?: string, limit = 20) {
  const params = new URLSearchParams();
  if (query) params.set("query", query);
  if (category) params.set("category", category);
  params.set("limit", String(limit));
  return request(`/marketplace/listings?${params}`);
}
export function getMarketplaceListing(id: string) { return request(`/marketplace/listings/${id}`); }
export function publishListing(data: any) { return request("/marketplace/listings", { method: "POST", body: JSON.stringify(data) }); }
export function getPopularListings() { return request("/marketplace/popular"); }
export function getTopRatedListings() { return request("/marketplace/top-rated"); }
export function getMarketplaceCategories() { return request("/marketplace/categories"); }
export function installListing(id: string) { return request(`/marketplace/listings/${id}/install`, { method: "POST" }); }
export function getListingReviews(id: string) { return request(`/marketplace/listings/${id}/reviews`); }
export function addListingReview(id: string, data: any) { return request(`/marketplace/listings/${id}/reviews`, { method: "POST", body: JSON.stringify(data) }); }
