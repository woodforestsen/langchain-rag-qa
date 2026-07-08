"""聊天 API - RAG 问答 SSE 流式接口"""

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from app.core.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import ChatRequest
from app.services.chat_service import stream_rag_answer

router = APIRouter()


@router.post("/{conversation_id}", summary="发送消息（SSE流式）")
async def chat_with_rag(
    conversation_id: int,
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """向 AI 发送消息并流式获取 RAG 增强回答

    返回 Server-Sent Events 流:
    - event: searching  → 正在搜索知识库
    - event: thinking   → 正在生成回答
    - event: token      → 回答文本增量
    - event: sources    → 引用的知识库来源列表
    - event: done       → 回答完成
    - event: error      → 错误信息
    """
    # request 中的 conversation_id 用于向后兼容，URL 参数优先
    return StreamingResponse(
        stream_rag_answer(
            db=db,
            conversation_id=conversation_id,
            question=request.question,
            user=current_user,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
        },
    )


@router.get("/{conversation_id}/export", summary="导出对话")
async def export_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """将对话导出为 Markdown 文件下载"""
    from sqlalchemy import select

    from app.models.conversation import Conversation
    from app.models.message import Message

    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conversation = result.scalar_one_or_none()

    if conversation is None or conversation.user_id != current_user.id:
        return PlainTextResponse("会话不存在或无权访问", status_code=404)

    messages_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = messages_result.scalars().all()

    # 构建 Markdown
    from datetime import datetime
    markdown = f"# {conversation.title}\n\n"
    markdown += f"*导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n---\n\n"

    for msg in messages:
        role_label = "用户" if msg.role == "user" else "AI 助手"
        markdown += f"### {role_label}\n\n{msg.content}\n\n"

        if msg.sources:
            markdown += "**参考来源：**\n"
            for source in msg.sources:
                markdown += f"- [{source.get('index', '?')}] **{source.get('document_name', '未知文档')}** (相关度: {source.get('score', 0):.0%})\n"
                markdown += f"  > {source.get('excerpt', '')}\n"
            markdown += "\n"

        markdown += "---\n\n"

    safe_title = conversation.title.replace("/", "_").replace("\\", "_").replace(":", "_")
    return PlainTextResponse(
        content=markdown,
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_title}.md"',
        },
    )
