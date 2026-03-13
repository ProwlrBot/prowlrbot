declare const BASE_URL: string;
declare const TOKEN: string;

/**
 * Get the full API URL with /api prefix
 * @param path - API path (e.g., "/models", "/skills")
 * @returns Full API URL (e.g., "http://localhost:8088/api/models" or "/api/models")
 */
export function getApiUrl(path: string): string {
  const base = BASE_URL || "";
  const apiPrefix = "/api";
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${base}${apiPrefix}${normalizedPath}`;
}

/**
 * Get the API token.
 *
 * Checks for a JWT in localStorage first (set after login), then falls back
 * to the build-time TOKEN constant for legacy API-token auth.
 */
export function getApiToken(): string {
  const jwt = localStorage.getItem("prowlrbot-jwt");
  if (jwt) return jwt;
  return typeof TOKEN !== "undefined" ? TOKEN : "";
}
