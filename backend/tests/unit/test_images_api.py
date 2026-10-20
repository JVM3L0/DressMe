import io
from collections.abc import AsyncIterator

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient
from PIL import Image

from config import settings
from domain.entities.image import MAX_IMAGE_BYTES, THUMBNAIL_SIDE
from infrastructure.storage.local_image_storage import LocalImageStorage
from infrastructure.web.dependencies import (
    get_current_user,
    get_garment_repository,
    get_image_storage,
    get_photo_repository,
)
from infrastructure.web.media import IMAGE_CACHE_CONTROL
from main import app
from tests.fakes import FakeGarmentRepository, FakePhotoRepository, make_user
from tests.images import EXIF_GPS_IFD, jpeg_bytes, png_bytes

pytestmark = pytest.mark.anyio

ALICE = make_user(username="alice", email="alice@example.com")
BRUNO = make_user(username="bruno", email="bruno@example.com")


@pytest.fixture
def storage(tmp_path) -> LocalImageStorage:
    return LocalImageStorage(tmp_path)


@pytest.fixture
def photos() -> FakePhotoRepository:
    return FakePhotoRepository()


@pytest.fixture
def garments() -> FakeGarmentRepository:
    return FakeGarmentRepository()


@pytest.fixture
def current_user():
    """Usuário da sessão; os testes trocam o valor para simular outra pessoa"""
    return {"user": ALICE}


@pytest.fixture
async def client(storage, photos, garments, current_user) -> AsyncIterator[AsyncClient]:
    app.dependency_overrides[get_current_user] = lambda: current_user["user"]
    app.dependency_overrides[get_image_storage] = lambda: storage
    app.dependency_overrides[get_photo_repository] = lambda: photos
    app.dependency_overrides[get_garment_repository] = lambda: garments
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()


def upload(data: bytes, filename: str = "foto.jpg", content_type="image/jpeg"):
    return {"file": (filename, data, content_type)}


