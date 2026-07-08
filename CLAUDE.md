# RAG 知识库问答系统 — 项目文档

---

## 一、项目概述

**项目名称**：RAG 企业级知识库问答系统
**项目类型**：毕设项目 — 基于 LangChain 的 RAG 电商知识库问答
**目标用户**：电商平台客服 / 普通消费者
**技术框架**：LangChain + FastAPI + React + ChromaDB

---

## 二、核心功能

1. **知识库管理**（管理员）：上传/删除文档，支持 PDF、Word、Excel、CSV、Markdown、TXT
2. **RAG 智能问答**：基于知识库内容回答商品问题，标注引用来源
3. **多用户会话**：每个用户独立会话，历史记录持久化
4. **用户认证**：注册/登录/修改密码，JWT 认证 + 角色权限

---

## 三、技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| LLM | 阿里云百炼 Qwen-Plus | 大语言模型 |
| RAG 框架 | LangChain | 检索增强生成管道 |
| Embedding | paraphrase-multilingual-MiniLM-L12-v2 | 文本向量化 |
| 后端 | FastAPI + SQLAlchemy 2.0 | API 服务 + ORM |
| 前端 | React 18 + TypeScript + Ant Design 5 | 用户界面 |
| 向量库 | ChromaDB | 向量存储与检索 |
| 数据库 | SQLite（开发）/ PostgreSQL（生产） | 业务数据 |
| 认证 | JWT + bcrypt | 用户认证 |

## 四、运行方式

### 后端
```bash
cd backend
$env:PYTHONPATH="."
uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
```

### 前端
```bash
cd frontend
npm run dev
```

### 默认管理员
- 用户名: `admin`
- 密码: `123456`

## 五、项目结构

```
langchainRAG/
├── backend/app/
│   ├── api/          # API 路由层
│   ├── core/         # 安全、中间件、依赖注入
│   ├── models/       # SQLAlchemy 数据模型
│   ├── schemas/      # Pydantic 验证模型
│   ├── services/     # 业务逻辑层
│   ├── rag/          # RAG 核心管道
│   └── db/           # 数据库配置
├── frontend/src/
│   ├── api/          # API 请求封装
│   ├── components/   # 可复用组件
│   ├── pages/        # 页面组件
│   ├── stores/       # Zustand 状态管理
│   └── types/        # TypeScript 类型
└── .claude/          # Claude Code 配置
```

## 六、开发规则

1. **技术决策**：列出方案 → 解释优劣 → 等用户选择
2. **代码修改前**：解释改什么、为什么、效果
3. **功能完成后**：用中文告知做了什么、如何验证
4. **错误处理**：用通俗语言解释，列出解决方案
5. **RAG 优先**：商品信息优先引用知识库，无相关内容时用模型自身知识
6. **安全第一**：密码 bcrypt 加密、JWT 认证、管理员权限隔离、API 限流
