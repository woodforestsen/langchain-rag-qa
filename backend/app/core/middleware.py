"""中间件 - CORS、请求ID、限流、日志"""

import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import Response

from app.config import settings


def setup_cors(app: FastAPI) -> None:
    """配置 CORS 跨域"""
    origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def setup_rate_limiting(app: FastAPI) -> None:
    """配置 API 限流"""
    if not settings.RATE_LIMIT_ENABLED:
        return

    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200/minute"],
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def setup_middleware(app: FastAPI) -> None:
    """注册所有中间件"""
    setup_cors(app)
    setup_rate_limiting(app)

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        """为每个请求添加唯一 ID 和耗时记录"""
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        start_time = time.time()
        response: Response = await call_next(request)
        process_time = time.time() - start_time

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        return response
