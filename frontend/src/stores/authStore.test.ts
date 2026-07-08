import { describe, it, expect, beforeEach } from 'vitest'
import { useAuthStore } from './authStore'

describe('useAuthStore', () => {
  beforeEach(() => {
    // 清空 localStorage 和 store
    localStorage.clear()
    useAuthStore.setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isAdmin: false,
    })
  })

  it('初始状态应该是未登录', () => {
    const state = useAuthStore.getState()
    expect(state.isAuthenticated).toBe(false)
    expect(state.user).toBeNull()
    expect(state.token).toBeNull()
    expect(state.isAdmin).toBe(false)
  })

  it('login 后应该设置认证状态', () => {
    const user = { id: 1, username: 'admin', is_admin: true, is_active: true }
    useAuthStore.getState().login('test-token-xxx', user)

    const state = useAuthStore.getState()
    expect(state.isAuthenticated).toBe(true)
    expect(state.token).toBe('test-token-xxx')
    expect(state.user?.username).toBe('admin')
    expect(state.isAdmin).toBe(true)
  })

  it('login 应该保存 token 到 localStorage', () => {
    const user = { id: 1, username: 'admin', is_admin: true, is_active: true }
    useAuthStore.getState().login('my-token', user)

    expect(localStorage.getItem('access_token')).toBe('my-token')
    expect(JSON.parse(localStorage.getItem('user')!)).toEqual(user)
  })

  it('logout 后应该清除认证状态', () => {
    const user = { id: 1, username: 'admin', is_admin: true, is_active: true }
    useAuthStore.getState().login('token', user)
    useAuthStore.getState().logout()

    const state = useAuthStore.getState()
    expect(state.isAuthenticated).toBe(false)
    expect(state.user).toBeNull()
    expect(state.token).toBeNull()
    expect(state.isAdmin).toBe(false)
  })

  it('logout 应该清除 localStorage', () => {
    const user = { id: 1, username: 'admin', is_admin: true, is_active: true }
    useAuthStore.getState().login('token', user)
    useAuthStore.getState().logout()

    expect(localStorage.getItem('access_token')).toBeNull()
    expect(localStorage.getItem('user')).toBeNull()
  })

  it('setUser 应该更新用户信息', () => {
    const user = { id: 2, username: 'testuser', is_admin: false, is_active: true }
    useAuthStore.getState().setUser(user)

    const state = useAuthStore.getState()
    expect(state.user?.username).toBe('testuser')
    expect(state.isAdmin).toBe(false)
  })

  it('普通用户登录后 isAdmin 应该为 false', () => {
    const user = { id: 2, username: 'user', is_admin: false, is_active: true }
    useAuthStore.getState().login('token', user)

    expect(useAuthStore.getState().isAdmin).toBe(false)
  })
})
