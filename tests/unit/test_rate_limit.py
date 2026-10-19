from collections.abc import AsyncIterator, Iterator

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient
from limits import parse

from application.use_cases.create_user import CreateUserUseCase
from config import settings
from infrastructure.web.dependencies import get_create_user_use_case
from infrastructure.web.rate_limit import limiter
from main import app
from tests.fakes import FakePasswordHasher, FakeUserRepository

pytestmark = pytest.mark.anyio

SIGNUP_LIMIT = parse(settings.RATE_LIMIT_SIGNUP).amount


def payload(i: int) -> dict:
    return {
        "username": f"user{i}",
        "email": f"user{i}@example.com",
        "password": "senha-segura",
    }


@pytest.fixture(autouse=True)
def enabled_limiter() -> Iterator[None]:
    limiter.reset()
    limiter.enabled = True
    yield
    limiter.enabled = settings.RATE_LIMIT_ENABLED
    limiter.reset()


@pytest.fixture(autouse=True)
def fake_use_case() -> Iterator[None]:
    repository = FakeUserRepository()
    app.dependency_overrides[get_create_user_use_case] = lambda: CreateUserUseCase(
        repository=repository, password_hasher=FakePasswordHasher()
    )
    yield
    app.dependency_overrides.clear()


def client_from(ip: str) -> AsyncClient:
    return AsyncClient(
        transport=ASGITransport(app=app, client=(ip, 12345)),
        base_url="http://test",
    )


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    async with client_from("203.0.113.10") as client:
        yield client


def test_default_signup_limit_is_5_per_minute():
    assert settings.RATE_LIMIT_SIGNUP == "5/minute"
    assert SIGNUP_LIMIT == 5


async def test_signups_within_limit_are_accepted(client):
    for i in range(SIGNUP_LIMIT):
        response = await client.post("/users/", json=payload(i))
        assert response.status_code == status.HTTP_201_CREATED


async def test_signup_over_limit_returns_429_with_retry_after(client):
    for i in range(SIGNUP_LIMIT):
        await client.post("/users/", json=payload(i))

    response = await client.post("/users/", json=payload(SIGNUP_LIMIT))

    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert response.json() == {
        "detail": "Muitas requisições. Tente novamente mais tarde."
    }
    assert response.headers["Retry-After"] == "60"


async def test_rejected_attempts_also_count_towards_the_limit(client):
    # Tentativas com usuário duplicado (409) também consomem o limite
    await client.post("/users/", json=payload(0))
    for _ in range(SIGNUP_LIMIT - 1):
        response = await client.post("/users/", json=payload(0))
        assert response.status_code == status.HTTP_409_CONFLICT

    response = await client.post("/users/", json=payload(1))

    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


async def test_limit_is_per_client_ip(client):
    for i in range(SIGNUP_LIMIT + 1):
        await client.post("/users/", json=payload(i))

    async with client_from("198.51.100.20") as other_client:
        response = await other_client.post("/users/", json=payload(100))

    assert response.status_code == status.HTTP_201_CREATED


async def test_forwarded_header_does_not_bypass_limit(client):
    for i in range(SIGNUP_LIMIT):
        await client.post("/users/", json=payload(i))

    response = await client.post(
        "/users/",
        json=payload(SIGNUP_LIMIT),
        headers={"X-Forwarded-For": "192.0.2.99"},
    )

    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


async def test_other_endpoints_are_not_limited(client):
    for i in range(SIGNUP_LIMIT + 1):
        await client.post("/users/", json=payload(i))

    response = await client.get("/healthcheck/")

    assert response.status_code == status.HTTP_200_OK


def test_limiter_is_disabled_in_testing_env_by_default():
    # Os demais testes da API não devem esbarrar no limite
    assert settings.RATE_LIMIT_ENABLED is False
