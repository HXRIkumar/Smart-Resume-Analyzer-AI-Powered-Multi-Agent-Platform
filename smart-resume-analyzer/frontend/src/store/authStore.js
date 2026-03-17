/**
 * Zustand authentication store with localStorage persistence
 * and automatic token refresh.
 *
 * State: user, accessToken, refreshToken, isAuthenticated, isLoading, error
 * Actions: login, register, googleLogin, logout, setUser, refreshAuth, fetchUser
 *
 * Tokens are persisted to localStorage via zustand/middleware persist.
 * Auto-refresh fires 5 minutes before access token expiry via setTimeout.
 *
 * @module store/authStore
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authAPI } from '../api/auth';

/**
 * Parse JWT token payload without verification (client-side only).
 *
 * @param {string} token - JWT token string.
 * @returns {{ sub: string, exp: number, iat: number, type: string } | null} Decoded payload or null.
 */
function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(
            atob(base64)
                .split('')
                .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
                .join('')
        );
        return JSON.parse(jsonPayload);
    } catch {
        return null;
    }
}

/** @type {ReturnType<typeof setTimeout> | null} */
let refreshTimer = null;

/**
 * Schedule an automatic token refresh 5 minutes before expiry.
 *
 * @param {string} accessToken - Current JWT access token.
 * @param {() => Promise<void>} refreshFn - The refreshAuth action from the store.
 */
function scheduleTokenRefresh(accessToken, refreshFn) {
    // Clear any existing timer
    if (refreshTimer) {
        clearTimeout(refreshTimer);
        refreshTimer = null;
    }

    const payload = parseJwt(accessToken);
    if (!payload?.exp) return;

    const expiresAt = payload.exp * 1000; // ms
    const now = Date.now();
    const fiveMinutes = 5 * 60 * 1000;
    const refreshIn = expiresAt - now - fiveMinutes;

    if (refreshIn > 0) {
        refreshTimer = setTimeout(async () => {
            try {
                await refreshFn();
            } catch {
                // Refresh failed — token is likely expired, user will be redirected
            }
        }, refreshIn);
    }
}

export const useAuthStore = create(
    persist(
        (set, get) => ({
            // ─── State ──────────────────────────────────────────────────
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,

            // ─── Actions ────────────────────────────────────────────────

            /**
             * Login with email/password credentials.
             *
             * @async
             * @param {{ email: string, password: string }} credentials - Login credentials.
             * @throws {Error} On authentication failure.
             */
            login: async (credentials) => {
                set({ isLoading: true, error: null });
                try {
                    const { data } = await authAPI.login(credentials.email, credentials.password);
                    set({
                        accessToken: data.access_token,
                        refreshToken: data.refresh_token,
                        user: data.user,
                        isAuthenticated: true,
                        isLoading: false,
                        error: null,
                    });
                    // Schedule auto-refresh
                    scheduleTokenRefresh(data.access_token, get().refreshAuth);
                } catch (err) {
                    set({
                        error: err.message || 'Login failed',
                        isLoading: false,
                        isAuthenticated: false,
                    });
                    throw err;
                }
            },

            /**
             * Register a new user and auto-login.
             *
             * @async
             * @param {{ email: string, full_name: string, password: string }} userData - Registration data.
             * @throws {Error} On registration failure (e.g., 409 duplicate email).
             */
            register: async (userData) => {
                set({ isLoading: true, error: null });
                try {
                    const { data } = await authAPI.register(userData);
                    set({
                        accessToken: data.access_token,
                        refreshToken: data.refresh_token,
                        user: data.user,
                        isAuthenticated: true,
                        isLoading: false,
                        error: null,
                    });
                    scheduleTokenRefresh(data.access_token, get().refreshAuth);
                } catch (err) {
                    set({
                        error: err.message || 'Registration failed',
                        isLoading: false,
                        isAuthenticated: false,
                    });
                    throw err;
                }
            },

            /**
             * Login with Google OAuth authorization code.
             *
             * @async
             * @param {string} code - Google authorization code.
             * @throws {Error} On Google auth failure.
             */
            googleLogin: async (code) => {
                set({ isLoading: true, error: null });
                try {
                    const { data } = await authAPI.googleLogin(code);
                    set({
                        accessToken: data.access_token,
                        refreshToken: data.refresh_token,
                        user: data.user,
                        isAuthenticated: true,
                        isLoading: false,
                        error: null,
                    });
                    scheduleTokenRefresh(data.access_token, get().refreshAuth);
                } catch (err) {
                    set({
                        error: err.message || 'Google login failed',
                        isLoading: false,
                        isAuthenticated: false,
                    });
                    throw err;
                }
            },

            /**
             * Fetch the current user profile from /auth/me.
             *
             * @async
             */
            fetchUser: async () => {
                try {
                    const { data } = await authAPI.getMe();
                    set({ user: data, isAuthenticated: true });
                } catch {
                    // Token invalid — clear auth state
                    get().logout();
                }
            },

            /**
             * Refresh the access token using the stored refresh token.
             * Schedules the next auto-refresh on success.
             *
             * @async
             */
            refreshAuth: async () => {
                const currentRefreshToken = get().refreshToken;
                if (!currentRefreshToken) {
                    get().logout();
                    return;
                }
                try {
                    const { data } = await authAPI.refreshToken(currentRefreshToken);
                    set({
                        accessToken: data.access_token,
                        refreshToken: data.refresh_token || currentRefreshToken,
                        user: data.user,
                        isAuthenticated: true,
                    });
                    // Schedule next refresh
                    scheduleTokenRefresh(data.access_token, get().refreshAuth);
                } catch {
                    // Refresh token expired — force logout
                    get().logout();
                }
            },

            /**
             * Set the user profile data directly.
             *
             * @param {object} user - User profile data.
             */
            setUser: (user) => {
                set({ user, isAuthenticated: !!user });
            },

            /**
             * Logout — clear all auth state and cancel refresh timer.
             */
            logout: () => {
                if (refreshTimer) {
                    clearTimeout(refreshTimer);
                    refreshTimer = null;
                }
                set({
                    user: null,
                    accessToken: null,
                    refreshToken: null,
                    isAuthenticated: false,
                    error: null,
                    isLoading: false,
                });
            },

            /**
             * Clear the current error message.
             */
            clearError: () => set({ error: null }),
        }),
        {
            name: 'sra-auth',
            partialize: (state) => ({
                accessToken: state.accessToken,
                refreshToken: state.refreshToken,
            }),
            onRehydrate: () => {
                // After rehydration, schedule a refresh if we have a token
                return (state) => {
                    if (state?.accessToken) {
                        state.fetchUser();
                        scheduleTokenRefresh(state.accessToken, state.refreshAuth);
                    }
                };
            },
        }
    )
);
