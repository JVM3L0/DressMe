import uuid
from collections.abc import AsyncIterator

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from domain.enums.garment_category import GarmentCategory as C
from infrastructure.web.dependencies import (
    get_current_user,
    get_garment_repository,
    get_outfit_repository,
)
from main import app
from tests.fakes import (
    FakeGarmentRepository,
    FakeOutfitRepository,
    make_garment,
    make_user,
)

pytestmark = pytest.mark.anyio

ALICE = make_user(username="alice", email="alice@example.com")
BRUNO = make_user(username="bruno", email="bruno@example.com")


@pytest.fixture
def garments() -> FakeGarmentRepository:
    return FakeGarmentRepository()


@pytest.fixture
def outfits() -> FakeOutfitRepository:
    return FakeOutfitRepository()


@pytest.fixture
def current_user():
    return {"user": ALICE}


@pytest.fixture
async def client(garments, outfits, current_user) -> AsyncIterator[AsyncClient]:
    app.dependency_overrides[get_current_user] = lambda: current_user["user"]
    app.dependency_overrides[get_garment_repository] = lambda: garments
    app.dependency_overrides[get_outfit_repository] = lambda: outfits
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()


async def piece(garments, category, owner=ALICE):
    garment = await garments.save(make_garment(owner.uid, category))
    return str(garment.uid)


async def create(client, name, *garment_ids):
    response = await client.post(
        "/outfits/", json={"name": name, "garment_ids": list(garment_ids)}
    )
    return response.json()


async def test_create_returns_the_outfit(client, garments):
    top = await piece(garments, C.TOP)
    shoes = await piece(garments, C.FOOTWEAR)

    response = await client.post(
        "/outfits/", json={"name": "  Look de sexta ", "garment_ids": [top, shoes]}
    )

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert set(body) == {"uid", "name", "garment_ids", "created_at"}
    assert body["name"] == "Look de sexta"
    assert sorted(body["garment_ids"]) == sorted([top, shoes])


async def test_list_returns_newest_first_and_only_own(client, garments, current_user):
    top = await piece(garments, C.TOP)
    first = await create(client, "A", top)
    second = await create(client, "B", top)

    listed = (await client.get("/outfits/")).json()
    assert [o["uid"] for o in listed] == [second["uid"], first["uid"]]

    current_user["user"] = BRUNO
    assert (await client.get("/outfits/")).json() == []


@pytest.mark.parametrize(
    ("categories", "code", "message"),
    [
        (
            (C.TOP, C.TOP),
            "outfit_duplicate_category",
            "Use no máximo uma peça por categoria.",
        ),
        (
            (C.ONE_PIECE, C.BOTTOM),
            "outfit_one_piece_conflict",
            "Uma peça única não combina com parte de cima ou de baixo.",
        ),
    ],
)
async def test_create_rejects_invalid_compositions(
    client, garments, outfits, categories, code, message
):
    ids = [await piece(garments, category) for category in categories]

    response = await client.post("/outfits/", json={"name": "Look", "garment_ids": ids})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json() == {"detail": message, "code": code}
    assert outfits.items == []


async def test_create_accepts_four_accessories_and_rejects_a_fifth(
    client, garments, outfits
):
    hats = [await piece(garments, C.ACCESSORY) for _ in range(5)]

    async def create(ids):
        return await client.post("/outfits/", json={"name": "Look", "garment_ids": ids})

    ok = await create(hats[:4])
    too_many = await create(hats)

    assert ok.status_code == status.HTTP_201_CREATED
    assert too_many.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert too_many.json() == {
        "detail": "Use no máximo 4 acessórios.",
        "code": "outfit_too_many_accessories",
    }
    assert len(outfits.items) == 1


async def test_create_with_garment_of_another_user_says_it_does_not_exist(
    client, garments
):
    foreign = await piece(garments, C.TOP, owner=BRUNO)

    response = await client.post(
        "/outfits/", json={"name": "Look", "garment_ids": [foreign]}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["code"] == "outfit_unknown_garment"


@pytest.mark.parametrize(
    "payload",
    [
        {"garment_ids": []},
        {"name": "Look", "garment_ids": []},
        {"name": "", "garment_ids": [str(uuid.uuid4())]},
        {"name": "   ", "garment_ids": [str(uuid.uuid4())]},
        {"name": "x" * 61, "garment_ids": [str(uuid.uuid4())]},
        {"name": "Look", "garment_ids": ["nao-e-uuid"]},
        {"name": "Look", "garment_ids": [str(uuid.uuid4())] * 2},
        {"name": "Look", "garment_ids": [str(uuid.uuid4()) for _ in range(9)]},
    ],
)
async def test_create_returns_422_for_invalid_payload(client, outfits, payload):
    response = await client.post("/outfits/", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert isinstance(response.json()["detail"], list)
    assert outfits.items == []


async def test_update_replaces_name_and_garments(client, garments):
    top = await piece(garments, C.TOP)
    dress = await piece(garments, C.ONE_PIECE)
    uid = (await create(client, "A", top))["uid"]

    response = await client.put(
        f"/outfits/{uid}", json={"name": "Vestido", "garment_ids": [dress]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["uid"] == uid
    assert response.json()["name"] == "Vestido"
    assert response.json()["garment_ids"] == [dress]


async def test_update_and_delete_of_other_users_outfit_return_404(
    client, garments, current_user
):
    top = await piece(garments, C.TOP)
    uid = (await create(client, "A", top))["uid"]
    current_user["user"] = BRUNO

    put = await client.put(f"/outfits/{uid}", json={"name": "X", "garment_ids": [top]})
    delete = await client.delete(f"/outfits/{uid}")

    assert put.status_code == delete.status_code == status.HTTP_404_NOT_FOUND
    assert delete.json() == {"detail": "Não encontrado."}


async def test_delete_removes_outfit_but_not_garments(client, garments):
    top = await piece(garments, C.TOP)
    uid = (await create(client, "A", top))["uid"]

    response = await client.delete(f"/outfits/{uid}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert (await client.get("/outfits/")).json() == []
    assert len(garments.items) == 1


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/outfits/"),
        ("POST", "/outfits/"),
        ("PUT", "/outfits/00000000-0000-0000-0000-000000000001"),
        ("DELETE", "/outfits/00000000-0000-0000-0000-000000000001"),
    ],
)
async def test_every_outfit_route_requires_a_session(method, path):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.request(method, path)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
