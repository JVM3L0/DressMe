import uuid
from typing import Annotated

from pydantic import (
    AwareDatetime,
    BaseModel,
    BeforeValidator,
    Field,
    field_validator,
)

from domain.entities.outfit import OUTFIT_NAME_MAX, Outfit
from domain.outfit_rules import MAX_OUTFIT_GARMENTS


def _strip(value: object) -> object:
    # Remove espaços antes das restrições; o que não é texto segue para a
    # validação de tipo do Pydantic (422)
    return value.strip() if isinstance(value, str) else value


OutfitName = Annotated[
    str,
    BeforeValidator(_strip),
    Field(
        min_length=1,
        max_length=OUTFIT_NAME_MAX,
        description="Nome do conjunto.",
        examples=["Look de sexta"],
    ),
]


class OutfitInput(BaseModel):
    name: OutfitName
    garment_ids: Annotated[
        list[uuid.UUID],
        Field(
            min_length=1,
            max_length=MAX_OUTFIT_GARMENTS,
            description="Peças do conjunto: no máximo uma por categoria (até 4 "
            "acessórios), e uma peça única não combina com parte de cima ou de baixo.",
        ),
    ]

    @field_validator("garment_ids")
    @classmethod
    def _no_repeated_ids(cls, value: list[uuid.UUID]) -> list[uuid.UUID]:
        if len(set(value)) != len(value):
            raise ValueError("Não repita a mesma peça.")
        return value


class OutfitPublic(BaseModel):
    uid: uuid.UUID
    name: str
    garment_ids: list[uuid.UUID]
    created_at: AwareDatetime

    @classmethod
    def from_entity(cls, outfit: Outfit) -> "OutfitPublic":
        return cls(
            uid=outfit.uid,
            name=outfit.name,
            garment_ids=outfit.garment_ids,
            created_at=outfit.created_at,
        )
