import { request } from "../request";

const TOKEN_KEY = "prowlrbot-jwt";

// ---------------------------------------------------------------------------
// Token storage
// ---------------------------------------------------------------------------

export function getStoredToken(): string {
  return localStorage.getItem(TOKEN_KEY) || "";
}

export function setStoredToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearStoredToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user_id: string;
  role: string;
}

export interface AuthUser {
  id: string;
  username: string;
  email: string;
  role: string;
  permissions: string[];
  is_active: boolean;
  created_at: number;
  last_login: number;
}

// ---------------------------------------------------------------------------
// API calls
// ---------------------------------------------------------------------------

export async function login(username: string, password: string): Promise<AuthResponse> {
  const resp = await request<AuthResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  setStoredToken(resp.access_token);
  return resp;
}

export async function register(
  username: string,
  password: string,
  email?: string,
): Promise<AuthResponse> {
  const resp = await request<AuthResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ username, password, email: email || "" }),
  });
  setStoredToken(resp.access_token);
  return resp;
}

export async function fetchMe(): Promise<AuthUser> {
  return request<AuthUser>("/auth/me");
}

export async function refreshToken(): Promise<AuthResponse> {
  const resp = await request<AuthResponse>("/auth/refresh", { method: "POST" });
  setStoredToken(resp.access_token);
  return resp;
}

export async function fetchOAuthProviders(): Promise<string[]> {
  const resp = await request<{ providers: string[] }>("/auth/oauth/providers");
  return resp.providers;
}

export function getOAuthStartUrl(provider: string): string {
  const base = window.location.origin;
  return `${base}/api/auth/oauth/${provider}`;
}

export function logout(): void {
  clearStoredToken();
}
