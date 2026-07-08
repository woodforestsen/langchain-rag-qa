"""Redis 客户端 - Embedding 缓存 + 查询结果缓存"""

import hashlib
import json
from typing import Optional

import redis.asyncio as aioredis

from app.config import settings

# 全局 Redis 连接池
_redis: Optional[aioredis.Redis] = None


async def get_redis() -> Optional[aioredis.Redis]:
    """获取 Redis 连接（延迟连接，启动时若 Redis 不可用则降级）"""
    global _redis
    if _redis is not None:
        return _redis

    try:
        _redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=False,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        await _redis.ping()
    except Exception:
        _redis = None  # Redis 不可用，降级运行
    return _redis


# ==================== Embedding 缓存 ====================

def _embedding_cache_key(text: str) -> str:
    """生成 Embedding 缓存键"""
    text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"emb:{text_hash}"


async def get_cached_embedding(text: str) -> Optional[list[float]]:
    """从 Redis 获取缓存的 Embedding 向量"""
    r = await get_redis()
    if r is None:
        return None
    try:
        key = _embedding_cache_key(text)
        data = await r.get(key)
        if data:
            return json.loads(data)
    except Exception:
        pass
    return None


async def set_cached_embedding(text: str, embedding: list[float]) -> None:
    """将 Embedding 向量缓存到 Redis（7天过期）"""
    r = await get_redis()
    if r is None:
        return
    try:
        key = _embedding_cache_key(text)
        await r.setex(key, 7 * 86400, json.dumps(embedding))
    except Exception:
        pass


# ==================== 查询结果缓存 ====================

def _query_cache_key(question: str) -> str:
    """生成查询缓存键"""
    text_hash = hashlib.sha256(question.encode("utf-8")).hexdigest()
    return f"query:{text_hash}"


async def get_cached_query_result(question: str) -> Optional[list[dict]]:
    """从 Redis 获取缓存的热点查询检索结果"""
    r = await get_redis()
    if r is None:
        return None
    try:
        key = _query_cache_key(question)
        data = await r.get(key)
        if data:
            return json.loads(data)
    except Exception:
        pass
    return None


async def set_cached_query_result(question: str, chunks: list[dict]) -> None:
    """缓存查询的检索结果（1小时过期）"""
    r = await get_redis()
    if r is None:
        return
    try:
        key = _query_cache_key(question)
        # 只缓存可序列化的字段
        serializable = [
            {"content": c["content"], "metadata": c["metadata"], "score": c["score"]}
            for c in chunks
        ]
        await r.setex(key, 3600, json.dumps(serializable, ensure_ascii=False))
    except Exception:
        pass
