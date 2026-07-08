---
name: rebuild-app
description: 重新构建 RAG 知识库问答系统。先检查前端 TypeScript + Vite 构建，再检查后端 Python 导入，最后报告结果。
disable-model-invocation: true
allowed-tools:
  - Bash
  - Read
  - Glob
---

# rebuild-app — 重新构建项目

## 执行步骤

### 第 1 步：前端类型检查
```bash
cd frontend && npx tsc --noEmit
```
- ✅ 通过 → 继续
- ❌ 有错误 → 用通俗语言告诉用户，**停止**

### 第 2 步：前端打包
```bash
cd frontend && npm run build
```

### 第 3 步：后端导入检查
```bash
cd backend && PYTHONPATH=. python -c "from app.main import app; print('Backend OK')"
```

### 第 4 步：报告结果
- ✅ 全部通过：告诉用户构建成功
- ❌ 某步失败：用通俗语言解释错误

## 注意事项
- 全程用中文沟通
- 前端打包输出在 `frontend/dist/`
- 后端用 FastAPI，不需要编译
