export interface UserInfo {
  id: number
  username: string
  is_admin: boolean
  is_active: boolean
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface ChangePasswordRequest {
  old_password: string
  new_password: string
}
