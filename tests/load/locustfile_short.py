"""RAG 知识库问答系统 — 短请求压测（不含 RAG SSE）

仅测试短 HTTP 请求，避免 LLM API 费用。
适用于快速验证认证、会话管理、知识库列表等 API 的并发性能。

用法:
    locust -f locustfile_short.py --headless -u 100 -r 20 -t 180s --host http://127.0.0.1:8080
"""

import json
import os
import random
from typing import Optional

from locust import HttpUser, between, task

# ============================================================
# 数据加载
# ============================================================
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def _load_json(filename: str):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"[WARNING] 数据文件不存在: {path}")
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


TOKENS: list[dict] = _load_json("loadtest_tokens.json") or []
CONVERSATIONS: dict = _load_json("loadtest_conversations.json") or {}


class ShortRequestUser(HttpUser):
    """仅短 HTTP 请求的压测用户（不含 SSE 长连接）"""

    wait_time = between(0.5, 3)
    host = "http://127.0.0.1:8080"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.headers: dict = {}

    def on_start(self):
        """启动时使用预生成 token 或登录"""
        if TOKENS:
            t = random.choice(TOKENS)
            self.token = t["token"]
            self.user_id = t["user_id"]
        else:
            # Fallback 登录
            i = random.randint(1, 100)
            with self.client.post(
                "/api/auth/login",
                json={"username": f"loadtest_{i:03d}", "password": "test123456"},
                catch_response=True,
                name="POST /api/auth/login",
            ) as r:
                if r.status_code == 200:
                    self.token = r.json()["access_token"]

        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(20)
    def get_conversations(self):
        """会话列表（权重 20）"""
        if not self.token:
            return
        self.client.get(
            "/api/conversations?page=1&page_size=10",
            headers=self.headers,
            name="GET /api/conversations",
        )

    @task(15)
    def get_health(self):
        """健康检查（权重 15）"""
        self.client.get("/api/health", name="GET /api/health")

    @task(10)
    def create_conversation(self):
        """创建会话（权重 10）"""
        if not self.token:
            return
        self.client.post(
            "/api/conversations",
            json={"title": f"短测试-{random.randint(1,9999)}"},
            headers=self.headers,
            name="POST /api/conversations",
        )

    @task(10)
    def get_conversation_detail(self):
        """会话详情（权重 10）"""
        if not self.token or not self.user_id:
            return
        user_convs = CONVERSATIONS.get(str(self.user_id), [1])
        conv_id = random.choice(user_convs)
        self.client.get(
            f"/api/conversations/{conv_id}",
            headers=self.headers,
            name="GET /api/conversations/:id",
        )

    @task(5)
    def login_request(self):
        """登录请求（权重 5）"""
        i = random.randint(1, 100)
        self.client.post(
            "/api/auth/login",
            json={"username": f"loadtest_{i:03d}", "password": "test123456"},
            name="POST /api/auth/login",
        )

    @task(5)
    def get_me(self):
        """获取当前用户信息（权重 5）"""
        if not self.token:
            return
        self.client.get(
            "/api/auth/me",
            headers=self.headers,
            name="GET /api/auth/me",
        )

    @task(3)
    def register_user(self):
        """注册新用户（权重 3）"""
        uid = random.randint(10000, 99999)
        self.client.post(
            "/api/auth/register",
            json={
                "username": f"shorttest_{uid}",
                "password": "test123456",
                "confirm_password": "test123456",
            },
            name="POST /api/auth/register",
        )

    @task(2)
    def export_conversation(self):
        """导出对话 Markdown（权重 2）"""
        if not self.token or not self.user_id:
            return
        user_convs = CONVERSATIONS.get(str(self.user_id), [1])
        conv_id = random.choice(user_convs)
        self.client.get(
            f"/api/chat/{conv_id}/export",
            headers=self.headers,
            name="GET /api/chat/:id/export",
        )
