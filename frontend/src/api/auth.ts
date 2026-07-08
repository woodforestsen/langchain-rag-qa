import apiClient from '@/config/api'
import type { LoginRequest, RegisterRequest, TokenResponse, UserInfo, ChangePasswordRequest } from '@/types/auth'

export const authApi = {
  login: (data: LoginRequest) =>
    apiClient.post<TokenResponse>('/auth/login', data),

  register: (data: RegisterRequest) =>
    apiClient.post<UserInfo>('/auth/register', data),

  getMe: () =>
    apiClient.get<UserInfo>('/auth/me'),

  changePassword: (data: ChangePasswordRequest) =>
    apiClient.post('/auth/change-password', data),
}
