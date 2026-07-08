"""ChromaDB 向量存储管理"""

import os
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings

# 全局 ChromaDB 客户端
_client: Optional[chromadb.PersistentClient] = None


def get_chroma_client() -> chromadb.PersistentClient:
    """获取 ChromaDB 持久化客户端（单例）"""
    global _client
    if _client is None:
        persist_dir = settings.CHROMA_PERSIST_DIR
        os.makedirs(persist_dir, exist_ok=True)
        _client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )
    return _client


def get_or_create_collection(collection_name: str) -> chromadb.Collection:
    """获取或创建 ChromaDB 集合"""
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def delete_collection(collection_name: str) -> None:
    """删除 ChromaDB 集合"""
    client = get_chroma_client()
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass  # 集合不存在时忽略


def get_global_collection() -> chromadb.Collection:
    """获取全局知识库集合（用于跨文档检索）"""
    # 注意：ChromaDB 支持多集合查询，此处为简化使用全局集合
    return get_or_create_collection("global_knowledge_base")


def get_chroma_langchain() -> "Chroma":
    """获取 LangChain 兼容的 Chroma 向量存储"""
    from langchain_chroma import Chroma
    from app.rag.embeddings import get_embeddings

    return Chroma(
        client=get_chroma_client(),
        collection_name="global_knowledge_base",
        embedding_function=get_embeddings(),
    )
