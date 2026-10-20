import pendulum
import pytest
from sqlalchemy import delete, func, select, text
from sqlalchemy.exc import IntegrityError

from domain.entities.garment import Garment
from domain.entities.photo import Photo
from domain.enums.garment_category import GarmentCategory
from infrastructure.persistence.models.garment_model import GarmentOrm
from infrastructure.persistence.models.photo_model import PhotoOrm
from infrastructure.persistence.models.user_model import UserOrm
from infrastructure.repositories.sqlalchemy_garment_repository import (
    SQLAlchemyGarmentRepository,
)
from infrastructure.repositories.sqlalchemy_photo_repository import (
    SQLAlchemyPhotoRepository,
)
from infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from tests.fakes import make_stored_image, make_user

pytestmark = [pytest.mark.anyio, pytest.mark.integration]


@pytest.fixture
async def alice(session):
    return await SQLAlchemyUserRepository(session).save(make_user())


@pytest.fixture
async def bruno(session):
    user = make_user(username="bruno", email="bruno@example.com")
    return await SQLAlchemyUserRepository(session).save(user)


@pytest.fixture
def photos(session) -> SQLAlchemyPhotoRepository:
    return SQLAlchemyPhotoRepository(session)


@pytest.fixture
def garments(session) -> SQLAlchemyGarmentRepository:
    return SQLAlchemyGarmentRepository(session)


def minutes_ago(minutes: int):
    return pendulum.now("UTC").subtract(minutes=minutes)


class TestPhotoRepository:
    async def test_save_and_get_round_trip(self, photos, alice):
        photo = Photo(owner_id=alice.uid, image=make_stored_image(width=640))

        saved = await photos.save(photo)

        found = await photos.get_for_owner(photo.uid, alice.uid)
        assert found == saved
        assert found.image == photo.image

    async def test_get_of_other_owner_returns_none(self, photos, alice, bruno):
        photo = await photos.save(Photo(owner_id=alice.uid, image=make_stored_image()))

        assert await photos.get_for_owner(photo.uid, bruno.uid) is None

    async def test_list_by_owner_newest_first(self, photos, alice, bruno):
        old = await photos.save(
            Photo(
                owner_id=alice.uid, image=make_stored_image(), created_at=minutes_ago(5)
            )
        )
        new = await photos.save(Photo(owner_id=alice.uid, image=make_stored_image()))
        await photos.save(Photo(owner_id=bruno.uid, image=make_stored_image()))

        assert [p.uid for p in await photos.list_by_owner(alice.uid)] == [
            new.uid,
            old.uid,
        ]

    async def test_delete(self, photos, alice):
        photo = await photos.save(Photo(owner_id=alice.uid, image=make_stored_image()))

        await photos.delete(photo)

        assert await photos.list_by_owner(alice.uid) == []

    async def test_image_key_is_unique(self, photos, alice):
        image = make_stored_image()
        await photos.save(Photo(owner_id=alice.uid, image=image))

        with pytest.raises(IntegrityError):
            await photos.save(Photo(owner_id=alice.uid, image=image))


class TestGarmentRepository:
    async def test_save_and_filter_by_category(self, garments, alice):
        top = await garments.save(
            Garment(
                owner_id=alice.uid,
                category=GarmentCategory.TOP,
                name="Camisa",
                image=make_stored_image(key="garments/a.png", content_type="image/png"),
            )
        )
        await garments.save(
            Garment(
                owner_id=alice.uid,
                category=GarmentCategory.BOTTOM,
                image=make_stored_image(),
            )
        )

        assert len(await garments.list_by_owner(alice.uid)) == 2
        assert await garments.list_by_owner(alice.uid, GarmentCategory.TOP) == [top]
        assert top.category is GarmentCategory.TOP
        assert top.image.content_type == "image/png"

    async def test_category_is_stored_as_text(self, garments, alice, session):
        await garments.save(
            Garment(
                owner_id=alice.uid,
                category=GarmentCategory.ONE_PIECE,
                image=make_stored_image(),
            )
        )

        assert await session.scalar(select(GarmentOrm.category)) == "one_piece"

    async def test_database_rejects_unknown_category(self, session, alice):
        with pytest.raises(IntegrityError):
            await session.execute(
                text(
                    "INSERT INTO garments (uid, owner_id, category, image_key, "
                    "image_content_type, image_width, image_height) VALUES "
                    "(gen_random_uuid(), :owner, 'chapeu', 'k', 'image/png', 1, 1)"
                ),
                {"owner": alice.uid},
            )


async def test_deleting_user_deletes_their_photos_and_garments(
    session, photos, garments, alice
):
    await photos.save(Photo(owner_id=alice.uid, image=make_stored_image()))
    await garments.save(
        Garment(
            owner_id=alice.uid, category=GarmentCategory.TOP, image=make_stored_image()
        )
    )

    await session.execute(delete(UserOrm).where(UserOrm.uid == alice.uid))

    for model in (PhotoOrm, GarmentOrm):
        assert await session.scalar(select(func.count()).select_from(model)) == 0
