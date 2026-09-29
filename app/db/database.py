import asyncio
from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import Settings


def build_database_url(settings: Settings) -> URL:
    """使用结构化 API 构造 URL，避免密码中的特殊字符破坏连接串。"""
    return URL.create(
        drivername="mysql+aiomysql",
        username=settings.mysql_user,
        password=settings.mysql_password,
        host=settings.mysql_host,
        port=settings.mysql_port,
        database=settings.mysql_database,
        query={"charset": "utf8mb4"},
    )


def create_database_engine(settings: Settings) -> AsyncEngine:
    return create_async_engine(
        build_database_url(settings),
        pool_pre_ping=True,
        pool_recycle=1800,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    """供业务路由通过 FastAPI Depends 获取事务会话。

    每个请求一个独立会话，自动管理事务：
    - 正常返回自动 commit（路由内 flush 即可拿到数据库生成的默认值）
    - 抛出异常自动 rollback
    """
    session_factory = request.app.state.db_session_factory
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def check_database(engine: AsyncEngine) -> bool:
    """在两秒内执行 SELECT 1，判断数据库是否可用。"""
    try:
        async with asyncio.timeout(2):
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
        return True
    except (SQLAlchemyError, TimeoutError, OSError):
        return False
