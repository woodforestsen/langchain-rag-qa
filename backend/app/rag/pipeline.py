"""RAG 管道编排 - 检索 + 组装 + 生成"""

from langchain_core.output_parsers import StrOutputParser

from app.rag.llm_factory import get_llm
from app.rag.prompt_templates import get_rag_prompt
from app.rag.retriever import format_docs_for_context, retrieve_similar_chunks


def build_rag_chain(provider: str | None = None, model: str | None = None):
    """
    构建 RAG 处理链（非流式版本，用于简单调用）
    对于 SSE 流式场景，chat_service 中手动编排管道以更好控制 SSE 事件
    """
    llm = get_llm(provider=provider, model=model, streaming=True)
    prompt = get_rag_prompt()
    return prompt | llm | StrOutputParser()


async def process_rag_query(
    query: str,
    chat_history: list[dict] | None = None,
    provider: str | None = None,
    model: str | None = None,
) -> dict:
    """处理 RAG 查询 - 完整管道（非流式版本）

    Returns:
        dict 包含 answer, sources, context
    """
    # Step 1: 检索相关文档块
    chunks = retrieve_similar_chunks(query)

    # Step 2: 格式化上下文
    context, citations = format_docs_for_context(chunks)

    # Step 3: 格式化对话历史
    chat_history_str = ""
    if chat_history:
        history_parts = []
        for msg in chat_history[-6:]:  # 最近 6 条消息
            role_label = "用户" if msg.get("role") == "user" else "助手"
            history_parts.append(f"{role_label}: {msg.get('content', '')}")
        chat_history_str = "\n".join(history_parts)

    # Step 4: 调用 LLM
    llm = get_llm(provider=provider, model=model, streaming=False)
    prompt = get_rag_prompt()

    chain = prompt | llm | StrOutputParser()
    answer = await chain.ainvoke({
        "context": context or "（知识库中暂无相关信息）",
        "chat_history": chat_history_str or "（无历史对话）",
        "question": query,
    })

    return {
        "answer": answer,
        "sources": citations,
        "context": context,
    }
