"""认证 API - 注册、登录、修改密码"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserInfo,
)
from app.services.auth_service import change_password, login_user, register_user

router = APIRouter()


@router.post("/register", response_model=UserInfo, summary="用户注册")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """注册新用户（默认注册为普通用户，无管理员权限）"""
    user = await register_user(db, data)
    return UserInfo.model_validate(user)


@router.post("/login", response_model=TokenResponse, summary="用户登录")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户名+密码登录，返回 JWT access token"""
    token = await login_user(db, data.username, data.password)
    return TokenResponse(access_token=token)


@router.post("/change-password", summary="修改密码")
async def change_password_endpoint(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """修改当前登录用户的密码"""
    await change_password(db, current_user, data.old_password, data.new_password)
    return {"message": "密码修改成功"}


@router.get("/me", response_model=UserInfo, summary="获取当前用户信息")
async def get_me(current_user: User = Depends(get_current_active_user)):
    """获取当前登录用户的个人信息"""
    return UserInfo.model_validate(current_user)
