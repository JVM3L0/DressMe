"""Regras da composição de um conjunto: cada categoria aparece no máximo uma
vez, exceto os acessórios (até `MAX_ACCESSORIES`: boné, óculos, relógio, bolsa),
e uma peça única (vestido, macacão) ocupa o lugar da parte de cima e da parte
de baixo, então não combina com nenhuma das duas."""

from collections import Counter
from collections.abc import Iterable

from domain.enums.garment_category import GarmentCategory
from domain.exceptions.outfit import InvalidOutfitError, OutfitProblem

MAX_ACCESSORIES = 4

# Acessórios, mais agasalho, parte de cima, parte de baixo e calçado (a peça
# única ocupa o lugar da parte de cima e da de baixo, então não soma)
MAX_OUTFIT_GARMENTS = MAX_ACCESSORIES + 4


def check_composition(categories: Iterable[GarmentCategory]) -> None:
    """Levanta `InvalidOutfitError` se a composição não valer"""
    counts = Counter(categories)
    if not counts:
        raise InvalidOutfitError(OutfitProblem.EMPTY)
    if any(
        count > 1
        for category, count in counts.items()
        if category is not GarmentCategory.ACCESSORY
    ):
        raise InvalidOutfitError(OutfitProblem.DUPLICATE_CATEGORY)
    if counts[GarmentCategory.ACCESSORY] > MAX_ACCESSORIES:
        raise InvalidOutfitError(OutfitProblem.TOO_MANY_ACCESSORIES)
    if GarmentCategory.ONE_PIECE in counts and (
        GarmentCategory.TOP in counts or GarmentCategory.BOTTOM in counts
    ):
        raise InvalidOutfitError(OutfitProblem.ONE_PIECE_CONFLICT)
