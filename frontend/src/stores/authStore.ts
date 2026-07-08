import { create } from 'zustand'
import type { UserInfo } from '@/types/auth'

interface AuthState {
  user: UserInfo | null
  token: string | null
  isAuthenticated: boolean
  isAdmin: boolean

  login: (token: string, user: UserInfo) => void
  logout: () => void
  setUser: (user: UserInfo) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  token: localStorage.getItem('access_token'),
  isAuthenticated: !!localStorage.getItem('access_token'),
  isAdmin: JSON.parse(localStorage.getItem('user') || 'null')?.is_admin || false,

  login: (token: string, user: UserInfo) => {
    localStorage.setItem('access_token', token)
    localStorage.setItem('user', JSON.stringify(user))
    set({
      token,
      user,
      isAuthenticated: true,
      isAdmin: user.is_admin,
    })
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    set({
      token: null,
      user: null,
      isAuthenticated: false,
      isAdmin: false,
    })
  },

  setUser: (user: UserInfo) => {
    localStorage.setItem('user', JSON.stringify(user))
    set({ user, isAdmin: user.is_admin })
  },
}))
