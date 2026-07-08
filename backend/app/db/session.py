"""数据库会话管理 - SQLAlchemy 异步引擎"""

import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# SQLite 优化参数
# - timeout: aiosqlite 传递 timeout 给 sqlite3.connect()，等待锁的最长时间（秒）
# - 小连接池：减少并发写竞争
SQLITE_CONNECT_ARGS = {"timeout": 30}
SQLITE_POOL_SIZE = 20
SQLITE_MAX_OVERFLOW = 10

# 异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=SQLITE_POOL_SIZE if "sqlite" in settings.DATABASE_URL else 50,
    max_overflow=SQLITE_MAX_OVERFLOW if "sqlite" in settings.DATABASE_URL else 30,
    pool_pre_ping=True,   # 连接前检测有效性，防止使用已断开的连接
    pool_recycle=1800,    # 30 分钟回收连接，避免长时间占用
    connect_args=SQLITE_CONNECT_ARGS if "sqlite" in settings.DATABASE_URL else {},
)


async def _init_sqlite_pragma():
    """在启动时设置 SQLite WAL 模式及其他性能优化

    关键：必须在 create_tables() 之前调用，否则 WAL 模式不会在表创建时生效。
    WAL 模式是持久化设置（存储在 DB 文件头），设置一次即可永久生效。
    """
    if "sqlite" not in settings.DATABASE_URL:
        return

    import sqlite3

    # 解析数据库文件路径
    db_path = settings.DATABASE_URL.split(":///")[-1]

    # 确保目录存在
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    # 即使文件不存在也连接（sqlite3 会自动创建），确保 WAL 模式在 create_tables 之前设置
    conn = sqlite3.connect(db_path)

    # 持久化设置（存于 DB 文件，设置一次永久生效）
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA cache_size=-8000;")   # 8MB 缓存
    conn.execute("PRAGMA temp_store=MEMORY;")

    # 验证设置
    mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
    print(f"[SQLite] journal_mode={mode}")

    conn.close()

# 异步会话工厂
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy 模型基类"""
    pass


async def get_db() -> AsyncSession:
    """FastAPI 依赖: 获取数据库会话"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
