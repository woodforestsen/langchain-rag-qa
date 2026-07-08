"""用户 API"""

from fastapi import APIRouter, Depends

from app.core.deps import get_current_active_user
from app.models.user import User
from app.schemas.auth import UserInfo

router = APIRouter()


@router.get("/me", response_model=UserInfo, summary="获取当前用户信息")
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """获取当前登录用户信息"""
    return UserInfo.model_validate(current_user)
