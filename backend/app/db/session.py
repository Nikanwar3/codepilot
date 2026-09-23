"""
Async SQLAlchemy engine + session factory, and the FastAPI dependency that
hands a request-scoped session to a route handler.

We use SQLAlchemy's async engine (asyncpg driver) because the whole request
path — FastAPI route -> RAG retrieval -> LLM call -> tool execution — is I/O
bound and async end to end. A sync session here would block the event loop
under load.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL_ASYNC,
    pool_pre_ping=True,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
