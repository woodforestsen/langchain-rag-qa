import { describe, it, expect, beforeEach } from 'vitest'
import { useThemeStore } from './themeStore'

describe('useThemeStore', () => {
  beforeEach(() => {
    localStorage.clear()
    useThemeStore.setState({ isDark: false })
  })

  it('初始状态应该是亮色模式', () => {
    expect(useThemeStore.getState().isDark).toBe(false)
  })

  it('toggle 应该切换暗色模式', () => {
    useThemeStore.getState().toggle()
    expect(useThemeStore.getState().isDark).toBe(true)
    expect(localStorage.getItem('theme')).toBe('dark')
  })

  it('toggle 两次应该回到亮色模式', () => {
    useThemeStore.getState().toggle()
    useThemeStore.getState().toggle()
    expect(useThemeStore.getState().isDark).toBe(false)
    expect(localStorage.getItem('theme')).toBe('light')
  })
})
