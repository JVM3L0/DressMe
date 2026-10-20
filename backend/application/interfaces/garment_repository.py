from typing import Protocol
from uuid import UUID

from domain.entities.garment import Garment
from domain.enums.garment_category import GarmentCategory


class GarmentRepository(Protocol):
    async def save(self, garment: Garment) -> Garment: ...

    async def list_by_owner(
        self, owner_id: UUID, category: GarmentCategory | None = None
    ) -> list[Garment]:
        """Peças do usuário, das mais recentes para as mais antigas"""
        ...

    async def get_for_owner(self, uid: UUID, owner_id: UUID) -> Garment | None: ...

    async def delete(self, garment: Garment) -> None: ...
