import os
import uuid

import pytest
from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from infrastructure.web.handlers import rate_limit_exceeded_handler

pytestmark = [pytest.mark.anyio, pytest.mark.integration]

TEST_REDIS_URL = os.environ.get("TEST_REDIS_URL")


def make_instance(prefix: str) -> FastAPI:
    """Simula uma instância da API com seu próprio limiter, como a de
    `infrastructure/web/rate_limit.py`, mas com storage no Redis."""
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri=TEST_REDIS_URL,
        strategy="moving-window",
        key_prefix=prefix,
    )
    app = FastAPI()
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    @app.post("/limited")
    @limiter.limit("2/minute")
    async def limited(request: Request) -> dict:
        return {"ok": True}

    return app


@pytest.fixture
def prefix() -> str:
    if not TEST_REDIS_URL:
        if os.environ.get("CI"):
            pytest.fail("TEST_REDIS_URL não definido no CI")
        pytest.skip("TEST_REDIS_URL não definido")
    return f"test-{uuid.uuid4()}"


async def post(app: FastAPI) -> int:
    transport = ASGITransport(app=app, client=("203.0.113.10", 12345))
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return (await client.post("/limited")).status_code


async def test_redis_storage_shares_limit_between_instances(prefix):
    instance_a, instance_b = make_instance(prefix), make_instance(prefix)

    assert await post(instance_a) == 200
    assert await post(instance_b) == 200
    # Terceira requisição, em qualquer instância, excede o limite compartilhado
    assert await post(instance_a) == 429
    assert await post(instance_b) == 429
