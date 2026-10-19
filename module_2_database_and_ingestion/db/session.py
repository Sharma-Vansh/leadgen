"""
Async Database Session Engine
Provides async session maker, connection pooling, and transactional context managers.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
import logging
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from sqlalchemy import text
from module_2_database_and_ingestion.config import settings

logger = logging.getLogger("DatabaseSession")

# Engine cache
_engine: Optional[AsyncEngine] = None
_sessionmaker: Optional[async_sessionmaker[AsyncSession]] = None


def get_engine(url: Optional[str] = None) -> AsyncEngine:
    """Creates or returns the cached async SQLAlchemy engine."""
    global _engine, _sessionmaker
    target_url = url or settings.DATABASE_URL

    if _engine is None or (url is not None and str(_engine.url) != target_url):
        is_sqlite = target_url.startswith("sqlite")
        engine_kwargs = {
            "echo": settings.DB_ECHO,
            "future": True,
        }
        if not is_sqlite:
            engine_kwargs.update({
                "pool_size": settings.DB_POOL_SIZE,
                "max_overflow": settings.DB_MAX_OVERFLOW,
                "pool_timeout": settings.DB_POOL_TIMEOUT,
            })

        _engine = create_async_engine(target_url, **engine_kwargs)
        _sessionmaker = async_sessionmaker(
            bind=_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )
        logger.info(f"[DB] Initialized async engine with driver: {_engine.dialect.name}")

    return _engine


def get_sessionmaker(url: Optional[str] = None) -> async_sessionmaker[AsyncSession]:
    """Returns the cached async sessionmaker."""
    global _sessionmaker
    if _sessionmaker is None:
        get_engine(url)
    return _sessionmaker


@asynccontextmanager
async def get_async_session(url: Optional[str] = None) -> AsyncGenerator[AsyncSession, None]:
    """Transactional context manager for async database sessions."""
    sm = get_sessionmaker(url)
    async with sm() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_health(url: Optional[str] = None) -> bool:
    """Verifies that the database is reachable and accepts queries."""
    try:
        async with get_async_session(url) as session:
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        logger.warning(f"[DB] Health check failed: {e}")
        return False
