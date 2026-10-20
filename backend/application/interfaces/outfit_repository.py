from typing import Protocol
from uuid import UUID

from domain.entities.outfit import Outfit


class OutfitRepository(Protocol):
    async def save(self, outfit: Outfit) -> Outfit: ...

    async def list_by_owner(self, owner_id: UUID) -> list[Outfit]:
        """Conjuntos do usuário, dos mais recentes para os mais antigos"""
        ...

    async def get_for_owner(self, uid: UUID, owner_id: UUID) -> Outfit | None: ...

    async def update(self, outfit: Outfit) -> Outfit:
        """Troca o nome e as peças do conjunto"""
        ...

    async def delete(self, outfit: Outfit) -> None: ...
