import { createContext, createElement, useContext, useEffect, useMemo, useState } from "react";
import { api, authStore } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [tokens, setTokens] = useState(() => authStore.read());
  const [user, setUser] = useState(tokens?.user || null);
  const [booting, setBooting] = useState(Boolean(tokens?.access_token));

  useEffect(() => {
    let alive = true;
    async function boot() {
      if (!tokens?.access_token) {
        setBooting(false);
        return;
      }
      try {
        const profile = await api.me();
        if (alive) setUser(profile);
      } catch {
        authStore.clear();
        if (alive) {
          setTokens(null);
          setUser(null);
        }
      } finally {
        if (alive) setBooting(false);
      }
    }
    boot();
    return () => { alive = false; };
  }, []);

  useEffect(() => {
    const theme = user?.preferences?.theme_mode || "system";
    const resolved = theme === "system"
      ? (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
      : theme;
    document.documentElement.dataset.theme = resolved;
  }, [user?.preferences?.theme_mode]);

  async function signIn(email, password) {
    const result = await api.login({ email, password });
    authStore.save(result.tokens);
    setTokens(result.tokens);
    setUser(result.user);
    return result.user;
  }

  async function register(payload) {
    const result = await api.register(payload);
    authStore.save(result.tokens);
    setTokens(result.tokens);
    setUser(result.user);
    return result.user;
  }

  async function signOut() {
    const refreshToken = authStore.read()?.refresh_token;
    if (refreshToken) await api.logout(refreshToken).catch(() => null);
    authStore.clear();
    setTokens(null);
    setUser(null);
  }

  const value = useMemo(() => ({
    booting,
    isAuthenticated: Boolean(tokens?.access_token),
    user,
    setUser,
    signIn,
    register,
    signOut,
  }), [booting, tokens, user]);

  return createElement(AuthContext.Provider, { value }, children);
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}
