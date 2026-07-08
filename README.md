# RAG 企业级知识库问答系统

基于 **LangChain** 框架开发的面向电商商品知识库的 RAG（检索增强生成）企业级问答系统。

## 功能特性

- **知识库管理**（管理员）：上传/删除/查看文档，支持 PDF、Word、Excel、CSV、Markdown、TXT
- **RAG 智能问答**：基于知识库内容回答，回答中标注引用来源
- **多用户会话管理**：每个用户独立会话，历史记录持久化
- **用户认证系统**：注册/登录/修改密码，JWT 认证
- **权限控制**：管理员可管理知识库，普通用户只能问答
- **SSE 流式响应**：AI 回答实时流式输出，首字延迟低
- **暗色模式**：支持亮色/暗色主题切换

## 技术栈

| 层级 | 技术 |
|------|------|
| LLM | DeepSeek API（中文优化，低成本） |
| RAG 框架 | LangChain + LangChain-Community |
| Embedding | BAAI/bge-large-zh-v1.5（本地免费） |
| 后端 | FastAPI（异步）+ SQLAlchemy 2.0 |
| 前端 | React 18 + TypeScript + Ant Design 5 |
| 向量数据库 | ChromaDB（HNSW 索引） |
| 数据库 | SQLite（开发）/ PostgreSQL（生产） |
| 认证 | JWT + bcrypt |

## 快速开始

### 1. 环境要求

- Python 3.11+
- Node.js 20+
- Redis（可选，用于缓存优化）

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入 DeepSeek API Key
```

### 3. 安装依赖

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 4. 初始化数据库

```bash
cd backend
PYTHONPATH="." python -m app.db.init_db
```

默认管理员账号：**admin** / 密码：**123456**

### 5. 启动服务

```bash
# 终端 1：启动后端
cd backend
PYTHONPATH="." uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 终端 2：启动前端
cd frontend
npm run dev
```

访问 http://localhost:5173 即可使用。

### 6. Docker 部署（可选）

```bash
docker-compose up -d
```

## API 文档

启动后端后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
langchainRAG/
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── api/              # API 路由
│   │   ├── core/             # 安全、中间件、依赖注入
│   │   ├── models/           # SQLAlchemy 数据模型
│   │   ├── schemas/          # Pydantic 请求/响应模型
│   │   ├── services/         # 业务逻辑层
│   │   ├── rag/              # RAG 核心（Embedding/检索/LLM/Prompt）
│   │   └── db/               # 数据库会话与初始化
│   └── requirements.txt
├── frontend/                 # React + TypeScript 前端
│   ├── src/
│   │   ├── api/              # API 请求封装
│   │   ├── components/       # 可复用组件
│   │   ├── pages/            # 页面组件
│   │   ├── stores/           # Zustand 状态管理
│   │   └── types/            # TypeScript 类型定义
│   └── package.json
├── docker/                   # Docker 配置
├── docker-compose.yml
└── .env.example
```

## RAG 管道流程

```
用户提问 → 查询重写 → 向量检索(ChromaDB HNSW) → 上下文组装
→ LLM生成(DeepSeek SSE流式) → 来源引用解析 → 返回前端
```

## License

毕业设计项目，仅供学习使用。
