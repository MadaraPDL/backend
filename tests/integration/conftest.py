from __future__ import annotations

from collections.abc import AsyncGenerator
from urllib.parse import urlparse

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings


def _get_safe_integration_database_url() -> str:
    database_url = settings.TEST_DATABASE_URL or settings.DATABASE_URL
    database_name = urlparse(database_url).path.lstrip("/").lower()

    if not database_name:
        pytest.exit(
            "Refusing to run integration tests: database name could not be detected.",
            returncode=2,
        )

    safe_markers = ("test", "ci")

    if not any(marker in database_name for marker in safe_markers):
        pytest.exit(
            "Refusing to run integration tests against database "
            f"'{database_name}'. Set TEST_DATABASE_URL to a safe test database "
            "such as postgresql+asyncpg://USER:PASSWORD@localhost:5432/pulsefi_test.",
            returncode=2,
        )

    return database_url


@pytest_asyncio.fixture
async def integration_db() -> AsyncGenerator[AsyncSession, None]:
    test_engine = create_async_engine(
        _get_safe_integration_database_url(),
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
