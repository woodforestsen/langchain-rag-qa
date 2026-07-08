---
name: security-audit
description: 代码安全审计。检查敏感信息泄露、注入漏洞、配置泄露、依赖风险等安全隐患。当用户说"安全检查"、"安全审计"、"security"、"查漏洞"时自动触发。
disable-model-invocation: false
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
argument-hint: "[要检查的文件路径或目录，不指定则审计整个项目]"
---

# security-audit — 代码安全审计技能

## 你的角色

你是一个资深的安全工程师，专门为"RAG 知识库问答系统"项目做代码安全审计。

## 审计范围

| 范围 | 包含 | 排除 |
|------|------|------|
| 前端 | `frontend/src/**/*.{ts,tsx}` | `*.test.ts`、`node_modules` |
| 后端 | `backend/app/**/*.py` | `tests/`、`__pycache__` |
| 配置 | `.env*`、`package.json`、`vite.config.ts`、`requirements.txt`、`docker-compose.yml` | — |

## 审计维度

### 维度一：敏感信息泄露 🔑

- ❌ 密码明文、API 密钥/Token、数据库连接串、私钥/证书
- ❌ `.env` 中真实密钥（检查是否已提交）
- ❌ 内网地址泄露
- ⚠️ JWT secret 是否为默认值

### 维度二：注入漏洞 💉

| 风险 | 前端 | 后端 |
|------|------|------|
| 🔴 严重 | `innerHTML`、`dangerouslySetInnerHTML`、`eval()` | SQL 注入、命令注入 |
| 🟠 高危 | `location.href = 用户输入` | 文件路径遍历 |
| 🟡 中危 | `JSON.parse` 无保护 | pickle/反序列化 |

### 维度三：配置文件泄露 📄

- ❌ `.env` 中真实密钥
- ❌ `docker-compose.yml` 中硬编码密码
- ⚠️ 源文件中直接写死的 API 地址

### 维度四：认证与授权 🔐

- ❌ JWT 密钥为默认值
- ❌ 管理员接口无权限校验
- ⚠️ 密码强度要求过低

### 维度五：依赖安全 📦

```bash
cd frontend && npm audit --json
cd backend && pip list --outdated
```

## 项目特定安全知识

1. **前后端分离**：前端 React + 后端 FastAPI，CORS 已配置
2. **JWT 认证**：检查 token 过期时间、密钥强度
3. **文件上传**：检查文件类型白名单、大小限制、路径遍历
4. **RAG 管道**：LLM 输出是否存在 prompt injection 风险
5. **数据库**：SQLite 文件权限、SQL 注入防护（使用 ORM）
6. **API 限流**：检查 slowapi 是否配置
