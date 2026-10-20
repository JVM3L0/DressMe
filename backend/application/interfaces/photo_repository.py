from typing import Protocol
from uuid import UUID

from domain.entities.photo import Photo


class PhotoRepository(Protocol):
    async def save(self, photo: Photo) -> Photo: ...

    async def list_by_owner(self, owner_id: UUID) -> list[Photo]:
        """Fotos do usuário, das mais recentes para as mais antigas"""
        ...

    async def get_for_owner(self, uid: UUID, owner_id: UUID) -> Photo | None: ...

    async def delete(self, photo: Photo) -> None: ...
