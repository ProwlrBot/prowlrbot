import { createContext, useContext, useEffect, useState, useCallback } from "react";
import type { ReactNode } from "react";
import {
  fetchMe,
  getStoredToken,
  clearStoredToken,
  setStoredToken,
  type AuthUser,
} from "../api/modules/auth";

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  isAuthenticated: boolean;
  /** Call after a successful login/register to refresh user state. */
  onLogin: (token: string) => void;
  /** Clear token and user state. */
  onLogout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async () => {
    const token = getStoredToken();
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const me = await fetchMe();
      setUser(me);
    } catch {
      // Token expired or invalid — clear it
      clearStoredToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  // Load user on mount
  useEffect(() => {
    loadUser();
  }, [loadUser]);

  // Handle OAuth callback — token arrives in URL hash
  useEffect(() => {
    const hash = window.location.hash;
    const match = hash.match(/[?&]token=([^&]+)/);
    if (match) {
      const token = decodeURIComponent(match[1]);
      setStoredToken(token);
      // Clean URL
      window.history.replaceState(null, "", window.location.pathname);
      loadUser();
    }
  }, [loadUser]);

  const onLogin = useCallback(
    (token: string) => {
      setStoredToken(token);
      loadUser();
    },
    [loadUser],
  );

  const onLogout = useCallback(() => {
    clearStoredToken();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user,
        onLogin,
        onLogout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
