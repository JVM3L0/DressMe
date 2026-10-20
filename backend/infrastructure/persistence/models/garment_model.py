import uuid

from sqlalchemy import UUID, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from domain.entities.garment import GARMENT_NAME_MAX
from domain.enums.garment_category import GarmentCategory

from .base import Base
from .image_columns import SQLImageMixin
from .mixins import SQLLifeCycleMixin, SQLUUIDMixin


class GarmentOrm(Base, SQLUUIDMixin, SQLLifeCycleMixin, SQLImageMixin):
    __tablename__ = "garments"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("users.uid", ondelete="CASCADE"), index=True, nullable=False
    )
    # VARCHAR com CHECK, e não um ENUM do Postgres: incluir uma categoria
    # depois é só trocar a constraint
    category: Mapped[GarmentCategory] = mapped_column(
        Enum(
            GarmentCategory,
            name="garment_category",
            native_enum=False,
            create_constraint=True,
            length=20,
            values_callable=lambda enum: [member.value for member in enum],
            validate_strings=True,
        ),
        nullable=False,
    )
    name: Mapped[str | None] = mapped_column(String(GARMENT_NAME_MAX), nullable=True)
