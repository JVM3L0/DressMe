from typing import Protocol


class ImageStorage(Protocol):
    """Onde os arquivos das imagens ficam (ADR-0003). A entrega ao navegador
    não passa por aqui: é feita pela camada web (nginx ou arquivo local)."""

    async def save(self, key: str, data: bytes) -> None: ...

    async def delete(self, key: str) -> None:
        """Remove o arquivo; não falha se ele já não existir"""
        ...
