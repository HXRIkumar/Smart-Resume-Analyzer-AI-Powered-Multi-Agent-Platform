"""Async SQLAlchemy engine and session setup.

Production-grade configuration with connection pooling,
health checks, and proper session lifecycle management.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from app.config import settings

# ─── Async Engine ────────────────────────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=not settings.is_production,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_timeout=30,
)

# ─── Session Factory ─────────────────────────────────────────────────────────
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


# ─── Declarative Base ────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


# ─── Dependency ──────────────────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields an async database session.

    Commits on success, rolls back on exception, always closes.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ─── Health Check ────────────────────────────────────────────────────────────
async def check_db_health() -> dict:
    """Verify database connectivity and return pool statistics.

    Returns:
        dict with keys: status, pool_size, checked_in, checked_out, overflow.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        pool = engine.pool
        return {
            "status": "healthy",
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
        }
    except Exception as exc:
        return {
            "status": "unhealthy",
            "error": str(exc),
        }
