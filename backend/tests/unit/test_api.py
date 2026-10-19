from collections.abc import AsyncIterator

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from application.use_cases.create_user import CreateUserUseCase
from infrastructure.web.dependencies import get_create_user_use_case
from main import app
from tests.fakes import FakePasswordHasher, FakeUserRepository

pytestmark = pytest.mark.anyio

PAYLOAD = {
    "username": "joao",
    "email": "joao@example.com",
    "password": "senha-segura",
}


@pytest.fixture
def repository() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
async def client(repository) -> AsyncIterator[AsyncClient]:
    app.dependency_overrides[get_create_user_use_case] = lambda: CreateUserUseCase(
        repository=repository, password_hasher=FakePasswordHasher()
    )
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()


async def test_healthcheck(client):
    response = await client.get("/healthcheck/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}


async def test_create_user_returns_201_with_public_fields(client, repository):
    response = await client.post("/users/", json=PAYLOAD)

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert set(body) == {"uid", "username", "email", "created_at"}
    assert body["username"] == "joao"
    assert body["email"] == "joao@example.com"
    assert body["uid"] == str(repository.users[0].uid)


async def test_create_user_normalizes_input(client):
    response = await client.post(
        "/users/",
        json=PAYLOAD | {"username": " JoaO ", "email": "Joao@Example.COM"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["username"] == "JoaO"
    assert response.json()["email"] == "joao@example.com"


@pytest.mark.parametrize(
    "duplicate",
    [
        {"username": "outro", "email": "JOAO@example.com"},
        {"username": "Joao", "email": "outro@example.com"},
    ],
)
async def test_create_user_returns_409_for_duplicates(client, repository, duplicate):
    await client.post("/users/", json=PAYLOAD)

    response = await client.post("/users/", json=PAYLOAD | duplicate)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {
        "detail": "Já existe um usuário com esse e-mail ou username."
    }
    assert len(repository.users) == 1


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("username", "ab"),
        ("username", "joao silva"),
        ("email", "nao-e-email"),
        ("password", "curta"),
        ("password", "a" * 73),
    ],
)
async def test_create_user_returns_422_for_invalid_input(
    client, repository, field, value
):
    response = await client.post("/users/", json=PAYLOAD | {field: value})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["detail"][0]["loc"] == ["body", field]
    assert repository.users == []


@pytest.mark.parametrize("missing", ["username", "email", "password"])
async def test_create_user_returns_422_for_missing_field(client, missing):
    payload = {k: v for k, v in PAYLOAD.items() if k != missing}

    response = await client.post("/users/", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_validation_error_does_not_echo_submitted_values(client):
    response = await client.post(
        "/users/", json=PAYLOAD | {"password": "segredo", "username": "x"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "segredo" not in response.text
    errors = response.json()["detail"]
    assert {tuple(e["loc"]) for e in errors} == {
        ("body", "password"),
        ("body", "username"),
    }
    assert all({"type", "loc", "msg"} <= e.keys() for e in errors)
    assert all("input" not in e for e in errors)


async def test_validation_error_for_password_too_long_keeps_message(client):
    response = await client.post("/users/", json=PAYLOAD | {"password": "é" * 37})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "é" * 37 not in response.text
    assert "72 bytes" in response.json()["detail"][0]["msg"]
