import uuid

from pydantic import BaseModel, Field

from domain.enums.garment_category import GarmentCategory

from .image import StoredImage
from .mixins import LifeCycleMixin, UUIDMixin

GARMENT_NAME_MAX = 60


class Garment(BaseModel, UUIDMixin, LifeCycleMixin):
    """Peça do guarda-roupa"""

    owner_id: uuid.UUID
    category: GarmentCategory
    name: str | None = Field(default=None, max_length=GARMENT_NAME_MAX)
    image: StoredImage
