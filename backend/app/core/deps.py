"""FastAPI 依赖注入 - 认证与授权"""

from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User


async def get_current_user(
    authorization: str = Header(None, description="Bearer {token}"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """从 JWT token 解析当前登录用户"""
    if not authorization:
        raise UnauthorizedException("请先登录")

    if not authorization.startswith("Bearer "):
        raise UnauthorizedException("认证格式错误，需要 Bearer token")

    token = authorization[7:]  # 去掉 "Bearer " 前缀
    payload = decode_access_token(token)

    if payload is None:
        raise UnauthorizedException("token 已过期或无效，请重新登录")

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("token 中缺少用户标识")

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise UnauthorizedException("用户不存在")

    if not user.is_active:
        raise ForbiddenException("用户已被禁用")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前活跃用户"""
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """要求管理员权限"""
    if not current_user.is_admin:
        raise ForbiddenException("需要管理员权限才能执行此操作")
    return current_user
