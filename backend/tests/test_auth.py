"""认证 API 测试"""

import pytest


@pytest.mark.asyncio
async def test_health_check(async_client):
    """测试健康检查接口"""
    response = await async_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_login_admin_success(async_client):
    """测试管理员登录成功"""
    response = await async_client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "123456"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 20


@pytest.mark.asyncio
async def test_login_wrong_password(async_client):
    """测试登录失败 - 错误密码"""
    response = await async_client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(async_client):
    """测试登录失败 - 不存在的用户"""
    response = await async_client.post(
        "/api/auth/login",
        json={"username": "nonexistent_user_xyz", "password": "123456"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_with_token(async_client, auth_headers):
    """测试获取当前用户信息（已认证）"""
    response = await async_client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"
    assert data["is_admin"] is True
    assert data["is_active"] is True
    assert "id" in data


@pytest.mark.asyncio
async def test_get_me_without_token(async_client):
    """测试获取当前用户信息（未认证）"""
    response = await async_client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_new_user(async_client):
    """测试注册新用户"""
    import random
    username = f"test_user_{random.randint(10000, 99999)}"
    response = await async_client.post(
        "/api/auth/register",
        json={"username": username, "password": "test123456"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == username
    assert data["is_admin"] is False


@pytest.mark.asyncio
async def test_register_duplicate_username(async_client):
    """测试重复用户名注册"""
    response = await async_client.post(
        "/api/auth/register",
        json={"username": "admin", "password": "123456"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_short_password(async_client):
    """测试短密码注册"""
    response = await async_client.post(
        "/api/auth/register",
        json={"username": "newuser", "password": "123"},
    )
    # FastAPI Pydantic 验证失败返回 422
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_change_password_success(async_client, auth_headers):
    """测试修改密码成功"""
    response = await async_client.post(
        "/api/auth/change-password",
        json={"old_password": "123456", "new_password": "newpass999"},
        headers=auth_headers,
    )
    assert response.status_code == 200

    # 改回原密码
    await async_client.post(
        "/api/auth/change-password",
        json={"old_password": "newpass999", "new_password": "123456"},
        headers=auth_headers,
    )


@pytest.mark.asyncio
async def test_change_password_wrong_old(async_client, auth_headers):
    """测试修改密码 - 旧密码错误"""
    response = await async_client.post(
        "/api/auth/change-password",
        json={"old_password": "wrongpassword", "new_password": "newpass999"},
        headers=auth_headers,
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_conversation(async_client, auth_headers):
    """测试创建新会话"""
    response = await async_client.post(
        "/api/conversations",
        json={"title": "测试会话"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["title"] == "测试会话"


@pytest.mark.asyncio
async def test_list_conversations(async_client, auth_headers):
    """测试获取会话列表"""
    response = await async_client.get(
        "/api/conversations",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_knowledge_stats_requires_admin(async_client):
    """测试知识库统计需要管理员权限"""
    # 先登录普通用户
    import random
    username = f"testuser_{random.randint(10000, 99999)}"
    reg_resp = await async_client.post(
        "/api/auth/register",
        json={"username": username, "password": "test123456"},
    )
    assert reg_resp.status_code == 200

    login_resp = await async_client.post(
        "/api/auth/login",
        json={"username": username, "password": "test123456"},
    )
    token = login_resp.json()["access_token"]

    response = await async_client.get(
        "/api/knowledge/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
