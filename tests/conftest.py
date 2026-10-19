import os

import pytest

# `config` exige DATABASE_URL na importação. Para os testes unitários basta um
# valor válido: o engine do SQLAlchemy só conecta quando é usado.
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/unused"
)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"
