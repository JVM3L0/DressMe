import uuid

import pytest

from application.services.image_upload import ImageUploader
from application.use_cases.garments import (
    AddGarmentUseCase,
    DeleteGarmentUseCase,
    GetGarmentUseCase,
    ListGarmentsUseCase,
)
from application.use_cases.photos import (
    DeletePhotoUseCase,
    GetPhotoUseCase,
    ListPhotosUseCase,
    UploadPhotoUseCase,
)
from domain.entities.image import MAX_IMAGE_BYTES
from domain.enums.garment_category import GarmentCategory
from domain.exceptions.common import ResourceNotFoundError
from domain.exceptions.image import ImageTooLargeError, InvalidImageError
from tests.fakes import (
    FakeGarmentRepository,
    FakeImageProcessor,
    FakeImageStorage,
    FakePhotoRepository,
)

pytestmark = pytest.mark.anyio

OWNER = uuid.uuid4()
OTHER = uuid.uuid4()


@pytest.fixture
def storage() -> FakeImageStorage:
    return FakeImageStorage()


@pytest.fixture
def uploader(storage) -> ImageUploader:
    return ImageUploader(processor=FakeImageProcessor(), storage=storage)


@pytest.fixture
def photos() -> FakePhotoRepository:
    return FakePhotoRepository()


@pytest.fixture
def garments() -> FakeGarmentRepository:
    return FakeGarmentRepository()


class TestImageUploader:
    async def test_stores_processed_image_under_generated_key(self, uploader, storage):
        async def persist(image):
            return image

        image = await uploader.store(b"foto", "photos", persist)

        assert image.key.startswith("photos/") and image.key.endswith(".jpg")
        uuid.UUID(image.key.removeprefix("photos/").removesuffix(".jpg"))
        assert storage.files == {
            image.key: b"processed:foto",
            image.thumbnail_key: b"thumbnail:foto",
        }
        assert (image.width, image.height) == (300, 400)

    async def test_rejects_too_large_before_processing(self, uploader, storage):
        with pytest.raises(ImageTooLargeError):
            await uploader.store(b"x" * (MAX_IMAGE_BYTES + 1), "photos", None)

        assert storage.files == {}

    async def test_accepts_exactly_the_limit(self, uploader):
        async def persist(image):
            return image

        await uploader.store(b"x" * MAX_IMAGE_BYTES, "photos", persist)

    async def test_invalid_image_stores_nothing(self, uploader, storage):
        with pytest.raises(InvalidImageError):
            await uploader.store(b"invalid", "photos", None)

        assert storage.files == {}

    async def test_removes_files_when_persisting_fails(self, uploader, storage):
        async def persist(image):
            raise RuntimeError("banco fora")

        with pytest.raises(RuntimeError):
            await uploader.store(b"foto", "photos", persist)

        assert storage.files == {}

    async def test_removes_the_image_when_saving_the_thumbnail_fails(self, uploader):
        class StorageFailingOnThumbnail(FakeImageStorage):
            async def save(self, key: str, data: bytes) -> None:
                if "_thumb" in key:
                    raise OSError("disco cheio")
                await super().save(key, data)

        storage = StorageFailingOnThumbnail()
        uploader = ImageUploader(processor=FakeImageProcessor(), storage=storage)

        with pytest.raises(OSError):
            await uploader.store(b"foto", "photos", None)

        assert storage.files == {}


class TestPhotos:
    async def test_upload_saves_photo_of_owner(self, photos, uploader, storage):
        photo = await UploadPhotoUseCase(photos, uploader).execute(OWNER, b"foto")

        assert photos.items == [photo]
        assert photo.owner_id == OWNER
        assert photo.image.key in storage.files

    async def test_list_returns_only_own_photos(self, photos, uploader):
        mine = await UploadPhotoUseCase(photos, uploader).execute(OWNER, b"a")
        await UploadPhotoUseCase(photos, uploader).execute(OTHER, b"b")

        assert await ListPhotosUseCase(photos).execute(OWNER) == [mine]

    async def test_get_of_other_owner_is_not_found(self, photos, uploader):
        photo = await UploadPhotoUseCase(photos, uploader).execute(OWNER, b"a")

        assert await GetPhotoUseCase(photos).execute(photo.uid, OWNER) == photo
        with pytest.raises(ResourceNotFoundError):
            await GetPhotoUseCase(photos).execute(photo.uid, OTHER)

    async def test_delete_removes_record_image_and_thumbnail(
        self, photos, uploader, storage
    ):
        photo = await UploadPhotoUseCase(photos, uploader).execute(OWNER, b"a")

        await DeletePhotoUseCase(photos, storage).execute(photo.uid, OWNER)

        assert photos.items == []
        assert storage.files == {}

    async def test_delete_of_other_owner_keeps_everything(
        self, photos, uploader, storage
    ):
        photo = await UploadPhotoUseCase(photos, uploader).execute(OWNER, b"a")

        with pytest.raises(ResourceNotFoundError):
            await DeletePhotoUseCase(photos, storage).execute(photo.uid, OTHER)

        assert photos.items == [photo]
        assert photo.image.key in storage.files


class TestGarments:
    async def test_add_saves_category_and_trimmed_name(self, garments, uploader):
        garment = await AddGarmentUseCase(garments, uploader).execute(
            OWNER, b"a", category=GarmentCategory.TOP, name="  Camisa azul  "
        )

        assert garment.category is GarmentCategory.TOP
        assert garment.name == "Camisa azul"
        assert garment.image.key.startswith("garments/")

    @pytest.mark.parametrize("name", [None, "", "   "])
    async def test_blank_name_becomes_none(self, garments, uploader, name):
        garment = await AddGarmentUseCase(garments, uploader).execute(
            OWNER, b"a", category=GarmentCategory.FOOTWEAR, name=name
        )

        assert garment.name is None

    async def test_list_filters_by_owner_and_category(self, garments, uploader):
        add = AddGarmentUseCase(garments, uploader).execute
        top = await add(OWNER, b"a", category=GarmentCategory.TOP)
        bottom = await add(OWNER, b"b", category=GarmentCategory.BOTTOM)
        await add(OTHER, b"c", category=GarmentCategory.TOP)

        listed = ListGarmentsUseCase(garments).execute
        assert {g.uid for g in await listed(OWNER)} == {top.uid, bottom.uid}
        assert await listed(OWNER, GarmentCategory.TOP) == [top]

    async def test_get_and_delete_respect_owner(self, garments, uploader, storage):
        garment = await AddGarmentUseCase(garments, uploader).execute(
            OWNER, b"a", category=GarmentCategory.ACCESSORY
        )

        with pytest.raises(ResourceNotFoundError):
            await GetGarmentUseCase(garments).execute(garment.uid, OTHER)
        with pytest.raises(ResourceNotFoundError):
            await DeleteGarmentUseCase(garments, storage).execute(garment.uid, OTHER)

        await DeleteGarmentUseCase(garments, storage).execute(garment.uid, OWNER)
        assert garments.items == []
        assert storage.files == {}
