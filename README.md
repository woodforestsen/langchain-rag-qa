# 🧠 RAG 企业级知识库问答系统

<div align="center">

基于 **LangChain** + **FastAPI** + **React** 构建的 RAG（检索增强生成）电商知识库智能问答系统。

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-1C3C3C?logo=langchain)](https://www.langchain.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5+-FBBF24)](https://www.trychroma.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](./LICENSE)

</div>

---

## 📖 目录

- [项目简介](#-项目简介)
- [功能特性](#-功能特性)
- [技术架构](#-技术架构)
- [快速开始](#-快速开始)
- [项目结构](#-项目结构)
- [API 文档](#-api-文档)
- [RAG 管道详解](#-rag-管道详解)
- [部署指南](#-部署指南)
- [常见问题](#-常见问题)

---

## 🎯 项目简介

本项目是一个面向电商场景的企业级知识库问答系统，支持管理员上传商品文档（PDF、Word、Excel、CSV、Markdown、TXT），系统自动对文档进行向量化存储。普通用户可以通过自然语言提问，系统基于知识库内容生成准确回答，并标注引用来源。

**适用场景**：电商客服辅助、商品信息查询、企业知识管理。

---

## ✨ 功能特性

### 知识库管理（管理员）

| 功能 | 说明 |
|------|------|
| 📄 文档上传 | 支持 PDF、Word (.docx)、Excel (.xlsx)、CSV、Markdown、TXT |
| 🔍 文档预览 | 查看已上传文档的解析内容和分块信息 |
| 🗑️ 文档删除 | 删除文档并同步清理向量数据库中的对应数据 |
| 📊 文档统计 | 查看知识库中的文档数量和分块总数 |

### RAG 智能问答

| 功能 | 说明 |
|------|------|
| 💬 自然语言问答 | 基于知识库内容回答商品相关问题 |
| 📎 来源引用 | 每个回答标注引用的文档名称和段落 |
| 🌊 SSE 流式响应 | AI 回答实时逐字输出，体验流畅 |
| 🔄 查询重写 | 自动优化用户输入，提升检索命中率 |
| 🧠 多 LLM 支持 | 支持阿里云百炼、DeepSeek、OpenAI、Ollama 本地模型，一键切换 |

### 用户系统

| 功能 | 说明 |
|------|------|
| 👤 用户注册 | 新用户自主注册账号 |
| 🔐 JWT 登录 | 基于 JWT + bcrypt 的安全认证 |
| 🔑 修改密码 | 登录后修改个人密码 |
| 🛡️ 角色权限 | 管理员 ↔ 普通用户权限隔离 |

### 用户体验

| 功能 | 说明 |
|------|------|
| 💬 多会话管理 | 每个用户独立会话，历史记录持久化 |
| 🌓 暗色模式 | 亮色 / 暗色主题一键切换 |
| 📱 响应式布局 | 适配桌面和移动端浏览器 |

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                      前端 (React 18)                      │
│  Ant Design 5  │  Zustand  │  React Router  │  Axios     │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP/SSE
┌────────────────────────▼────────────────────────────────┐
│                   后端 (FastAPI)                          │
│  JWT 认证  │  API 限流  │  CORS  │  文档解析  │  日志     │
└────────────────────────┬────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   ChromaDB   │  │   SQLite /   │  │    Redis     │
│  (向量存储)   │  │  PostgreSQL  │  │   (缓存)     │
└─────────────┘  └─────────────┘  └─────────────┘
```

### 技术选型

| 层级 | 技术 | 选型理由 |
|------|------|----------|
| **LLM** | 阿里云百炼 Qwen-Plus（默认） | 中文理解力强，API 兼容 OpenAI 协议 |
| | DeepSeek / OpenAI / Ollama | 多提供商支持，可灵活切换 |
| **RAG 框架** | LangChain + LangChain-Community | 成熟的 RAG 管道抽象 |
| **Embedding** | paraphrase-multilingual-MiniLM-L12-v2 | 多语言支持好，本地运行零成本 |
| **后端** | FastAPI + SQLAlchemy 2.0 | 异步高性能，自动生成 API 文档 |
| **前端** | React 18 + TypeScript + Ant Design 5 | 类型安全，企业级 UI 组件库 |
| **向量库** | ChromaDB | 轻量级，嵌入式部署，HNSW 索引 |
| **数据库** | SQLite（开发）/ PostgreSQL（生产） | 开发零配置，生产可切换 |
| **认证** | JWT + bcrypt | 无状态认证，密码安全加密 |
| **限流** | slowapi | 防止 API 滥用 |

---

## 🚀 快速开始

### 环境要求

| 工具 | 最低版本 |
|------|----------|
| Python | 3.11+ |
| Node.js | 20+ |
| npm | 10+ |
| Redis | 7+（可选，用于缓存） |

### 1. 克隆项目

```bash
git clone https://github.com/woodforestsen/langchain-rag-qa.git
cd langchain-rag-qa
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，至少配置一个 LLM 的 API Key
```

**最小配置**（使用阿里云百炼）：

```ini
DEFAULT_LLM_PROVIDER=aliyun
ALIYUN_API_KEY=你的阿里云APIKey
```

<details>
<summary>🔧 支持的所有 LLM 提供商配置（点击展开）</summary>

```ini
# 阿里云百炼（默认推荐）
ALIYUN_API_KEY=sk-xxxx
ALIYUN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
ALIYUN_MODEL=qwen-plus

# DeepSeek（中文友好，低成本）
DEEPSEEK_API_KEY=sk-xxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# OpenAI
OPENAI_API_KEY=sk-xxxx
OPENAI_DEFAULT_MODEL=gpt-4o

# Ollama 本地模型（免费，无需网络）
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=qwen2.5:7b

# 切换提供商
DEFAULT_LLM_PROVIDER=aliyun  # aliyun / deepseek / openai / ollama
```

</details>

### 3. 安装依赖

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd ../frontend
npm install
```

### 4. 初始化数据库

```bash
cd backend
$env:PYTHONPATH="."
python -m app.db.init_db
```

首次运行会自动创建默认管理员账号：

| 用户名 | 密码 |
|--------|------|
| `admin` | `123456` |

### 5. 启动服务

**方式一：手动启动（开发环境）**

```bash
# 终端 1：启动后端
cd backend
$env:PYTHONPATH="."
uvicorn app.main:app --reload --host 127.0.0.1 --port 8080

# 终端 2：启动前端
cd frontend
npm run dev
```

**方式二：Docker 一键部署**

```bash
docker-compose up -d
```

### 6. 访问系统

| 服务 | 地址 |
|------|------|
| 🖥️ 前端界面 | http://localhost:5173 |
| 📚 API 文档 (Swagger) | http://localhost:8080/docs |
| 📖 API 文档 (ReDoc) | http://localhost:8080/redoc |
| ❤️ 健康检查 | http://localhost:8080/api/health |

---

## 📁 项目结构

```
langchainRAG/
├── backend/                          # FastAPI 后端
│   ├── app/
│   │   ├── api/                      # API 路由层
│   │   │   ├── auth.py               #   认证接口（注册/登录/修改密码）
│   │   │   ├── users.py              #   用户管理接口
│   │   │   ├── chat.py               #   RAG 问答接口（SSE 流式）
│   │   │   ├── conversations.py      #   会话管理接口
│   │   │   └── knowledge_base.py     #   知识库管理接口
│   │   ├── core/                     # 核心模块
│   │   │   ├── security.py           #   JWT 生成与验证
│   │   │   ├── middleware.py         #   中间件（CORS、限流）
│   │   │   ├── dependencies.py       #   依赖注入
│   │   │   └── exceptions.py         #   自定义异常
│   │   ├── models/                   # SQLAlchemy 数据模型
│   │   │   ├── user.py               #   用户模型
│   │   │   ├── document.py           #   文档模型
│   │   │   ├── conversation.py       #   会话模型
│   │   │   └── message.py            #   消息模型
│   │   ├── schemas/                  # Pydantic 验证模型
│   │   │   ├── auth.py               #   认证请求/响应
│   │   │   ├── chat.py               #   聊天请求/响应
│   │   │   ├── conversation.py       #   会话请求/响应
│   │   │   └── knowledge_base.py     #   知识库请求/响应
│   │   ├── services/                 # 业务逻辑层
│   │   │   ├── auth_service.py       #   用户认证逻辑
│   │   │   └── document_service.py   #   文档解析与处理
│   │   ├── rag/                      # RAG 核心管道
│   │   │   ├── embeddings.py         #   Embedding 模型加载
│   │   │   ├── chunker.py            #   文档分割器
│   │   │   ├── retriever.py          #   向量检索器
│   │   │   ├── pipeline.py           #   RAG 管道编排
│   │   │   └── llm_provider.py       #   多 LLM 提供商适配
│   │   ├── db/                       # 数据库配置
│   │   │   ├── session.py            #   异步会话管理
│   │   │   └── init_db.py            #   数据库初始化
│   │   ├── utils/                    # 工具函数
│   │   └── config.py                 # 全局配置（基于 pydantic-settings）
│   └── requirements.txt              # Python 依赖
├── frontend/                         # React + TypeScript 前端
│   ├── src/
│   │   ├── api/                      # API 请求封装
│   │   │   ├── auth.ts               #   认证 API
│   │   │   ├── chat.ts               #   聊天 API（SSE）
│   │   │   └── conversation.ts       #   会话 API
│   │   ├── components/               # 可复用组件
│   │   │   ├── layout/               #   布局组件（Header、Sidebar）
│   │   │   └── chat/                 #   聊天组件（气泡、输入框、引用）
│   │   ├── pages/                    # 页面组件
│   │   │   ├── ChatPage.tsx          #   问答主页
│   │   │   ├── LoginPage.tsx         #   登录页
│   │   │   ├── RegisterPage.tsx      #   注册页
│   │   │   ├── KnowledgePage.tsx     #   知识库管理页
│   │   │   ├── ProfilePage.tsx       #   个人中心页
│   │   │   └── NotFoundPage.tsx      #   404 页面
│   │   ├── stores/                   # Zustand 状态管理
│   │   │   ├── authStore.ts          #   认证状态
│   │   │   ├── chatStore.ts          #   聊天状态
│   │   │   └── themeStore.ts         #   主题状态
│   │   ├── types/                    # TypeScript 类型定义
│   │   │   ├── auth.ts               #   认证类型
│   │   │   ├── chat.ts               #   聊天类型
│   │   │   ├── document.ts           #   文档类型
│   │   │   └── common.ts             #   通用类型
│   │   ├── config/                   # 配置文件
│   │   │   └── api.ts                #   API 地址配置
│   │   ├── styles/                   # 样式文件
│   │   │   └── global.css            #   全局样式
│   │   ├── App.tsx                   # 根组件
│   │   └── main.tsx                  # 入口文件
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── docker/                           # Docker 配置
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
├── docker-compose.yml                # Docker 编排
├── .env.example                      # 环境变量模板
├── .gitignore
├── CLAUDE.md                         # Claude Code 项目文档
└── README.md                         # 本文件
```

---

## 📡 API 文档

### 接口总览

| 模块 | 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|------|
| 健康检查 | `GET` | `/api/health` | 服务健康检查 | 公开 |
| 认证 | `POST` | `/api/auth/register` | 用户注册 | 公开 |
| 认证 | `POST` | `/api/auth/login` | 用户登录 | 公开 |
| 认证 | `POST` | `/api/auth/change-password` | 修改密码 | 登录 |
| 用户 | `GET` | `/api/users/me` | 获取当前用户信息 | 登录 |
| 用户 | `PUT` | `/api/users/me` | 更新个人信息 | 登录 |
| 会话 | `GET` | `/api/conversations` | 获取会话列表 | 登录 |
| 会话 | `POST` | `/api/conversations` | 创建新会话 | 登录 |
| 会话 | `DELETE` | `/api/conversations/{id}` | 删除会话 | 登录 |
| 聊天 | `POST` | `/api/chat` | 发送消息（SSE 流式） | 登录 |
| 知识库 | `GET` | `/api/knowledge/documents` | 文档列表 | 登录 |
| 知识库 | `POST` | `/api/knowledge/documents/upload` | 上传文档 | 管理员 |
| 知识库 | `GET` | `/api/knowledge/documents/{id}` | 文档详情 | 登录 |
| 知识库 | `DELETE` | `/api/knowledge/documents/{id}` | 删除文档 | 管理员 |

启动后端后，访问 http://localhost:8080/docs 可查看完整的交互式 API 文档。

---

## 🔬 RAG 管道详解

```
                    ┌──────────────┐
                    │   用户提问     │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   查询重写     │  ← LLM 优化查询语句
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Embedding    │  ← sentence-transformers 向量化
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  ChromaDB     │  ← HNSW 索引，Top-K 检索
                    │  相似度检索    │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  上下文组装    │  ← 拼接检索片段 + 系统提示词
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   LLM 生成    │  ← 阿里云百炼 / DeepSeek SSE 流式
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  来源引用解析  │  ← 提取文档名称和段落编号
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  返回前端展示  │  ← SSE 逐字流式 + 引用标注
                    └──────────────┘
```

### 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `CHUNK_SIZE` | 500 | 文档分块大小（字符数） |
| `CHUNK_OVERLAP` | 50 | 相邻块重叠字符数 |
| `RETRIEVAL_TOP_K` | 8 | 检索返回的最相关文档块数 |
| `MAX_UPLOAD_SIZE_MB` | 20 | 上传文件大小限制 |

---

## 🐳 部署指南

### Docker 部署

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env，填入生产环境配置

# 2. 启动所有服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down
```

### 生产环境注意事项

1. **JWT 密钥**：修改 `JWT_SECRET_KEY` 为随机字符串
2. **数据库**：生产环境建议切换到 PostgreSQL
3. **Redis**：生产环境建议启用 Redis 缓存
4. **关闭 DEBUG**：设置 `DEBUG=false`
5. **关闭注册**：如不需要公开注册，设置 `ALLOW_REGISTRATION=false`
6. **HTTPS**：生产环境务必配置 HTTPS 反向代理（Nginx / Caddy）
7. **防火墙**：只开放 80/443 端口，后端 8080 端口不对公网暴露

### Nginx 反向代理配置参考

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        proxy_pass http://127.0.0.1:5173;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_buffering off;  # SSE 流式响应必须关闭缓冲
    }
}
```

---

## ❓ 常见问题

<details>
<summary><b>Q: 首次启动时 Embedding 模型下载很慢怎么办？</b></summary>

模型 `paraphrase-multilingual-MiniLM-L12-v2` 约 470MB，首次启动会自动从 HuggingFace 下载。如果网络不佳：

1. 设置 HuggingFace 镜像：`export HF_ENDPOINT=https://hf-mirror.com`
2. 或手动下载模型放到 `~/.cache/huggingface/hub/` 目录
3. 也可在 `.env` 中更换为其他 Embedding 模型，如 `BAAI/bge-large-zh-v1.5`
</details>

<details>
<summary><b>Q: 如何切换 LLM 提供商？</b></summary>

修改 `.env` 中的 `DEFAULT_LLM_PROVIDER` 即可：

```ini
DEFAULT_LLM_PROVIDER=deepseek   # 切换到 DeepSeek
DEFAULT_LLM_PROVIDER=openai     # 切换到 OpenAI
DEFAULT_LLM_PROVIDER=ollama     # 切换到本地 Ollama
```

切换后重启后端服务生效。
</details>

<details>
<summary><b>Q: Windows 下运行报错怎么办？</b></summary>

1. 确保使用 **PowerShell** 而非 CMD
2. Python 路径设置：`$env:PYTHONPATH="."`
3. 如遇到 `python-magic` 安装失败，Windows 需要先安装 `pip install python-magic-bin`
4. Redis 在 Windows 上可使用 Docker 运行：`docker run -d -p 6379:6379 redis:7-alpine`
</details>

<details>
<summary><b>Q: 如何重置管理员密码？</b></summary>

```bash
cd backend
$env:PYTHONPATH="."
python -c "
import asyncio
from app.db.session import async_session
from app.models.user import User
from app.core.security import hash_password

async def reset():
    async with async_session() as db:
        user = await db.get(User, 1)
        user.hashed_password = hash_password('新密码')
        await db.commit()
        print('密码已重置')

asyncio.run(reset())
"
```
</details>

---

## 🤝 贡献者

本项目为毕业设计作品，由 [woodforestsen](https://github.com/woodforestsen) 开发。

---

## 📄 License

本项目仅用于学习用途。

---

<div align="center">
  <sub>Built with ❤️ using LangChain, FastAPI, and React</sub>
</div>
