from sqlalchemy import URL, make_url, text
from sqlalchemy.ext.asyncio import create_async_engine

from config import settings


def _default_test_database_url() -> str:
    # Mesmo servidor e credenciais do DATABASE_URL, em um banco `<nome>_test`
    url = make_url(settings.DATABASE_URL)
    return url.set(database=f"{url.database}_test").render_as_string(
        hide_password=False
    )


TEST_DATABASE_URL: str = (
    settings.get("TEST_DATABASE_URL") or _default_test_database_url()
)


async def create_database_if_missing(url: URL) -> None:
    admin_engine = create_async_engine(
        url.set(database="postgres"), isolation_level="AUTOCOMMIT"
    )
    try:
        async with admin_engine.connect() as conn:
            exists = await conn.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": url.database},
            )
            if not exists:
                await conn.execute(text(f'CREATE DATABASE "{url.database}"'))
    finally:
        await admin_engine.dispose()
