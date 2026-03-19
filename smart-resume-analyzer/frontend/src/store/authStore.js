import { create } from 'zustand'

const safeGet = (key) => { try { return localStorage.getItem(key) } catch { return null } }
const safeSet = (key, val) => { try { localStorage.setItem(key, val) } catch { } }
const safeRemove = (key) => { try { localStorage.removeItem(key) } catch { } }

export const useAuthStore = create((set) => ({
    user: (() => { try { const u = safeGet('user'); return u ? JSON.parse(u) : null } catch { return null } })(),
    accessToken: safeGet('access_token'),
    isAuthenticated: !!safeGet('access_token'),
    isLoading: false,

    login: (token, user) => {
        safeSet('access_token', token)
        safeSet('user', JSON.stringify(user))
        set({ accessToken: token, user, isAuthenticated: true })
    },

    logout: () => {
        safeRemove('access_token')
        safeRemove('user')
        set({ accessToken: null, user: null, isAuthenticated: false })
    },

    setUser: (user) => set({ user }),
    setLoading: (isLoading) => set({ isLoading }),
}))
