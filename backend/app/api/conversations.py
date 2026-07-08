"""会话 API - 会话 CRUD"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.conversation import (
    ConversationCreate,
    ConversationDetail,
    ConversationListResponse,
    ConversationResponse,
    ConversationUpdate,
)
from app.services.conversation_service import (
    create_conversation,
    delete_conversation,
    get_conversation,
    get_conversation_messages,
    list_conversations,
    update_conversation_title,
)

router = APIRouter()


@router.get("", response_model=ConversationListResponse, summary="获取会话列表")
async def list_user_conversations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的会话列表，按更新时间倒序排列"""
    items, total = await list_conversations(db, current_user, page, page_size)

    return ConversationListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=ConversationResponse, summary="创建新会话")
async def create_new_conversation(
    data: ConversationCreate = ConversationCreate(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """创建新的空会话，默认标题为'新对话'"""
    conv = await create_conversation(db, current_user, data.title)
    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=0,
    )


@router.get("/{conversation_id}", response_model=ConversationDetail, summary="获取会话详情")
async def get_conversation_detail(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取会话详情，包含消息列表"""
    conversation = await get_conversation(db, conversation_id, current_user)
    messages = await get_conversation_messages(db, conversation_id)

    messages_data = []
    for msg in messages:
        messages_data.append({
            "id": msg.id,
            "conversation_id": msg.conversation_id,
            "role": msg.role,
            "content": msg.content,
            "sources": msg.sources,
            "created_at": msg.created_at.isoformat() if msg.created_at else "",
        })

    return ConversationDetail(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        message_count=len(messages),
        messages=messages_data,
    )


@router.patch("/{conversation_id}", response_model=ConversationResponse, summary="更新会话标题")
async def update_conversation(
    conversation_id: int,
    data: ConversationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """修改会话标题"""
    conv = await update_conversation_title(db, conversation_id, current_user, data.title)
    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=len(conv.messages),
    )


@router.delete("/{conversation_id}", summary="删除会话")
async def remove_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """删除会话及其所有消息"""
    await delete_conversation(db, conversation_id, current_user)
    return {"message": "会话已删除"}
