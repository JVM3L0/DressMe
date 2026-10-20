import uuid
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field

from domain.entities.garment import GARMENT_NAME_MAX, Garment
from domain.entities.photo import Photo
from domain.enums.garment_category import GarmentCategory

GarmentName = Annotated[
    str | None,
    Field(
        max_length=GARMENT_NAME_MAX,
        description="Nome opcional para reconhecer a peça.",
        examples=["Camisa de linho azul"],
    ),
]


class ImageDimensions(BaseModel):
    """Dimensões em pixels, para a página reservar o espaço da imagem antes
    de ela carregar"""

    width: int
    height: int


class PhotoPublic(ImageDimensions):
    uid: uuid.UUID
    created_at: AwareDatetime

    @classmethod
    def from_entity(cls, photo: Photo) -> "PhotoPublic":
        return cls(
            uid=photo.uid,
            created_at=photo.created_at,
            width=photo.image.width,
            height=photo.image.height,
        )


class GarmentPublic(ImageDimensions):
    uid: uuid.UUID
    category: GarmentCategory
    name: str | None
    created_at: AwareDatetime

    @classmethod
    def from_entity(cls, garment: Garment) -> "GarmentPublic":
        return cls(
            uid=garment.uid,
            category=garment.category,
            name=garment.name,
            created_at=garment.created_at,
            width=garment.image.width,
            height=garment.image.height,
        )
