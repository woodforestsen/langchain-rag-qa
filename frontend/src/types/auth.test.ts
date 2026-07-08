import { describe, it, expect } from 'vitest'
import type { UserInfo, LoginRequest, TokenResponse, ChangePasswordRequest } from './auth'

describe('Auth Types', () => {
  it('LoginRequest 应该包含 username 和 password', () => {
    const login: LoginRequest = { username: 'admin', password: '123456' }
    expect(login.username).toBe('admin')
    expect(login.password).toBe('123456')
    expect(typeof login.username).toBe('string')
    expect(typeof login.password).toBe('string')
  })

  it('TokenResponse 应该包含 access_token 和 token_type', () => {
    const token: TokenResponse = { access_token: 'xxx', token_type: 'bearer' }
    expect(token.token_type).toBe('bearer')
    expect(token.access_token).toBeTruthy()
  })

  it('UserInfo 应该包含用户基本信息', () => {
    const user: UserInfo = {
      id: 1,
      username: 'admin',
      is_admin: true,
      is_active: true,
    }
    expect(user.id).toBe(1)
    expect(user.is_admin).toBe(true)
    expect(user.is_active).toBe(true)
  })

  it('ChangePasswordRequest 应该包含旧密码和新密码', () => {
    const req: ChangePasswordRequest = {
      old_password: 'old',
      new_password: 'newpass123',
    }
    expect(req.new_password.length).toBeGreaterThanOrEqual(6)
  })

  it('UserInfo 普通用户 is_admin 应为 false', () => {
    const user: UserInfo = {
      id: 2,
      username: 'testuser',
      is_admin: false,
      is_active: true,
    }
    expect(user.is_admin).toBe(false)
  })
})
