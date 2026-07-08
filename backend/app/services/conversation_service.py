"""会话服务 - 会话CRUD"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User


async def list_conversations(
    db: AsyncSession, user: User, page: int = 1, page_size: int = 20
) -> tuple[list[dict], int]:
    """获取用户会话列表（分页），按更新时间倒序"""
    # 统计总数
    count_query = select(func.count()).select_from(Conversation).where(Conversation.user_id == user.id)
    total = (await db.execute(count_query)).scalar() or 0

    # 分页查询，同时用子查询获取消息数量
    query = (
        select(Conversation)
        .where(Conversation.user_id == user.id)
        .order_by(Conversation.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    conversations = result.scalars().all()

    # 构建返回数据，用 count 查询获取每个会话的消息数量
    items = []
    for conv in conversations:
        count_result = await db.execute(
            select(func.count()).select_from(Message).where(Message.conversation_id == conv.id)
        )
        msg_count = count_result.scalar() or 0
        items.append({
            "id": conv.id,
            "title": conv.title,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
            "message_count": msg_count,
        })

    return items, total


async def create_conversation(db: AsyncSession, user: User, title: str = "新对话") -> Conversation:
    """创建新会话"""
    conversation = Conversation(user_id=user.id, title=title)
    db.add(conversation)
    await db.flush()
    await db.refresh(conversation)
    return conversation


async def get_conversation(db: AsyncSession, conversation_id: int, user: User) -> Conversation:
    """获取会话详情（不含消息列表，消息需要单独查询）"""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if conversation is None:
        raise NotFoundException("会话不存在")

    if conversation.user_id != user.id and not user.is_admin:
        raise ForbiddenException("无权访问该会话")

    return conversation


async def get_conversation_messages(db: AsyncSession, conversation_id: int) -> list[Message]:
    """获取会话的消息列表（按时间正序）"""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    return list(result.scalars().all())


async def update_conversation_title(db: AsyncSession, conversation_id: int, user: User, title: str) -> Conversation:
    """更新会话标题"""
    conversation = await get_conversation(db, conversation_id, user)
    conversation.title = title
    db.add(conversation)
    await db.flush()
    await db.refresh(conversation)
    return conversation


async def delete_conversation(db: AsyncSession, conversation_id: int, user: User) -> None:
    """删除会话（级联删除消息）"""
    conversation = await get_conversation(db, conversation_id, user)
    await db.delete(conversation)
    await db.flush()


async def get_conversation_message_count(db: AsyncSession, conversation_id: int) -> int:
    """获取会话的消息数量"""
    result = await db.execute(
        select(func.count()).select_from(Message).where(Message.conversation_id == conversation_id)
    )
    return result.scalar() or 0
