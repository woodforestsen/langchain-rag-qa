"""数据库初始化 - 建表 + 创建管理员账号"""

import asyncio

from sqlalchemy import select

from app.config import settings
from app.core.security import hash_password
from app.db.session import Base, async_session_factory, engine, _init_sqlite_pragma
from app.models import *  # noqa: 确保所有模型被导入


async def create_tables():
    """创建所有数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("数据库表创建完成")


async def seed_admin():
    """创建默认管理员账号 admin/123456"""
    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.username == "admin"))
        existing_admin = result.scalar_one_or_none()

        if existing_admin is None:
            admin = User(
                username="admin",
                password_hash=hash_password("123456"),
                is_admin=True,
            )
            session.add(admin)
            await session.commit()
            print("管理员账号已创建: admin / 123456")
        else:
            print("管理员账号已存在，跳过创建")


async def init_db():
    """初始化数据库：建表 + 种子数据"""
    await _init_sqlite_pragma()  # 先设置 WAL 模式
    await create_tables()
    await seed_admin()


if __name__ == "__main__":
    asyncio.run(init_db())
