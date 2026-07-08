"""FastAPI 应用入口"""

# ⚠️ 必须在所有 HuggingFace 相关导入之前设置离线模式
import os
os.environ["HF_HUB_OFFLINE"] = "1"

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.exceptions import AppException
from app.core.middleware import setup_middleware
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库 + 预加载 Embedding 模型"""
    await init_db()

    # 预加载 Embedding 模型，避免首次请求时下载导致 httpx 冲突
    try:
        from app.rag.embeddings import get_embeddings
        import asyncio as aio
        await aio.to_thread(get_embeddings)
        print("Embedding model loaded successfully")
    except Exception as e:
        print(f"Warning: Failed to preload embedding model: {e}")

    yield


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    app = FastAPI(
        title=settings.APP_NAME,
        description="基于 LangChain 的 RAG 企业级知识库问答系统",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 注册自定义异常处理器
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.code,
            content={"detail": exc.message},
        )

    # 注册中间件
    setup_middleware(app)

    # 注册路由（延迟导入避免循环引用）
    from app.api.auth import router as auth_router
    from app.api.users import router as users_router
    from app.api.conversations import router as conversations_router
    from app.api.chat import router as chat_router
    from app.api.knowledge_base import router as knowledge_router

    app.include_router(auth_router, prefix="/api/auth", tags=["认证"])
    app.include_router(users_router, prefix="/api/users", tags=["用户"])
    app.include_router(conversations_router, prefix="/api/conversations", tags=["会话"])
    app.include_router(chat_router, prefix="/api/chat", tags=["聊天"])
    app.include_router(knowledge_router, prefix="/api/knowledge", tags=["知识库"])

    @app.get("/api/health", tags=["健康检查"])
    async def health_check():
        """服务健康检查"""
        return {"status": "healthy", "app": settings.APP_NAME}

    return app


app = create_app()
