import uuid

from pydantic import BaseModel, Field, field_validator

from .mixins import LifeCycleMixin, UUIDMixin

OUTFIT_NAME_MAX = 60


class Outfit(BaseModel, UUIDMixin, LifeCycleMixin):
    """Conjunto de peças do guarda-roupa, com um nome ("Look de sexta")"""

    owner_id: uuid.UUID
    name: str = Field(min_length=1, max_length=OUTFIT_NAME_MAX)
    garment_ids: list[uuid.UUID]

    @field_validator("name")
    @classmethod
    def _strip_name(cls, value: str) -> str:
        return value.strip()
