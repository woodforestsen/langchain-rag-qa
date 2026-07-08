"""RAG 知识库问答系统 — Locust 压力测试脚本

支持三个测试场景（通过 --tags 切换）：
  - auth_only : 纯登录压测
  - rag_chat   : RAG 问答压测（SSE 长连接）
  - mixed_flow : 混合场景（默认，模拟真实用户行为）

用法:
  # Web UI 模式
  locust -f locustfile.py --host http://127.0.0.1:8080

  # Headless 模式
  locust -f locustfile.py --headless -u 100 -r 10 -t 300s --host http://127.0.0.1:8080

  # 指定场景
  locust -f locustfile.py --tags rag_chat --headless -u 50 -r 5 -t 120s --host http://127.0.0.1:8080
"""

import csv
import json
import os
import random
import time
from typing import Optional

import httpx
from locust import HttpUser, between, events, task, tag

# ============================================================
# 数据加载（模块级，测试启动时加载一次）
# ============================================================
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")


def _load_json(filename: str):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"[WARNING] 数据文件不存在: {path}")
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


TOKENS: list[dict] = _load_json("loadtest_tokens.json") or []
QUESTIONS: list[str] = _load_json("loadtest_questions.json") or ["这个产品怎么样？"]
CONVERSATIONS: dict = _load_json("loadtest_conversations.json") or {}

# 默认用户凭证（当 token 文件不存在时用于实时注册/登录）
DEFAULT_PASSWORD = "test123456"

# SSE 阶段指标收集
sse_metrics: list[dict] = []


# ============================================================
# 事件钩子
# ============================================================
@events.init.add_listener
def on_init(environment, **kwargs):
    global sse_metrics
    sse_metrics = []
    print(f"\n{'='*50}")
    print(f"  压力测试初始化")
    print(f"{'='*50}")
    print(f"  Token 数量: {len(TOKENS)}")
    print(f"  问题池大小: {len(QUESTIONS)}")
    print(f"  会话映射数: {len(CONVERSATIONS)}")
    print(f"{'='*50}\n")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception=None,
               context=None, **kwargs):
    if request_type == "SSE_METRICS" and context:
        sse_metrics.append(context)


