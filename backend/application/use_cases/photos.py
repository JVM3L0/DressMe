"""Casos de uso das fotos do usuário. Toda operação recebe o dono: uma foto
de outra pessoa se comporta como se não existisse."""

from uuid import UUID

from application.interfaces.photo_repository import PhotoRepository
from application.services.image_upload import ImageUploader, delete_stored_image
from domain.entities.photo import Photo
from domain.exceptions.common import ResourceNotFoundError
from domain.ports.image_storage import ImageStorage

PHOTOS_FOLDER = "photos"


class UploadPhotoUseCase:
    def __init__(self, repository: PhotoRepository, uploader: ImageUploader):
        self.repository = repository
        self.uploader = uploader

    async def execute(self, owner_id: UUID, data: bytes) -> Photo:
        async def persist(image) -> Photo:
            return await self.repository.save(Photo(owner_id=owner_id, image=image))

        return await self.uploader.store(data, PHOTOS_FOLDER, persist)


class ListPhotosUseCase:
    def __init__(self, repository: PhotoRepository):
        self.repository = repository

    async def execute(self, owner_id: UUID) -> list[Photo]:
        return await self.repository.list_by_owner(owner_id)


class GetPhotoUseCase:
    def __init__(self, repository: PhotoRepository):
        self.repository = repository

    async def execute(self, uid: UUID, owner_id: UUID) -> Photo:
        photo = await self.repository.get_for_owner(uid, owner_id)
        if photo is None:
            raise ResourceNotFoundError()
        return photo


class DeletePhotoUseCase:
    def __init__(self, repository: PhotoRepository, storage: ImageStorage):
        self.repository = repository
        self.storage = storage

    async def execute(self, uid: UUID, owner_id: UUID) -> None:
        photo = await GetPhotoUseCase(self.repository).execute(uid, owner_id)
        # Primeiro o registro: se o arquivo não puder ser apagado, sobra um
        # arquivo órfão (inofensivo), e não um registro apontando para o nada
        await self.repository.delete(photo)
        await delete_stored_image(self.storage, photo.image)
