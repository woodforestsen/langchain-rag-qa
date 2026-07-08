"""测试配置和共享 Fixtures"""

import asyncio
import os
import sys

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# 确保项目路径正确
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环供测试使用"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_client():
    """创建带 ASGI transport 的异步 HTTP 测试客户端"""
    os.environ["PYTHONPATH"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def admin_token(async_client):
    """获取管理员 JWT token"""
    response = await async_client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "123456"},
    )
    data = response.json()
    return data["access_token"]


@pytest_asyncio.fixture
async def auth_headers(admin_token):
    """带管理员认证的请求头"""
    return {"Authorization": f"Bearer {admin_token}"}