@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    """测试结束时输出 SSE 阶段统计"""
    if not sse_metrics:
        return

    os.makedirs(RESULTS_DIR, exist_ok=True)

    # 计算统计
    def _pct(data, p):
        if not data:
            return 0
        return sorted(data)[int(len(data) * p / 100)]

    searching_times = [m["searching_time"] for m in sse_metrics if m.get("searching_time")]
    first_token_times = [m["first_token_time"] for m in sse_metrics if m.get("first_token_time")]
    total_times = [m["total_time"] for m in sse_metrics if m.get("total_time")]
    token_counts = [m["token_count"] for m in sse_metrics if m.get("token_count")]

    print("\n" + "=" * 60)
    print("  📊 SSE 阶段耗时统计")
    print("=" * 60)
    print(f"  有效样本数: {len(sse_metrics)}")
    if searching_times:
        print(f"  检索阶段 P50: {_pct(searching_times, 50):.2f}s  P95: {_pct(searching_times, 95):.2f}s  P99: {_pct(searching_times, 99):.2f}s")
    if first_token_times:
        print(f"  首Token   P50: {_pct(first_token_times, 50):.2f}s  P95: {_pct(first_token_times, 95):.2f}s  P99: {_pct(first_token_times, 99):.2f}s")
    if total_times:
        print(f"  完整回答  P50: {_pct(total_times, 50):.2f}s  P95: {_pct(total_times, 95):.2f}s  P99: {_pct(total_times, 99):.2f}s")
    if token_counts:
        print(f"  平均 Token 数: {sum(token_counts) / len(token_counts):.1f}")
    print("=" * 60 + "\n")

    # 写 CSV
    if sse_metrics:
        csv_path = os.path.join(RESULTS_DIR, "sse_stage_metrics.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=sse_metrics[0].keys())
            writer.writeheader()
            writer.writerows(sse_metrics)
        print(f"  SSE 阶段指标已保存至: {csv_path}\n")


# ============================================================
# 基础用户行为类
# ============================================================
class RAGBaseUser(HttpUser):
    """RAG 系统压测基类 — 提供登录、注册、创建会话等公共方法"""

    abstract = True  # 标记为抽象，Locust 不会直接实例化
    wait_time = between(3, 10)
    host = "http://127.0.0.1:8080"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.conv_ids: list[int] = []
        self.headers: dict = {}

    def _set_auth(self, token_data: dict):
        """设置认证信息"""
        self.token = token_data["token"]
        self.user_id = token_data["user_id"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        # 加载预创建的会话
        user_convs = CONVERSATIONS.get(str(self.user_id), [])
        self.conv_ids = user_convs if user_convs else [1]

    def _login(self, username: str, password: str) -> bool:
        """登录获取 token"""
        with self.client.post(
            "/api/auth/login",
            json={"username": username, "password": password},
            catch_response=True,
            name="POST /api/auth/login",
        ) as resp:
            if resp.status_code == 200:
                data = resp.json()
                self.token = data.get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
                return True
            else:
                resp.failure(f"Login failed [{resp.status_code}]: {resp.text}")
                return False

    def _register(self, username: str, password: str) -> bool:
        """注册新用户"""
        with self.client.post(
            "/api/auth/register",
            json={
                "username": username,
                "password": password,
                "confirm_password": password,
            },
            catch_response=True,
            name="POST /api/auth/register",
        ) as resp:
            return resp.status_code == 200

    def _create_conversation(self) -> Optional[int]:
        """创建新会话，返回 conversation_id"""
        if not self.token:
            return None
        with self.client.post(
            "/api/conversations",
            json={"title": "压测对话"},
            headers=self.headers,
            catch_response=True,
            name="POST /api/conversations",
        ) as resp:
            if resp.status_code == 200:
                return resp.json().get("id")
            return None

    def _ask_rag(self, conv_id: int, question: str) -> Optional[dict]:
        """发送 RAG 问题并收集 SSE 流式响应

        Returns:
            dict 包含 searching_time, first_token_time, total_time, token_count, sources_count
            失败返回 None
        """
        start = time.time()
        searching_time = None
        thinking_time = None
        first_token_time = None
        token_count = 0
        sources_count = 0
        has_done = False

        try:
            with httpx.stream(
                "POST",
                f"{self.host}/api/chat/{conv_id}",
                json={"question": question, "conversation_id": conv_id},
                headers=self.headers,
                timeout=120.0,
            ) as resp:
                if resp.status_code != 200:
                    events.request.fire(
                        request_type="SSE",
                        name="POST /api/chat (RAG SSE)",
                        response_time=(time.time() - start) * 1000,
                        response_length=0,
                        exception=Exception(f"HTTP {resp.status_code}"),
                    )
                    return None

                for line in resp.iter_lines():
                    if not line.startswith("data: "):
                        continue
                    try:
                        data = json.loads(line[6:])
                    except json.JSONDecodeError:
                        continue

                    event_type = data.get("event")
                    if event_type == "searching":
                        searching_time = time.time() - start
                    elif event_type == "thinking":
                        thinking_time = time.time() - start
                    elif event_type == "token":
                        if first_token_time is None:
                            first_token_time = time.time() - start
                        token_count += 1
                    elif event_type == "sources":
                        sources_count = len(data.get("data", []))
                    elif event_type == "error":
                        events.request.fire(
                            request_type="SSE",
                            name="POST /api/chat (RAG SSE)",
                            response_time=(time.time() - start) * 1000,
                            response_length=0,
                            exception=Exception(data.get("data", "Unknown SSE error")),
                        )
                        return None
                    elif event_type == "done":
                        has_done = True

        except Exception as e:
            events.request.fire(
                request_type="SSE",
                name="POST /api/chat (RAG SSE)",
                response_time=(time.time() - start) * 1000,
                response_length=0,
                exception=e,
            )
            return None

        total_time = time.time() - start

        if not has_done:
            events.request.fire(
                request_type="SSE",
                name="POST /api/chat (RAG SSE)",
                response_time=total_time * 1000,
                response_length=token_count,
                exception=Exception("SSE stream ended without 'done' event"),
            )
            return None

        # 上报 Locust 统计
        events.request.fire(
            request_type="SSE",
            name="POST /api/chat (RAG SSE)",
            response_time=total_time * 1000,
            response_length=token_count,
        )

        # 上报 SSE 阶段指标
        if first_token_time is not None:
            events.request.fire(
                request_type="SSE_METRICS",
                name="rag_stages",
                response_time=total_time * 1000,
                response_length=token_count,
                context={
                    "searching_time": round(searching_time, 3) if searching_time else 0,
                    "thinking_time": round(thinking_time, 3) if thinking_time else 0,
                    "first_token_time": round(first_token_time, 3),
                    "total_time": round(total_time, 3),
                    "token_count": token_count,
                    "sources_count": sources_count,
                },
            )

        return {
            "searching_time": searching_time,
            "first_token_time": first_token_time,
            "total_time": total_time,
            "token_count": token_count,
            "sources_count": sources_count,
        }


# ============================================================
# 统一压测用户（单一非抽象类，所有场景的任务合并）
# 通过 --tags 切换场景：auth_only | rag_chat | mixed_flow
# ============================================================
class LoadTestUser(RAGBaseUser):
    """统一压测用户 — 通过 --tags 切换场景"""

    wait_time = between(3, 10)
    _registered_users = set()

    def on_start(self):
        """启动时根据场景初始化"""
        if TOKENS:
            self._set_auth(random.choice(TOKENS))

    # ========== 场景 1：纯登录压测 ==========

    @tag("auth_only")
    @task
    def login_only(self):
        """高频登录请求"""
        i = random.randint(1, 100)
        self._login(f"loadtest_{i:03d}", DEFAULT_PASSWORD)

    # ========== 场景 2：RAG 问答压测 ==========

    @tag("rag_chat")
    @task
    def ask_rag_question(self):
        """RAG 问答（SSE 流式）"""
        if not self.token:
            i = random.randint(1, 100)
            self._login(f"loadtest_{i:03d}", DEFAULT_PASSWORD)
            if not self.token:
                return
        if not self.conv_ids:
            cid = self._create_conversation()
            if cid:
                self.conv_ids = [cid]
            else:
                return

        conv_id = random.choice(self.conv_ids)
        question = random.choice(QUESTIONS)
        self._ask_rag(conv_id, question)

    # ========== 场景 3：混合场景（默认） ==========

    @tag("mixed_flow")
    @task(35)
    def mixed_returning_ask(self):
        """老用户提问"""
        if not self.token:
            i = random.randint(1, 100)
            self._login(f"loadtest_{i:03d}", DEFAULT_PASSWORD)
            if not self.token:
                return
        if not self.conv_ids:
            cid = self._create_conversation()
            if cid:
                self.conv_ids = [cid]
            else:
                return
        conv_id = random.choice(self.conv_ids)
        self._ask_rag(conv_id, random.choice(QUESTIONS))

    @tag("mixed_flow")
    @task(15)
    def mixed_browse(self):
        """浏览会话列表"""
        if not self.token:
            return
        self.client.get("/api/conversations", headers=self.headers,
                        name="GET /api/conversations")

    @tag("mixed_flow")
    @task(10)
    def mixed_create_conv(self):
        """创建新会话"""
        if not self.token:
            return
        cid = self._create_conversation()
        if cid and cid not in self.conv_ids:
            self.conv_ids.append(cid)

    @tag("mixed_flow")
    @task(10)
    def mixed_new_user_flow(self):
        """新用户完整流程"""
        uid = random.randint(10000, 99999)
        username = f"perf_{uid}"
        with self.client.post(
            "/api/auth/register",
            json={"username": username, "password": DEFAULT_PASSWORD,
                  "confirm_password": DEFAULT_PASSWORD},
            catch_response=True,
            name="POST /api/auth/register",
        ) as r:
            if r.status_code not in (200, 409):
                r.failure(f"Register failed [{r.status_code}]")
                return

        if self._login(username, DEFAULT_PASSWORD):
            cid = self._create_conversation()
            if cid:
                self.conv_ids = [cid]
                self._ask_rag(cid, random.choice(QUESTIONS))

    @tag("mixed_flow")
    @task(15)
    def mixed_login(self):
        """登录"""
        i = random.randint(1, 100)
        self._login(f"loadtest_{i:03d}", DEFAULT_PASSWORD)

    @tag("mixed_flow")
    @task(5)
    def mixed_health(self):
        """健康检查"""
        self.client.get("/api/health", name="GET /api/health")

    @tag("mixed_flow")
    @task(10)
    def mixed_login_and_ask(self):
        """登录后立即提问"""
        i = random.randint(1, 100)
        if self._login(f"loadtest_{i:03d}", DEFAULT_PASSWORD):
            user_convs = CONVERSATIONS.get(str(i), [1])
            self._ask_rag(random.choice(user_convs), random.choice(QUESTIONS))
