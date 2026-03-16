import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authAPI } from '../api/auth';

export const useAuthStore = create(
    persist(
        (set, get) => ({
            token: null,
            user: null,
            isLoading: false,
            error: null,

            login: async (email, password) => {
                set({ isLoading: true, error: null });
                try {
                    const { data } = await authAPI.login(email, password);
                    set({ token: data.access_token, isLoading: false });
                    // Fetch user profile
                    await get().fetchUser();
                } catch (err) {
                    set({
                        error: err.response?.data?.detail || 'Login failed',
                        isLoading: false,
                    });
                    throw err;
                }
            },

            register: async (email, fullName, password) => {
                set({ isLoading: true, error: null });
                try {
                    await authAPI.register(email, fullName, password);
                    // Auto-login after registration
                    await get().login(email, password);
                } catch (err) {
                    set({
                        error: err.response?.data?.detail || 'Registration failed',
                        isLoading: false,
                    });
                    throw err;
                }
            },

            fetchUser: async () => {
                try {
                    const { data } = await authAPI.getMe();
                    set({ user: data });
                } catch {
                    set({ token: null, user: null });
                }
            },

            logout: () => {
                set({ token: null, user: null, error: null });
            },

            clearError: () => set({ error: null }),
        }),
        {
            name: 'sra-auth',
            partialize: (state) => ({ token: state.token }),
        },
    ),
);
