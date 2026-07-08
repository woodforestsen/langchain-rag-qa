"""检索器 - 向量相似度搜索 + MMR 多样性优化"""

from langchain_core.documents import Document

from app.config import settings
from app.rag.embeddings import get_embeddings
from app.rag.vector_store import get_global_collection


def retrieve_similar_chunks(
    query: str,
    top_k: int | None = None,
    similarity_threshold: float = 0.4,
) -> list[dict]:
    """检索与查询最相似的文档块

    Args:
        query: 查询文本
        top_k: 返回的块数
        similarity_threshold: 相似度阈值，低于此值的块将被过滤

    Returns:
        包含 content, metadata, score 的文档列表
    """
    top_k = top_k or settings.RETRIEVAL_TOP_K
    embeddings = get_embeddings()
    collection = get_global_collection()

    # 生成查询向量
    query_embedding = embeddings.embed_query(query)

    # ChromaDB 相似度搜索（cosine 距离转相似度）
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k * 2,  # 多取一些用于过滤和重排
        include=["documents", "metadatas", "distances"],
    )

    if not results["ids"] or not results["ids"][0]:
        return []

    chunks = []
    for i in range(len(results["ids"][0])):
        distance = results["distances"][0][i] if "distances" in results else 0
        # ChromaDB 的 cosine 距离转相似度: similarity = 1 - distance/2
        similarity = 1.0 - (distance / 2.0) if distance else 1.0

        if similarity < similarity_threshold:
            continue

        chunks.append({
            "content": results["documents"][0][i],
            "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
            "score": round(similarity, 4),
        })

    # 按相似度降序排序，取 top_k
    chunks.sort(key=lambda x: x["score"], reverse=True)
    return chunks[:top_k]


def format_docs_for_context(chunks: list[dict]) -> tuple[str, list[dict]]:
    """将检索到的文档块格式化为 LLM 上下文

    Returns:
        (formatted_context, citations): 格式化后的上下文字符串和引用信息列表
    """
    context_parts = []
    citations = []

    for i, chunk in enumerate(chunks):
        source_label = i + 1
        metadata = chunk.get("metadata", {})
        doc_name = metadata.get("filename", metadata.get("source", "未知文档"))

        context_parts.append(
            f"[来源{source_label}] 文档: {doc_name}\n"
            f"{chunk['content']}\n"
        )

        citations.append({
            "index": source_label,
            "document_name": doc_name,
            "chunk_id": metadata.get("chunk_id", 0),
            "excerpt": chunk["content"][:200] + ("..." if len(chunk["content"]) > 200 else ""),
            "score": chunk["score"],
        })

    context_text = "\n---\n".join(context_parts)
    return context_text, citations
