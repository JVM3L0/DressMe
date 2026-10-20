import uuid

from sqlalchemy import UUID, Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.entities.outfit import OUTFIT_NAME_MAX

from .base import Base
from .garment_model import GarmentOrm
from .mixins import SQLLifeCycleMixin, SQLUUIDMixin

# Peças de cada conjunto. Ao excluir o conjunto ou a peça, o vínculo some (a
# peça apagada sai dos conjuntos; um conjunto pode ficar vazio).
outfit_garments = Table(
    "outfit_garments",
    Base.metadata,
    Column(
        "outfit_id",
        UUID,
        ForeignKey("outfits.uid", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "garment_id",
        UUID,
        ForeignKey("garments.uid", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
)


class OutfitOrm(Base, SQLUUIDMixin, SQLLifeCycleMixin):
    __tablename__ = "outfits"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("users.uid", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(OUTFIT_NAME_MAX), nullable=False)
    garments: Mapped[list[GarmentOrm]] = relationship(
        secondary=outfit_garments, lazy="selectin", passive_deletes=True
    )
