import os
import sys
from subprocess import CalledProcessError

import pytest
from anyio import run_process
from sqlalchemy import make_url, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine

from tests.integration.database import TEST_DATABASE_URL, create_database_if_missing

pytestmark = [pytest.mark.anyio, pytest.mark.integration]

MIGRATIONS_URL = make_url(TEST_DATABASE_URL).set(
    database=f"{make_url(TEST_DATABASE_URL).database}_migrations"
)


async def alembic(*args: str) -> None:
    env = os.environ | {
        "DATABASE_URL": MIGRATIONS_URL.render_as_string(hide_password=False)
    }
    await run_process([sys.executable, "-m", "alembic", *args], env=env)


@pytest.fixture
async def engine():
    try:
        await create_database_if_missing(MIGRATIONS_URL)
    except (OSError, SQLAlchemyError) as exc:
        pytest.skip(f"Postgres de teste indisponível: {exc}")

    engine = create_async_engine(MIGRATIONS_URL)
    await alembic("downgrade", "base")
    yield engine
    await alembic("downgrade", "base")
    await engine.dispose()


async def test_migrations_upgrade_and_downgrade_cleanly(engine):
    await alembic("upgrade", "head")
    await alembic("check")  # models e migrações estão sincronizados
    await alembic("downgrade", "base")
    await alembic("upgrade", "head")


async def test_lowercase_migration_normalizes_existing_rows(engine):
    await alembic("upgrade", "61b394fd8bf1")
    async with engine.begin() as conn:
        await conn.execute(
            text(
                "INSERT INTO users (uid, username, email, hashed_password) "
                "VALUES (gen_random_uuid(), 'Joao', 'Joao@Example.com', 'hash')"
            )
        )

    await alembic("upgrade", "e08d8c40f2c0")

    async with engine.connect() as conn:
        row = (await conn.execute(text("SELECT username, email FROM users"))).one()
    assert tuple(row) == ("joao", "joao@example.com")


async def test_lowercase_migration_fails_on_case_insensitive_duplicates(engine):
    await alembic("upgrade", "61b394fd8bf1")
    async with engine.begin() as conn:
        await conn.execute(
            text(
                "INSERT INTO users (uid, username, email, hashed_password) VALUES "
                "(gen_random_uuid(), 'joao', 'joao@example.com', 'hash'), "
                "(gen_random_uuid(), 'JOAO', 'outro@example.com', 'hash')"
            )
        )

    with pytest.raises(CalledProcessError):
        await alembic("upgrade", "e08d8c40f2c0")
