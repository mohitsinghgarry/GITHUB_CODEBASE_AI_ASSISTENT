"""
Database connection management with async SQLAlchemy.

This module provides database connection setup, session management, and
connection pooling for the GitHub Codebase RAG Assistant.

Requirements:
- 14.2: Persist repository metadata, ingestion job status, and chat session history to a database
- 14.5: Support database migrations for schema changes
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.core.config import get_settings

# Base class for all ORM models
Base = declarative_base()

# Global engine and session maker instances
_engine: AsyncEngine | None = None
_async_session_maker: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """
    Get or create the global async database engine.
    
    The engine is created with connection pooling configured from settings.
    
    Returns:
        AsyncEngine: The global async database engine
    """
    global _engine
    
    if _engine is None:
        settings = get_settings()
        db_config = settings.get_database_config()
        
        _engine = create_async_engine(
            db_config["url"],
            pool_size=db_config["pool_size"],
            max_overflow=db_config["max_overflow"],
            echo=settings.debug,  # Log SQL queries in debug mode
            pool_pre_ping=True,  # Verify connections before using them
            pool_recycle=3600,  # Recycle connections after 1 hour
        )
    
    return _engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """
    Get or create the global async session maker.
    
    Returns:
        async_sessionmaker: The global async session maker
    """
    global _async_session_maker
    
    if _async_session_maker is None:
        engine = get_engine()
        _async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,  # Don't expire objects after commit
            autocommit=False,
            autoflush=False,
        )
    
    return _async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get a database session.
    
    This function is designed to be used with FastAPI's dependency injection.
    It yields a database session and ensures it's properly closed after use.
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    
    Yields:
        AsyncSession: An async database session
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    This function should be called during application startup.
    In production, use Alembic migrations instead.
    
    Note:
        This is primarily for development and testing. In production,
        use Alembic migrations to manage schema changes.
    """
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close the database engine and clean up connections.
    
    This function should be called during application shutdown.
    """
    global _engine, _async_session_maker
    
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_maker = None
