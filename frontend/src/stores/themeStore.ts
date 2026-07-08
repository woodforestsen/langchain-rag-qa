import { create } from 'zustand'

interface ThemeState {
  isDark: boolean
  toggle: () => void
}

export const useThemeStore = create<ThemeState>((set) => ({
  isDark: localStorage.getItem('theme') === 'dark',
  toggle: () =>
    set((state) => {
      const newDark = !state.isDark
      localStorage.setItem('theme', newDark ? 'dark' : 'light')
      return { isDark: newDark }
    }),
}))
