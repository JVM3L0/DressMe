import os

import pytest

# Seleciona o ambiente [testing] do settings.toml antes de importar `config`
os.environ.setdefault("MODE", "testing")


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"
