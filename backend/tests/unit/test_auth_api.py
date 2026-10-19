from collections.abc import AsyncIterator, Iterator

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient
from limits import parse

from config import settings
from infrastructure.web.dependencies import (
    SESSION_COOKIE,
    get_dummy_hash,
    get_password_hasher,
    get_token_service,
    get_user_repository,
)
from infrastructure.web.rate_limit import limiter
from main import app
from tests.fakes import FakePasswordHasher, FakeUserRepository

pytestmark = pytest.mark.anyio

SIGNUP = {"username": "joao", "email": "joao@example.com", "password": "senha-segura"}
CREDENTIALS = {"email": "joao@example.com", "password": "senha-segura"}


@pytest.fixture
def repository() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
async def client(repository) -> AsyncIterator[AsyncClient]:
    # Token real (JWTService): o cookie carrega um JWT de verdade
    app.dependency_overrides[get_user_repository] = lambda: repository
    app.dependency_overrides[get_password_hasher] = FakePasswordHasher
    app.dependency_overrides[get_dummy_hash] = lambda: "dummy"
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        assert (await client.post("/users/", json=SIGNUP)).status_code == 201
        yield client
    app.dependency_overrides.clear()


def session_cookie_header(response) -> str:
    [header] = [
        value
        for value in response.headers.get_list("set-cookie")
        if value.startswith(f"{SESSION_COOKIE}=")
    ]
    return header


async def test_login_returns_user_and_sets_session_cookie(client, repository):
    response = await client.post("/auth/login", json=CREDENTIALS)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["uid"] == str(repository.users[0].uid)
    assert "access_token" not in response.text  # o token fica só no cookie
    token = client.cookies[SESSION_COOKIE]
    assert get_token_service().verify_token(token) == repository.users[0].uid


async def test_session_cookie_is_httponly_strict_and_lasts_one_week(client):
    response = await client.post("/auth/login", json=CREDENTIALS)

    header = session_cookie_header(response).lower()
    assert "httponly" in header
    assert "samesite=strict" in header
    assert "path=/" in header
    assert f"max-age={7 * 24 * 60 * 60}" in header
    # No ambiente de testes não há HTTPS; em produção o cookie é `Secure`
    assert ("secure" in header.split("; ")) is settings.AUTH_COOKIE_SECURE


def test_session_lasts_one_week_by_default():
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 7 * 24 * 60


@pytest.mark.parametrize(
    "credentials",
    [
        CREDENTIALS | {"password": "senha-errada"},
        CREDENTIALS | {"email": "ninguem@example.com"},
    ],
)
async def test_login_rejects_bad_credentials_with_the_same_response(
    client, credentials
):
    response = await client.post("/auth/login", json=credentials)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "E-mail ou senha incorretos."}
    assert SESSION_COOKIE not in client.cookies


async def test_login_accepts_email_in_any_case(client):
    response = await client.post(
        "/auth/login", json=CREDENTIALS | {"email": "JOAO@Example.com"}
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "joao@example.com"},
        {"email": "nao-e-email", "password": "x"},
        {"email": "joao@example.com", "password": ""},
        {"email": "joao@example.com", "password": "a" * 1025},
    ],
)
async def test_login_returns_422_for_invalid_payload(client, payload):
    response = await client.post("/auth/login", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "input" not in response.text


async def test_me_returns_the_logged_in_user(client):
    await client.post("/auth/login", json=CREDENTIALS)

    response = await client.get("/users/me")

    assert response.status_code == status.HTTP_200_OK
    assert set(response.json()) == {"uid", "username", "email", "created_at"}
    assert response.json()["username"] == "joao"


async def test_me_without_session_returns_401(client):
    response = await client.get("/users/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Faça login para continuar."}


async def test_me_with_tampered_token_returns_401(client):
    await client.post("/auth/login", json=CREDENTIALS)
    client.cookies.set(SESSION_COOKIE, client.cookies[SESSION_COOKIE] + "x")

    response = await client.get("/users/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_me_ignores_bearer_header(client, repository):
    # A sessão vem só do cookie; um token no header não é aceito
    token = get_token_service().create_access_token(repository.users[0].uid)

    response = await client.get(
        "/users/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_logout_clears_the_session_cookie(client):
    await client.post("/auth/login", json=CREDENTIALS)

    response = await client.post("/auth/logout")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert "max-age=0" in session_cookie_header(response).lower()
    assert SESSION_COOKIE not in client.cookies
    assert (await client.get("/users/me")).status_code == 401


async def test_logout_without_session_is_harmless(client):
    response = await client.post("/auth/logout")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_openapi_documents_the_session_cookie():
    schemes = app.openapi()["components"]["securitySchemes"]

    assert schemes["APIKeyCookie"] == {
        "type": "apiKey",
        "in": "cookie",
        "name": SESSION_COOKIE,
        "description": "Sessão criada pelo login.",
    }


class TestLoginRateLimit:
    LIMIT = parse(settings.RATE_LIMIT_LOGIN).amount

    @pytest.fixture(autouse=True)
    def enabled_limiter(self) -> Iterator[None]:
        limiter.reset()
        limiter.enabled = True
        yield
        limiter.enabled = settings.RATE_LIMIT_ENABLED
        limiter.reset()

    def test_default_login_limit_is_10_per_minute(self):
        assert settings.RATE_LIMIT_LOGIN == "10/minute"

    async def test_failed_attempts_count_towards_the_limit(self, client):
        wrong = CREDENTIALS | {"password": "senha-errada"}
        for _ in range(self.LIMIT):
            assert (await client.post("/auth/login", json=wrong)).status_code == 401

        response = await client.post("/auth/login", json=CREDENTIALS)

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert response.headers["Retry-After"] == "60"

    async def test_login_and_signup_limits_are_separate(self, client):
        # O cadastro do fixture já consumiu uma tentativa de cadastro, não de login
        for _ in range(self.LIMIT):
            assert (
                await client.post("/auth/login", json=CREDENTIALS)
            ).status_code == 200
