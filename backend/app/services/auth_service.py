"""认证服务 - 注册、登录、密码修改"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import RegisterRequest


async def register_user(db: AsyncSession, data: RegisterRequest) -> User:
    """注册新用户"""
    if not settings.ALLOW_REGISTRATION:
        raise UnauthorizedException("当前不允许新用户注册")

    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise ConflictException(f"用户名 '{data.username}' 已被占用")

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        is_admin=False,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def login_user(db: AsyncSession, username: str, password: str) -> str:
    """用户登录，返回 JWT token"""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if user is None:
        raise UnauthorizedException("用户名或密码错误")

    if not verify_password(password, user.password_hash):
        raise UnauthorizedException("用户名或密码错误")

    if not user.is_active:
        raise UnauthorizedException("该账号已被禁用")

    token = create_access_token(data={"sub": str(user.id), "username": user.username})
    return token


async def change_password(db: AsyncSession, user: User, old_password: str, new_password: str) -> None:
    """修改用户密码"""
    if not verify_password(old_password, user.password_hash):
        raise UnauthorizedException("旧密码不正确")

    user.password_hash = hash_password(new_password)
    db.add(user)
    await db.flush()
