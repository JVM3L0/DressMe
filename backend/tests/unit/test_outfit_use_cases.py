import uuid

import pytest

from application.use_cases.outfits import (
    CreateOutfitUseCase,
    DeleteOutfitUseCase,
    ListOutfitsUseCase,
    UpdateOutfitUseCase,
)
from domain.enums.garment_category import GarmentCategory as C
from domain.exceptions.common import ResourceNotFoundError
from domain.exceptions.outfit import InvalidOutfitError, OutfitProblem
from tests.fakes import FakeGarmentRepository, FakeOutfitRepository, make_garment

pytestmark = pytest.mark.anyio

OWNER = uuid.uuid4()
OTHER = uuid.uuid4()


@pytest.fixture
def garments() -> FakeGarmentRepository:
    return FakeGarmentRepository()


@pytest.fixture
def outfits() -> FakeOutfitRepository:
    return FakeOutfitRepository()


async def add(garments, owner, category):
    return await garments.save(make_garment(owner, category))


class TestCreate:
    async def test_saves_outfit_of_the_owner(self, outfits, garments):
        top = await add(garments, OWNER, C.TOP)
        bottom = await add(garments, OWNER, C.BOTTOM)

        outfit = await CreateOutfitUseCase(outfits, garments).execute(
            OWNER, "  Look de sexta ", [top.uid, bottom.uid]
        )

        assert outfits.items == [outfit]
        assert outfit.owner_id == OWNER
        assert outfit.name == "Look de sexta"
        assert outfit.garment_ids == [top.uid, bottom.uid]

    async def test_rejects_garment_of_another_user_as_unknown(self, outfits, garments):
        foreign = await add(garments, OTHER, C.TOP)

        with pytest.raises(InvalidOutfitError) as exc:
            await CreateOutfitUseCase(outfits, garments).execute(
                OWNER, "Look", [foreign.uid]
            )

        assert exc.value.problem is OutfitProblem.UNKNOWN_GARMENT
        assert outfits.items == []

    async def test_rejects_garment_that_does_not_exist(self, outfits, garments):
        with pytest.raises(InvalidOutfitError) as exc:
            await CreateOutfitUseCase(outfits, garments).execute(
                OWNER, "Look", [uuid.uuid4()]
            )

        assert exc.value.problem is OutfitProblem.UNKNOWN_GARMENT

    async def test_rejects_two_garments_of_the_same_category(self, outfits, garments):
        first = await add(garments, OWNER, C.TOP)
        second = await add(garments, OWNER, C.TOP)

        with pytest.raises(InvalidOutfitError) as exc:
            await CreateOutfitUseCase(outfits, garments).execute(
                OWNER, "Look", [first.uid, second.uid]
            )

        assert exc.value.problem is OutfitProblem.DUPLICATE_CATEGORY

    async def test_rejects_the_same_garment_twice(self, outfits, garments):
        hat = await add(garments, OWNER, C.ACCESSORY)

        with pytest.raises(InvalidOutfitError) as exc:
            await CreateOutfitUseCase(outfits, garments).execute(
                OWNER, "Look", [hat.uid, hat.uid]
            )

        assert exc.value.problem is OutfitProblem.DUPLICATE_GARMENT

    async def test_accepts_up_to_four_different_accessories(self, outfits, garments):
        hats = [await add(garments, OWNER, C.ACCESSORY) for _ in range(4)]

        outfit = await CreateOutfitUseCase(outfits, garments).execute(
            OWNER, "Look", [hat.uid for hat in hats]
        )

        assert outfit.garment_ids == [hat.uid for hat in hats]

    async def test_rejects_a_fifth_accessory(self, outfits, garments):
        hats = [await add(garments, OWNER, C.ACCESSORY) for _ in range(5)]

        with pytest.raises(InvalidOutfitError) as exc:
            await CreateOutfitUseCase(outfits, garments).execute(
                OWNER, "Look", [hat.uid for hat in hats]
            )

        assert exc.value.problem is OutfitProblem.TOO_MANY_ACCESSORIES

    async def test_rejects_one_piece_with_top(self, outfits, garments):
        dress = await add(garments, OWNER, C.ONE_PIECE)
        top = await add(garments, OWNER, C.TOP)

        with pytest.raises(InvalidOutfitError) as exc:
            await CreateOutfitUseCase(outfits, garments).execute(
                OWNER, "Look", [dress.uid, top.uid]
            )

        assert exc.value.problem is OutfitProblem.ONE_PIECE_CONFLICT

    async def test_rejects_empty_outfit(self, outfits, garments):
        with pytest.raises(InvalidOutfitError) as exc:
            await CreateOutfitUseCase(outfits, garments).execute(OWNER, "Look", [])

        assert exc.value.problem is OutfitProblem.EMPTY


class TestListUpdateDelete:
    async def test_list_returns_only_own_outfits(self, outfits, garments):
        mine = await add(garments, OWNER, C.TOP)
        theirs = await add(garments, OTHER, C.TOP)
        create = CreateOutfitUseCase(outfits, garments).execute
        own = await create(OWNER, "Meu", [mine.uid])
        await create(OTHER, "Dela", [theirs.uid])

        assert await ListOutfitsUseCase(outfits).execute(OWNER) == [own]

    async def test_update_changes_name_and_garments(self, outfits, garments):
        top = await add(garments, OWNER, C.TOP)
        shoes = await add(garments, OWNER, C.FOOTWEAR)
        outfit = await CreateOutfitUseCase(outfits, garments).execute(
            OWNER, "Look", [top.uid]
        )

        updated = await UpdateOutfitUseCase(outfits, garments).execute(
            outfit.uid, OWNER, " Look novo ", [shoes.uid]
        )

        assert updated.uid == outfit.uid
        assert updated.name == "Look novo"
        assert updated.garment_ids == [shoes.uid]
        assert updated.created_at == outfit.created_at
        assert outfits.items == [updated]

    async def test_update_validates_the_new_composition(self, outfits, garments):
        top = await add(garments, OWNER, C.TOP)
        dress = await add(garments, OWNER, C.ONE_PIECE)
        outfit = await CreateOutfitUseCase(outfits, garments).execute(
            OWNER, "Look", [top.uid]
        )

        with pytest.raises(InvalidOutfitError):
            await UpdateOutfitUseCase(outfits, garments).execute(
                outfit.uid, OWNER, "Look", [top.uid, dress.uid]
            )

        assert outfits.items[0].garment_ids == [top.uid]

    async def test_update_and_delete_of_other_owner_are_not_found(
        self, outfits, garments
    ):
        top = await add(garments, OWNER, C.TOP)
        outfit = await CreateOutfitUseCase(outfits, garments).execute(
            OWNER, "Look", [top.uid]
        )

        with pytest.raises(ResourceNotFoundError):
            await UpdateOutfitUseCase(outfits, garments).execute(
                outfit.uid, OTHER, "Look", [top.uid]
            )
        with pytest.raises(ResourceNotFoundError):
            await DeleteOutfitUseCase(outfits).execute(outfit.uid, OTHER)

        assert outfits.items == [outfit]

    async def test_delete_removes_only_the_outfit(self, outfits, garments):
        top = await add(garments, OWNER, C.TOP)
        outfit = await CreateOutfitUseCase(outfits, garments).execute(
            OWNER, "Look", [top.uid]
        )

        await DeleteOutfitUseCase(outfits).execute(outfit.uid, OWNER)

        assert outfits.items == []
        assert garments.items == [top]
