"""应用配置管理 - 基于 Pydantic Settings 从环境变量加载"""

import os
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings

# 项目根目录 = backend/ 的父目录
# config.py 在 backend/app/ 下，所以需要往上两级
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def resolve_path(path: str) -> str:
    """将相对路径解析为基于项目根目录的绝对路径"""
    if path.startswith("./") or path.startswith(".\\"):
        return os.path.join(PROJECT_ROOT, path[2:])
    if not os.path.isabs(path):
        return os.path.join(PROJECT_ROOT, path)
    return path


class Settings(BaseSettings):
    """全局配置，自动从 .env 文件和环境变量加载"""

    # 应用
    APP_NAME: str = "RAG 知识库问答系统"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # LLM - 阿里云百炼
    ALIYUN_API_KEY: Optional[str] = None
    ALIYUN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    ALIYUN_MODEL: str = "qwen-plus"

    # LLM - DeepSeek
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # LLM - OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_DEFAULT_MODEL: str = "gpt-4o"

    # LLM - Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_DEFAULT_MODEL: str = "qwen2.5:7b"

    # 默认 LLM 提供商: aliyun / deepseek / openai / ollama
    DEFAULT_LLM_PROVIDER: str = "aliyun"

    # Embedding
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-large-zh-v1.5"
    EMBEDDING_DEVICE: str = "cpu"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/app.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./data/chroma"

    # JWT
    JWT_SECRET_KEY: str = "change-me-to-a-random-secret-key-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    # 文件上传
    MAX_UPLOAD_SIZE_MB: int = 20

    # 文档分块
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    RETRIEVAL_TOP_K: int = 8

    # 限流
    RATE_LIMIT_ENABLED: bool = True

    # 用户注册开关
    ALLOW_REGISTRATION: bool = True

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def resolve_db_path(cls, v: str) -> str:
        """将 SQLite 相对路径解析为绝对路径"""
        if "sqlite" in v and ":///" in v:
            prefix, path = v.split(":///", 1)
            if path.startswith("./") or path.startswith(".\\"):
                abs_path = os.path.join(PROJECT_ROOT, path[2:])
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                return f"{prefix}:///{abs_path}"
        return v

    @field_validator("CHROMA_PERSIST_DIR", mode="after")
    @classmethod
    def resolve_chroma_path(cls, v: str) -> str:
        """将 ChromaDB 相对路径解析为绝对路径"""
        abs_path = resolve_path(v)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    model_config = {
        "env_file": os.path.join(PROJECT_ROOT, ".env"),
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
