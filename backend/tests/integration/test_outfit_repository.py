import pytest
from sqlalchemy import delete, func, select, text
from sqlalchemy.exc import IntegrityError

from domain.entities.garment import Garment
from domain.entities.outfit import Outfit
from domain.enums.garment_category import GarmentCategory as C
from infrastructure.persistence.models.garment_model import GarmentOrm
from infrastructure.persistence.models.outfit_model import outfit_garments
from infrastructure.persistence.models.user_model import UserOrm
from infrastructure.repositories.sqlalchemy_garment_repository import (
    SQLAlchemyGarmentRepository,
)
from infrastructure.repositories.sqlalchemy_outfit_repository import (
    SQLAlchemyOutfitRepository,
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
def outfits(session) -> SQLAlchemyOutfitRepository:
    return SQLAlchemyOutfitRepository(session)


@pytest.fixture
def garments(session) -> SQLAlchemyGarmentRepository:
    return SQLAlchemyGarmentRepository(session)


async def add_garment(garments, owner, category=C.TOP) -> Garment:
    return await garments.save(
        Garment(owner_id=owner.uid, category=category, image=make_stored_image())
    )


async def save_outfit(outfits, owner, name, *garments) -> Outfit:
    return await outfits.save(
        Outfit(owner_id=owner.uid, name=name, garment_ids=[g.uid for g in garments])
    )


async def link_count(session) -> int:
    return await session.scalar(select(func.count()).select_from(outfit_garments))


async def test_save_and_list_round_trip(outfits, garments, alice):
    top = await add_garment(garments, alice, C.TOP)
    shoes = await add_garment(garments, alice, C.FOOTWEAR)

    saved = await outfits.save(
        Outfit(owner_id=alice.uid, name="Look", garment_ids=[top.uid, shoes.uid])
    )

    assert sorted(saved.garment_ids) == sorted([top.uid, shoes.uid])
    assert await outfits.list_by_owner(alice.uid) == [saved]
    assert await outfits.get_for_owner(saved.uid, alice.uid) == saved


async def test_list_is_per_owner_newest_first(outfits, garments, alice, bruno):
    top = await add_garment(garments, alice)
    old = await save_outfit(outfits, alice, "Velho", top)
    new = await save_outfit(outfits, alice, "Novo", top)
    other = await add_garment(garments, bruno)
    await save_outfit(outfits, bruno, "Dele", other)

    listed = await outfits.list_by_owner(alice.uid)

    assert {o.uid for o in listed} == {old.uid, new.uid}
    assert await outfits.get_for_owner(old.uid, bruno.uid) is None


async def test_update_replaces_name_and_links(outfits, garments, alice, session):
    top = await add_garment(garments, alice, C.TOP)
    shoes = await add_garment(garments, alice, C.FOOTWEAR)
    outfit = await outfits.save(
        Outfit(owner_id=alice.uid, name="Look", garment_ids=[top.uid])
    )

    updated = await outfits.update(
        Outfit(
            uid=outfit.uid,
            owner_id=alice.uid,
            name="Novo nome",
            garment_ids=[shoes.uid],
            created_at=outfit.created_at,
        )
    )

    assert updated.name == "Novo nome"
    assert updated.garment_ids == [shoes.uid]
    assert await link_count(session) == 1


async def test_an_outfit_keeps_four_accessories_and_the_rest(outfits, garments, alice):
    hats = [await add_garment(garments, alice, C.ACCESSORY) for _ in range(4)]
    top = await add_garment(garments, alice, C.TOP)
    ids = [top.uid, *[hat.uid for hat in hats]]

    saved = await outfits.save(Outfit(owner_id=alice.uid, name="Look", garment_ids=ids))

    again = await outfits.get_for_owner(saved.uid, alice.uid)
    assert again is not None
    assert sorted(again.garment_ids) == sorted(ids)


async def test_deleting_an_outfit_keeps_its_garments(outfits, garments, alice, session):
    top = await add_garment(garments, alice)
    outfit = await outfits.save(
        Outfit(owner_id=alice.uid, name="Look", garment_ids=[top.uid])
    )

    await outfits.delete(outfit)

    assert await link_count(session) == 0
    assert await garments.get_for_owner(top.uid, alice.uid) is not None


async def test_deleting_a_garment_removes_it_from_the_outfit(
    outfits, garments, alice, session
):
    top = await add_garment(garments, alice, C.TOP)
    shoes = await add_garment(garments, alice, C.FOOTWEAR)
    outfit = await outfits.save(
        Outfit(owner_id=alice.uid, name="Look", garment_ids=[top.uid, shoes.uid])
    )

    await garments.delete(top)
    session.expire_all()

    again = await outfits.get_for_owner(outfit.uid, alice.uid)
    assert again is not None
    assert again.garment_ids == [shoes.uid]


async def test_deleting_the_user_deletes_outfits_and_links(
    outfits, garments, alice, session
):
    top = await add_garment(garments, alice)
    await outfits.save(Outfit(owner_id=alice.uid, name="Look", garment_ids=[top.uid]))

    await session.execute(delete(UserOrm).where(UserOrm.uid == alice.uid))

    assert await link_count(session) == 0
    assert await session.scalar(select(func.count()).select_from(GarmentOrm)) == 0


async def test_a_garment_cannot_be_linked_twice_to_the_same_outfit(
    outfits, garments, alice, session
):
    top = await add_garment(garments, alice)
    outfit = await outfits.save(
        Outfit(owner_id=alice.uid, name="Look", garment_ids=[top.uid])
    )

    with pytest.raises(IntegrityError):
        await session.execute(
            text("INSERT INTO outfit_garments VALUES (:o, :g)"),
            {"o": outfit.uid, "g": top.uid},
        )


async def test_list_garments_by_ids_only_returns_the_owners(garments, alice, bruno):
    mine = await add_garment(garments, alice)
    theirs = await add_garment(garments, bruno)

    found = await garments.list_by_ids([mine.uid, theirs.uid], alice.uid)

    assert [g.uid for g in found] == [mine.uid]
    assert await garments.list_by_ids([], alice.uid) == []
