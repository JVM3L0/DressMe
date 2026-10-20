from enum import StrEnum


class OutfitProblem(StrEnum):
    EMPTY = "outfit_empty"
    DUPLICATE_CATEGORY = "outfit_duplicate_category"
    DUPLICATE_GARMENT = "outfit_duplicate_garment"
    TOO_MANY_ACCESSORIES = "outfit_too_many_accessories"
    ONE_PIECE_CONFLICT = "outfit_one_piece_conflict"
    UNKNOWN_GARMENT = "outfit_unknown_garment"


class InvalidOutfitError(Exception):
    """A composição do conjunto não é válida. `problem` diz o motivo."""

    def __init__(self, problem: OutfitProblem) -> None:
        super().__init__(problem.value)
        self.problem = problem
