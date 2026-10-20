import pytest

from domain.enums.garment_category import GarmentCategory as C
from domain.exceptions.outfit import InvalidOutfitError, OutfitProblem
from domain.outfit_rules import MAX_ACCESSORIES, MAX_OUTFIT_GARMENTS, check_composition


@pytest.mark.parametrize(
    "categories",
    [
        [C.TOP],
        [C.TOP, C.BOTTOM],
        [C.ACCESSORY, C.OUTERWEAR, C.TOP, C.BOTTOM, C.FOOTWEAR],
        [C.ONE_PIECE, C.FOOTWEAR, C.ACCESSORY, C.OUTERWEAR],
        [C.ONE_PIECE],
        [C.ACCESSORY],
        [C.ACCESSORY] * MAX_ACCESSORIES,
        [C.ACCESSORY, C.TOP, C.ACCESSORY, C.BOTTOM, C.ACCESSORY, C.FOOTWEAR],
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
        ([C.OUTERWEAR, C.OUTERWEAR], OutfitProblem.DUPLICATE_CATEGORY),
        ([C.ACCESSORY] * (MAX_ACCESSORIES + 1), OutfitProblem.TOO_MANY_ACCESSORIES),
        (
            [C.ACCESSORY] * (MAX_ACCESSORIES + 1) + [C.ONE_PIECE, C.TOP],
            OutfitProblem.TOO_MANY_ACCESSORIES,
        ),
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


def test_the_largest_possible_outfit_is_valid_and_has_the_maximum_pieces():
    largest = [
        *[C.ACCESSORY] * MAX_ACCESSORIES,
        C.OUTERWEAR,
        C.TOP,
        C.BOTTOM,
        C.FOOTWEAR,
    ]

    check_composition(largest)

    assert len(largest) == MAX_OUTFIT_GARMENTS == 8


def test_accessories_do_not_conflict_with_a_one_piece():
    check_composition([C.ACCESSORY, C.ACCESSORY, C.ONE_PIECE, C.FOOTWEAR])