class TestPhotosApi:
    async def test_upload_returns_dimensions_and_strips_metadata(
        self, client, photos, storage
    ):
        response = await client.post("/photos/", files=upload(jpeg_bytes(40, 20)))

        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert set(body) == {"uid", "width", "height", "created_at"}
        assert (body["width"], body["height"]) == (40, 20)
        saved = storage.path(photos.items[0].image.key)
        assert EXIF_GPS_IFD not in Image.open(saved).getexif()

    async def test_file_name_and_declared_type_are_ignored(self, client, photos):
        # O tipo vem do conteúdo: um PNG enviado como "foto.jpg" continua PNG
        response = await client.post(
            "/photos/", files=upload(png_bytes(), "../../foto.jpg", "image/jpeg")
        )

        assert response.status_code == status.HTTP_201_CREATED
        key = photos.items[0].image.key
        assert key.startswith("photos/") and key.endswith(".png")
        assert "foto" not in key

    async def test_list_returns_newest_first(self, client):
        first = (await client.post("/photos/", files=upload(jpeg_bytes()))).json()
        second = (await client.post("/photos/", files=upload(jpeg_bytes()))).json()

        response = await client.get("/photos/")

        assert [p["uid"] for p in response.json()] == [second["uid"], first["uid"]]

    async def test_image_is_served_with_private_cache(self, client):
        uid = (await client.post("/photos/", files=upload(png_bytes()))).json()["uid"]

        response = await client.get(f"/photos/{uid}/image")

        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "image/png"
        assert response.headers["cache-control"] == IMAGE_CACHE_CONTROL
        assert Image.open(io.BytesIO(response.content)).format == "PNG"

    async def test_thumbnail_is_smaller_and_kept_private(self, client, photos, storage):
        big = jpeg_bytes(1600, 1200)
        uid = (await client.post("/photos/", files=upload(big))).json()["uid"]

        response = await client.get(f"/photos/{uid}/thumbnail")

        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "image/jpeg"
        assert response.headers["cache-control"] == IMAGE_CACHE_CONTROL
        assert max(Image.open(io.BytesIO(response.content)).size) == THUMBNAIL_SIDE
        full = await client.get(f"/photos/{uid}/image")
        assert len(response.content) < len(full.content)
        # As duas versões ficam no disco, com chaves derivadas
        image = photos.items[0].image
        assert storage.path(image.key).exists()
        assert storage.path(image.thumbnail_key).exists()

    async def test_thumbnail_behind_nginx_points_to_the_thumbnail_file(
        self, client, photos, monkeypatch
    ):
        monkeypatch.setattr(settings, "MEDIA_ACCEL_REDIRECT", True)
        uid = (await client.post("/photos/", files=upload(jpeg_bytes()))).json()["uid"]

        response = await client.get(f"/photos/{uid}/thumbnail")

        key = photos.items[0].image.thumbnail_key
        assert response.headers["x-accel-redirect"] == f"/_media/{key}"

    async def test_behind_nginx_the_api_only_authorizes(
        self, client, photos, monkeypatch
    ):
        monkeypatch.setattr(settings, "MEDIA_ACCEL_REDIRECT", True)
        uid = (await client.post("/photos/", files=upload(jpeg_bytes()))).json()["uid"]

        response = await client.get(f"/photos/{uid}/image")

        assert response.status_code == status.HTTP_200_OK
        key = photos.items[0].image.key
        assert response.headers["x-accel-redirect"] == f"/_media/{key}"
        assert response.content == b""

    async def test_delete_removes_photo_and_file(self, client, photos, storage):
        uid = (await client.post("/photos/", files=upload(jpeg_bytes()))).json()["uid"]
        image = photos.items[0].image
        paths = [storage.path(image.key), storage.path(image.thumbnail_key)]

        response = await client.delete(f"/photos/{uid}")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not any(path.exists() for path in paths)
        assert (await client.get("/photos/")).json() == []
        assert (await client.get(f"/photos/{uid}/image")).status_code == 404

    async def test_other_users_photo_does_not_exist_for_them(
        self, client, current_user, photos
    ):
        uid = (await client.post("/photos/", files=upload(jpeg_bytes()))).json()["uid"]
        current_user["user"] = BRUNO

        assert (await client.get("/photos/")).json() == []
        for response in (
            await client.get(f"/photos/{uid}/image"),
            await client.get(f"/photos/{uid}/thumbnail"),
            await client.delete(f"/photos/{uid}"),
        ):
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json() == {"detail": "Não encontrado."}
        assert len(photos.items) == 1

    async def test_rejects_files_over_10_mb(self, client, photos, storage):
        response = await client.post(
            "/photos/", files=upload(b"\xff" * (MAX_IMAGE_BYTES + 1))
        )

        assert response.status_code == status.HTTP_413_CONTENT_TOO_LARGE
        assert response.json() == {"detail": "A imagem passa de 10 MB."}
        assert photos.items == []
        assert list(storage.root.iterdir()) == []

    @pytest.mark.parametrize(
        ("data", "filename"),
        [
            (b"GIF89a...", "foto.gif"),
            (b"<svg xmlns='http://www.w3.org/2000/svg'></svg>", "foto.svg"),
            (b"MZ\x90\x00", "foto.jpg"),  # executável com extensão de imagem
        ],
    )
    async def test_rejects_non_images(self, client, photos, data, filename):
        response = await client.post("/photos/", files=upload(data, filename))

        assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        assert response.json() == {"detail": "Envie uma imagem JPEG ou PNG."}
        assert photos.items == []

    async def test_upload_without_file_returns_422(self, client):
        response = await client.post("/photos/", data={"x": "1"})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_invalid_uid_returns_422(self, client):
        response = await client.get("/photos/nao-e-uuid/image")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestGarmentsApi:
    async def test_add_with_category_and_name(self, client):
        response = await client.post(
            "/garments/",
            files=upload(png_bytes(), "camisa.png", "image/png"),
            data={"category": "top", "name": "  Camisa de linho "},
        )

        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert set(body) == {"uid", "category", "name", "width", "height", "created_at"}
        assert body["category"] == "top"
        assert body["name"] == "Camisa de linho"

    async def test_name_is_optional(self, client):
        response = await client.post(
            "/garments/", files=upload(jpeg_bytes()), data={"category": "footwear"}
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["name"] is None

    @pytest.mark.parametrize(
        "data",
        [{}, {"category": "chapeu"}, {"category": "top", "name": "x" * 61}],
    )
    async def test_rejects_invalid_fields(self, client, garments, data):
        response = await client.post(
            "/garments/", files=upload(jpeg_bytes()), data=data
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert garments.items == []

    async def test_list_filters_by_category(self, client):
        for category in ("top", "bottom", "top"):
            await client.post(
                "/garments/", files=upload(jpeg_bytes()), data={"category": category}
            )

        all_items = (await client.get("/garments/")).json()
        tops = (await client.get("/garments/", params={"category": "top"})).json()

        assert len(all_items) == 3
        assert [g["category"] for g in tops] == ["top", "top"]
        invalid = await client.get("/garments/", params={"category": "chapeu"})
        assert invalid.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_image_and_delete_respect_owner(self, client, current_user, storage):
        uid = (
            await client.post(
                "/garments/", files=upload(jpeg_bytes()), data={"category": "top"}
            )
        ).json()["uid"]

        current_user["user"] = BRUNO
        for suffix in ("/image", "/thumbnail", ""):
            method = client.delete if suffix == "" else client.get
            assert (await method(f"/garments/{uid}{suffix}")).status_code == 404

        current_user["user"] = ALICE
        assert (await client.get(f"/garments/{uid}/image")).status_code == 200
        assert (await client.get(f"/garments/{uid}/thumbnail")).status_code == 200
        assert (await client.delete(f"/garments/{uid}")).status_code == 204
        assert list(storage.root.rglob("*.jpg")) == []


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/photos/"),
        ("POST", "/photos/"),
        ("GET", "/photos/00000000-0000-0000-0000-000000000001/image"),
        ("GET", "/photos/00000000-0000-0000-0000-000000000001/thumbnail"),
        ("DELETE", "/photos/00000000-0000-0000-0000-000000000001"),
        ("GET", "/garments/"),
        ("POST", "/garments/"),
        ("GET", "/garments/00000000-0000-0000-0000-000000000001/image"),
        ("GET", "/garments/00000000-0000-0000-0000-000000000001/thumbnail"),
        ("DELETE", "/garments/00000000-0000-0000-0000-000000000001"),
    ],
)
async def test_every_image_route_requires_a_session(method, path):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.request(method, path)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
