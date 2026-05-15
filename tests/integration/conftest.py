from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings


@pytest_asyncio.fixture
async def integration_db() -> AsyncGenerator[AsyncSession, None]:
    test_engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        poolclass=NullPool,
    )

    connection = await test_engine.connect()
    transaction = await connection.begin()

    TestSessionLocal = async_sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

    await transaction.rollback()
    await connection.close()
    await test_engine.dispose()
