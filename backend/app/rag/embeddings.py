"""Embedding 模型工厂 - 支持本地模型和 OpenAI 在线模型，含 Redis 缓存"""

import asyncio
import os
from typing import Optional

from langchain_core.embeddings import Embeddings

# 强制 HuggingFace 离线模式，避免每次检查更新时因 SSL 失败
os.environ["HF_HUB_OFFLINE"] = "1"

from app.config import settings  # noqa: E402

# 全局 Embedding 实例缓存
_embedding_instance: Optional[Embeddings] = None


def get_embeddings() -> Embeddings:
    """获取 Embedding 模型实例（单例模式）"""
    global _embedding_instance

    if _embedding_instance is not None:
        return _embedding_instance

    model_name = settings.EMBEDDING_MODEL_NAME

    # BGE 系列模型通过 HuggingFace 本地加载
    if "bge" in model_name.lower():
        from langchain_huggingface import HuggingFaceEmbeddings

        _embedding_instance = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": settings.EMBEDDING_DEVICE},
            encode_kwargs={"normalize_embeddings": True},
        )
    # OpenAI Embeddings
    elif settings.OPENAI_API_KEY and "text-embedding" in model_name:
        from langchain_openai import OpenAIEmbeddings
        _embedding_instance = OpenAIEmbeddings(
            model=model_name,
            openai_api_key=settings.OPENAI_API_KEY,
        )
    else:
        # 默认使用 HuggingFace 加载
        from langchain_huggingface import HuggingFaceEmbeddings
        _embedding_instance = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": settings.EMBEDDING_DEVICE},
            encode_kwargs={"normalize_embeddings": True},
        )

    return _embedding_instance


async def embed_with_cache(text: str) -> list[float]:
    """生成 Embedding 并利用 Redis 缓存加速"""
    from app.db.redis_client import get_cached_embedding, set_cached_embedding

    # 1. 尝试从 Redis 缓存获取
    cached = await get_cached_embedding(text)
    if cached is not None:
        return cached

    # 2. 缓存未命中，调用 Embedding 模型
    embeddings = get_embeddings()
    # HuggingFaceEmbeddings.embed_query 是同步的，在线程池中运行
    vector = await asyncio.to_thread(embeddings.embed_query, text)

    # 3. 写入缓存
    await set_cached_embedding(text, vector)

    return vector
