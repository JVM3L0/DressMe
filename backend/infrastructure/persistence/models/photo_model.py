import uuid

from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .image_columns import SQLImageMixin
from .mixins import SQLLifeCycleMixin, SQLUUIDMixin


class PhotoOrm(Base, SQLUUIDMixin, SQLLifeCycleMixin, SQLImageMixin):
    __tablename__ = "photos"

    # Ao excluir o usuário, as fotos vão junto (os arquivos são removidos pela
    # aplicação, ADR-0003)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("users.uid", ondelete="CASCADE"), index=True, nullable=False
    )
