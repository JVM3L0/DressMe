from collections.abc import AsyncIterator

import pytest
from sqlalchemy import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

import infrastructure.persistence.models.user_model  # noqa: F401 (registra o model)
from infrastructure.persistence.models.base import Base
from tests.integration.database import (
    TEST_DATABASE_URL,
    create_database_if_missing,
)


@pytest.fixture(scope="session")
async def engine() -> AsyncIterator[AsyncEngine]:
    url = make_url(TEST_DATABASE_URL)
    try:
        await create_database_if_missing(url)
    except (OSError, SQLAlchemyError) as exc:
        pytest.skip(f"Postgres de teste indisponível: {exc}")

    engine = create_async_engine(url, hide_parameters=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def session(engine) -> AsyncIterator[AsyncSession]:
    """Sessão isolada: os commits do código viram savepoints e tudo é desfeito
    ao final do teste."""
    async with engine.connect() as conn:
        transaction = await conn.begin()
        session = AsyncSession(bind=conn, join_transaction_mode="create_savepoint")
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()
