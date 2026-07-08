"""LLM 工厂 - 支持阿里云百炼 / DeepSeek / OpenAI / Ollama 多后端"""

import httpx
from langchain_core.language_models.chat_models import BaseChatModel

from app.config import settings

# 共享的 httpx 客户端，避免每次调用 create 创建新客户端导致 "client has been closed" 错误
_shared_http_client: httpx.AsyncClient | None = None


def _get_http_client() -> httpx.AsyncClient:
    global _shared_http_client
    if _shared_http_client is None or _shared_http_client.is_closed:
        _shared_http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(120.0, connect=10.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=20),
        )
    return _shared_http_client


def get_llm(
    provider: str | None = None,
    model: str | None = None,
    temperature: float = 0.3,
    streaming: bool = True,
) -> BaseChatModel:
    """获取 LLM 实例，支持运行时切换提供商

    Args:
        provider: aliyun / deepseek / openai / ollama
        model: 模型名称
        temperature: 温度参数
        streaming: 是否开启流式输出
    """
    provider = provider or settings.DEFAULT_LLM_PROVIDER

    if provider in ("aliyun", "deepseek", "openai"):
        from langchain_openai import ChatOpenAI

        provider_config = {
            "aliyun": (settings.ALIYUN_API_KEY, settings.ALIYUN_BASE_URL, settings.ALIYUN_MODEL),
            "deepseek": (settings.DEEPSEEK_API_KEY, settings.DEEPSEEK_BASE_URL, settings.DEEPSEEK_MODEL),
            "openai": (settings.OPENAI_API_KEY, None, settings.OPENAI_DEFAULT_MODEL),
        }
        api_key, base_url, default_model = provider_config[provider]

        kwargs = dict(
            model=model or default_model,
            api_key=api_key,
            temperature=temperature,
            streaming=streaming,
            max_tokens=2048,
            http_async_client=_get_http_client(),
        )
        if base_url:
            kwargs["base_url"] = base_url

        return ChatOpenAI(**kwargs)

    elif provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=model or settings.OLLAMA_DEFAULT_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=temperature,
        )

    else:
        raise ValueError(f"不支持的 LLM 提供商: {provider}")
