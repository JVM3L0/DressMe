"""Regras da composição de um conjunto: cada categoria aparece no máximo uma
vez, e uma peça única (vestido, macacão) ocupa o lugar da parte de cima e da
parte de baixo, então não combina com nenhuma das duas."""

from collections.abc import Iterable

from domain.enums.garment_category import GarmentCategory
from domain.exceptions.outfit import InvalidOutfitError, OutfitProblem

# Um conjunto tem uma peça por categoria, no máximo
MAX_OUTFIT_GARMENTS = len(GarmentCategory)


def check_composition(categories: Iterable[GarmentCategory]) -> None:
    """Levanta `InvalidOutfitError` se a composição não valer"""
    chosen = list(categories)
    if not chosen:
        raise InvalidOutfitError(OutfitProblem.EMPTY)
    if len(set(chosen)) != len(chosen):
        raise InvalidOutfitError(OutfitProblem.DUPLICATE_CATEGORY)
    if GarmentCategory.ONE_PIECE in chosen and (
        GarmentCategory.TOP in chosen or GarmentCategory.BOTTOM in chosen
    ):
        raise InvalidOutfitError(OutfitProblem.ONE_PIECE_CONFLICT)
