import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from .config import settings

# Vercel serverless 环境：SQLite 必须写到 /tmp
db_url = settings.DATABASE_URL
IS_VERCEL = os.environ.get("VERCEL") == "1"

if IS_VERCEL and "sqlite" in db_url:
    db_url = "sqlite+aiosqlite:////tmp/class_pet.db"

# 根据数据库类型选择连接参数
connect_args = {}
if "sqlite" in db_url:
    connect_args = {"check_same_thread": False}

# 异步引擎
engine = create_async_engine(
    db_url,
    echo=settings.DEBUG,
    connect_args=connect_args,
)

# 异步会话工厂
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# 基类
class Base(DeclarativeBase):
    pass


# 依赖注入：获取数据库会话
async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
