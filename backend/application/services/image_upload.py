import uuid
from collections.abc import Awaitable, Callable

from domain.entities.image import MAX_IMAGE_BYTES, StoredImage
from domain.exceptions.image import ImageTooLargeError
from domain.ports.image_processor import ImageProcessor
from domain.ports.image_storage import ImageStorage


async def delete_stored_image(storage: ImageStorage, image: StoredImage) -> None:
    """Remove a imagem e a miniatura. Não falha se um deles já não existir."""
    await storage.delete(image.key)
    await storage.delete(image.thumbnail_key)


class ImageUploader:
    """Fluxo comum aos uploads de fotos e de peças: valida, regrava sem
    metadados e guarda com um nome gerado (ADR-0003)."""

    def __init__(self, processor: ImageProcessor, storage: ImageStorage) -> None:
        self.processor = processor
        self.storage = storage

    async def store[T](
        self,
        data: bytes,
        folder: str,
        persist: Callable[[StoredImage], Awaitable[T]],
    ) -> T:
        """Guarda a imagem e chama `persist` para gravar o registro. Se o
        registro falhar, os arquivos são removidos, para não sobrar imagem órfã."""
        if len(data) > MAX_IMAGE_BYTES:
            raise ImageTooLargeError()

        processed = await self.processor.process(data)
        image = StoredImage(
            key=f"{folder}/{uuid.uuid4()}{processed.extension}",
            content_type=processed.content_type,
            width=processed.width,
            height=processed.height,
        )
        await self._save(image, processed.data, processed.thumbnail)
        try:
            return await persist(image)
        except BaseException:
            await delete_stored_image(self.storage, image)
            raise

    async def _save(self, image: StoredImage, data: bytes, thumbnail: bytes) -> None:
        await self.storage.save(image.key, data)
        try:
            await self.storage.save(image.thumbnail_key, thumbnail)
        except BaseException:
            await self.storage.delete(image.key)
            raise
