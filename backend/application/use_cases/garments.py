"""Casos de uso do guarda-roupa. Toda operação recebe o dono: uma peça de
outra pessoa se comporta como se não existisse."""

from uuid import UUID

from application.interfaces.garment_repository import GarmentRepository
from application.services.image_upload import ImageUploader
from domain.entities.garment import Garment
from domain.enums.garment_category import GarmentCategory
from domain.exceptions.common import ResourceNotFoundError
from domain.ports.image_storage import ImageStorage

GARMENTS_FOLDER = "garments"


class AddGarmentUseCase:
    def __init__(self, repository: GarmentRepository, uploader: ImageUploader):
        self.repository = repository
        self.uploader = uploader

    async def execute(
        self,
        owner_id: UUID,
        data: bytes,
        category: GarmentCategory,
        name: str | None = None,
    ) -> Garment:
        name = (name or "").strip() or None

        async def persist(image) -> Garment:
            garment = Garment(
                owner_id=owner_id, category=category, name=name, image=image
            )
            return await self.repository.save(garment)

        return await self.uploader.store(data, GARMENTS_FOLDER, persist)


class ListGarmentsUseCase:
    def __init__(self, repository: GarmentRepository):
        self.repository = repository

    async def execute(
        self, owner_id: UUID, category: GarmentCategory | None = None
    ) -> list[Garment]:
        return await self.repository.list_by_owner(owner_id, category)


class GetGarmentUseCase:
    def __init__(self, repository: GarmentRepository):
        self.repository = repository

    async def execute(self, uid: UUID, owner_id: UUID) -> Garment:
        garment = await self.repository.get_for_owner(uid, owner_id)
        if garment is None:
            raise ResourceNotFoundError()
        return garment


class DeleteGarmentUseCase:
    def __init__(self, repository: GarmentRepository, storage: ImageStorage):
        self.repository = repository
        self.storage = storage

    async def execute(self, uid: UUID, owner_id: UUID) -> None:
        garment = await GetGarmentUseCase(self.repository).execute(uid, owner_id)
        # Primeiro o registro (ver DeletePhotoUseCase)
        await self.repository.delete(garment)
        await self.storage.delete(garment.image.key)
