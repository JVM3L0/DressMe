import uuid

from pydantic import BaseModel

from .image import StoredImage
from .mixins import LifeCycleMixin, UUIDMixin


class Photo(BaseModel, UUIDMixin, LifeCycleMixin):
    """Foto do próprio usuário, sobre a qual as peças são provadas"""

    owner_id: uuid.UUID
    image: StoredImage
