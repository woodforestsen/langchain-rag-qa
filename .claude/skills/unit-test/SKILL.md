---
name: unit-test
description: 使用 Vitest 为前端代码、pytest 为后端代码编写和执行单元测试。当用户说"写测试"、"加测试"、"测试一下"、"跑测试"、"单元测试"、"测试覆盖率"时自动触发。
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
argument-hint: "[要测试的文件或功能名称，不指定则测试全部]"
---

## 适用项目

RAG 知识库问答系统（langchainRAG），包含：
- **前端**: React + TypeScript + Ant Design + Zustand（Vitest 测试）
- **后端**: FastAPI + LangChain + SQLAlchemy（pytest 测试）

## 工作流程

### 收到"写测试"需求时

1. 先读取要测试的源代码文件
2. 分析其中的函数、组件、API 端点
3. **前端代码** → 创建 `xxx.test.ts`，放在被测试文件旁边
4. **后端代码** → 创建 `backend/tests/test_xxx.py`
5. 运行测试确认全部通过
6. 用中文汇报结果

### 收到"跑测试"需求时

1. 前端测试: `cd frontend && npx vitest run --reporter=verbose`
2. 后端测试: `cd backend && PYTHONPATH=. python -m pytest tests/ -v`
3. 用中文解读测试结果

### 收到"修复测试"需求时

1. 先跑一次测试，看哪些失败
2. 分析失败原因
3. 修复代码或测试
4. 重跑确认通过

## 项目特定规则

### 前端测试规则
- 测试文件命名: `xxx.test.ts`，放在被测试文件旁边
- Store 测试需要 mock Zustand
- localStorage 相关测试必须 mock
- React 组件测试使用 `@testing-library/react` + `jsdom`
- 每个 `it()` 只测一个行为
- 覆盖正常 + 边界情况（空数据、错误状态等）

### 后端测试规则
- 测试文件放在 `backend/tests/` 目录
- 使用 `pytest` + `pytest-asyncio`
- API 测试使用 `httpx.ASGITransport` 避免启动真实服务器
- 数据库测试使用 SQLite 内存数据库
- RAG 管道函数可以直接测试（不需要数据库）

## 执行测试命令

```bash
# 前端测试
cd frontend && npx vitest run --reporter=verbose

# 后端测试
cd backend && PYTHONPATH=. python -m pytest tests/ -v

# 后端单个测试文件
cd backend && PYTHONPATH=. python -m pytest tests/test_rag_pipeline.py -v
```

## 测试报告

每次执行完毕后，写入 `.claude/artifacts/test-result.json`:

```json
{
  "passed": true,
  "totalTests": 67,
  "failedTests": 0,
  "timestamp": "2026-07-08T12:00:00.000Z"
}
```
