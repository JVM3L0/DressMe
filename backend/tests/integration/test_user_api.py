from collections.abc import AsyncIterator

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from infrastructure.auth.bcrypt_hasher import BcryptHasher
from infrastructure.persistence.database import get_db_session
from infrastructure.persistence.models.user_model import UserOrm
from infrastructure.web.dependencies import get_password_hasher
from main import app

pytestmark = [pytest.mark.anyio, pytest.mark.integration]

PAYLOAD = {
    "username": "Joao",
    "email": "Joao@Example.com",
    "password": "senha-segura",
}


@pytest.fixture
async def client(session) -> AsyncIterator[AsyncClient]:
    """Aplicação completa (rotas, use case, repositório e bcrypt reais) sobre
    a sessão isolada de teste."""

    async def override_session():
        yield session

    app.dependency_overrides[get_db_session] = override_session
    app.dependency_overrides[get_password_hasher] = lambda: BcryptHasher(rounds=4)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()


async def test_create_user_persists_normalized_user_with_hashed_password(
    client, session
):
    response = await client.post("/users/", json=PAYLOAD)

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()

    row = (await session.scalars(select(UserOrm))).one()
    assert str(row.uid) == body["uid"]
    assert row.username == body["username"] == "Joao"
    assert row.email == body["email"] == "joao@example.com"
    assert row.hashed_password.startswith("$2b$")
    assert await BcryptHasher().verify("senha-segura", row.hashed_password)


@pytest.mark.parametrize(
    "duplicate",
    [
        {"username": "outro", "email": "JOAO@example.com"},
        {"username": "JOAO", "email": "outro@example.com"},
    ],
)
async def test_create_user_returns_409_for_duplicates_ignoring_case(
    client, session, duplicate
):
    assert (await client.post("/users/", json=PAYLOAD)).status_code == 201

    response = await client.post("/users/", json=PAYLOAD | duplicate)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert len((await session.scalars(select(UserOrm))).all()) == 1


async def test_create_user_returns_422_for_password_longer_than_72_bytes(
    client, session
):
    response = await client.post("/users/", json=PAYLOAD | {"password": "é" * 37})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert (await session.scalars(select(UserOrm))).all() == []


async def test_signup_login_me_and_logout_with_real_bcrypt_and_jwt(client):
    assert (await client.post("/users/", json=PAYLOAD)).status_code == 201

    login = await client.post(
        "/auth/login", json={"email": "joao@EXAMPLE.com", "password": "senha-segura"}
    )
    assert login.status_code == status.HTTP_200_OK

    me = await client.get("/users/me")
    assert me.status_code == status.HTTP_200_OK
    assert me.json() == login.json()
    assert me.json()["username"] == "Joao"

    assert (await client.post("/auth/logout")).status_code == 204
    assert (await client.get("/users/me")).status_code == 401


async def test_login_with_wrong_password_returns_401(client):
    await client.post("/users/", json=PAYLOAD)

    response = await client.post(
        "/auth/login", json={"email": "joao@example.com", "password": "senha-errada"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_session_of_deleted_user_is_rejected(client, session):
    await client.post("/users/", json=PAYLOAD)
    await client.post(
        "/auth/login", json={"email": "joao@example.com", "password": "senha-segura"}
    )

    await session.execute(delete(UserOrm))

    assert (await client.get("/users/me")).status_code == 401
