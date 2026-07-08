"""聊天服务 - RAG 问答核心 + SSE 流式处理 + 查询重写 + Redis 缓存"""

import asyncio
import json
from typing import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.rag.citations import parse_sources_from_llm_response
from app.rag.llm_factory import get_llm
from app.rag.prompt_templates import get_query_rewrite_prompt, get_rag_prompt
from app.rag.retriever import format_docs_for_context, retrieve_similar_chunks


async def load_chat_history(db: AsyncSession, conversation_id: int, limit: int = 6) -> list[dict]:
    """加载最近的对话历史"""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    # 反转为时间顺序
    messages = list(reversed(messages))
    return [{"role": m.role, "content": m.content} for m in messages]


async def save_message(
    db: AsyncSession,
    conversation_id: int,
    role: str,
    content: str,
    sources: list[dict] | None = None,
) -> Message:
    """保存消息到数据库"""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        sources=sources,
    )
    db.add(message)
    await db.flush()
    await db.refresh(message)
    return message


async def generate_auto_title(question: str) -> str:
    """根据首条问题自动生成会话标题"""
    # 清理并截断问题作为标题
    cleaned = question.strip().replace("\n", " ")
    if len(cleaned) > 30:
        return cleaned[:30] + "..."
    return cleaned


async def update_conversation_title(db: AsyncSession, conversation_id: int, title: str) -> None:
    """更新会话标题（仅当标题仍为默认时）"""
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conv = result.scalar_one_or_none()
    if conv and (conv.title == "新对话" or not conv.title or conv.title == "新的对话"):
        conv.title = title
        db.add(conv)
        await db.flush()


async def stream_rag_answer(
    db: AsyncSession,
    conversation_id: int,
    question: str,
    user: User,
    provider: str | None = None,
    model: str | None = None,
) -> AsyncGenerator[str, None]:
    """SSE 流式 RAG 回答生成器

    产生结构化 SSE 事件:
    - event: rewriting → 正在重写查询
    - event: searching → 正在搜索知识库
    - event: thinking  → 正在生成回答
    - event: token     → 文本增量
    - event: sources   → 引用的知识库来源
    - event: done      → 完成标记
    - event: error     → 错误信息
    """
    try:
        # Step 0: 验证会话归属
        result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
        conversation = result.scalar_one_or_none()
        if conversation is None or conversation.user_id != user.id:
            yield f"data: {json.dumps({'event': 'error', 'data': '会话不存在或无权访问'}, ensure_ascii=False)}\n\n"
            return

        # Step 1: 加载对话历史
        chat_history = await load_chat_history(db, conversation_id, limit=6)
        chat_history_str = ""
        if chat_history:
            parts = []
            for msg in chat_history:
                role_label = "用户" if msg["role"] == "user" else "助手"
                parts.append(f"{role_label}: {msg['content']}")
            chat_history_str = "\n".join(parts)

        # Step 2: 保存用户消息
        user_message = await save_message(db, conversation_id, "user", question)

        # Step 3: 自动更新会话标题（首条消息时）
        await update_conversation_title(db, conversation_id, await generate_auto_title(question))

        # Step 4: 直接使用原始问题检索（查询重写后续可选加回）
        rewritten_question = question

        # Step 5: 检索相关文档
        yield f"data: {json.dumps({'event': 'searching', 'data': '正在搜索知识库...'}, ensure_ascii=False)}\n\n"

        chunks = None
        try:
            from app.db.redis_client import get_cached_query_result
            chunks = await get_cached_query_result(rewritten_question)
        except Exception:
            pass

        if chunks is None:
            try:
                chunks = retrieve_similar_chunks(rewritten_question, similarity_threshold=0.55)
            except Exception as e:
                yield f"data: {json.dumps({'event': 'error', 'data': f'检索失败: {str(e)}'}, ensure_ascii=False)}\n\n"
                return

        context_text, citations = format_docs_for_context(chunks)

        # Step 6: LLM 流式生成
        yield f"data: {json.dumps({'event': 'thinking', 'data': '正在生成回答...'}, ensure_ascii=False)}\n\n"

        try:
            llm = get_llm(provider=provider, model=model, streaming=True)
        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'data': f'创建LLM失败: {str(e)}'}, ensure_ascii=False)}\n\n"
            return

        prompt = get_rag_prompt()
        chain = prompt | llm

        full_response = ""
        async for chunk in chain.astream({
            "context": context_text or "（知识库中暂无相关信息）",
            "chat_history": chat_history_str or "（无历史对话）",
            "question": rewritten_question,
        }):
            if hasattr(chunk, "content"):
                token = chunk.content
            else:
                token = str(chunk)

            if token:
                full_response += token
                yield f"data: {json.dumps({'event': 'token', 'data': token}, ensure_ascii=False)}\n\n"

        # Step 7: 解析引用来源
        used_sources = parse_sources_from_llm_response(full_response, citations)

        # Step 8: 保存 AI 回答
        assistant_message = await save_message(
            db, conversation_id, "assistant", full_response, sources=used_sources
        )

        # Step 9: 更新会话时间
        conversation.updated_at = assistant_message.created_at
        db.add(conversation)
        await db.flush()

        # Step 10: 发送引用来源和完成事件
        yield f"data: {json.dumps({'event': 'sources', 'data': used_sources}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'event': 'done', 'data': {'message_id': assistant_message.id, 'conversation_id': conversation_id}}, ensure_ascii=False)}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'event': 'error', 'data': str(e)}, ensure_ascii=False)}\n\n"
