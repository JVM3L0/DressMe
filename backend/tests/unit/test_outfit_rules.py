import pytest

from domain.enums.garment_category import GarmentCategory as C
from domain.exceptions.outfit import InvalidOutfitError, OutfitProblem
from domain.outfit_rules import MAX_OUTFIT_GARMENTS, check_composition


@pytest.mark.parametrize(
    "categories",
    [
        [C.TOP],
        [C.TOP, C.BOTTOM],
        [C.ACCESSORY, C.OUTERWEAR, C.TOP, C.BOTTOM, C.FOOTWEAR],
        [C.ONE_PIECE, C.FOOTWEAR, C.ACCESSORY, C.OUTERWEAR],
        [C.ONE_PIECE],
    ],
)
def test_accepts_valid_compositions(categories):
    check_composition(categories)


@pytest.mark.parametrize(
    ("categories", "problem"),
    [
        ([], OutfitProblem.EMPTY),
        ([C.TOP, C.TOP], OutfitProblem.DUPLICATE_CATEGORY),
        ([C.FOOTWEAR, C.TOP, C.FOOTWEAR], OutfitProblem.DUPLICATE_CATEGORY),
        ([C.ONE_PIECE, C.TOP], OutfitProblem.ONE_PIECE_CONFLICT),
        ([C.BOTTOM, C.ONE_PIECE], OutfitProblem.ONE_PIECE_CONFLICT),
        ([C.ONE_PIECE, C.TOP, C.BOTTOM], OutfitProblem.ONE_PIECE_CONFLICT),
    ],
)
def test_rejects_invalid_compositions(categories, problem):
    with pytest.raises(InvalidOutfitError) as exc:
        check_composition(categories)

    assert exc.value.problem is problem


def test_accepts_any_generator_of_categories():
    check_composition(category for category in (C.TOP, C.BOTTOM))


def test_an_outfit_never_has_more_pieces_than_categories():
    assert MAX_OUTFIT_GARMENTS == len(C) == 6
