from typing import Protocol

from domain.entities.image import ProcessedImage


class ImageProcessor(Protocol):
    """Valida a imagem pelo conteúdo e a regrava sem metadados (ADR-0003).
    Levanta `InvalidImageError` se ela não for uma imagem aceita."""

    async def process(self, data: bytes) -> ProcessedImage: ...
