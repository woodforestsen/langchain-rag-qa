"""启动脚本 - 自动设置 Python 路径并启动 FastAPI 服务"""
import sys
import os

# 将 backend 目录加入 Python 路径
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# 同时设置 PYTHONPATH 环境变量，确保 reload 子进程也能找到模块
existing_path = os.environ.get("PYTHONPATH", "")
if existing_path:
    os.environ["PYTHONPATH"] = backend_dir + os.pathsep + existing_path
else:
    os.environ["PYTHONPATH"] = backend_dir

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8080,
        reload=True,
        reload_dirs=[backend_dir],
    )
