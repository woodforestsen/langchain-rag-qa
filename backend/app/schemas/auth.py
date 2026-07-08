"""认证相关 Pydantic 模型"""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=1, max_length=100, description="密码")


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码（至少6位）")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码（至少6位）")


class TokenResponse(BaseModel):
    """登录返回的 Token"""
    access_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    """用户基本信息"""
    id: int
    username: str
    is_admin: bool
    is_active: bool

    model_config = {"from_attributes": True}
