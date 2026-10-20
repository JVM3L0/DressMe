from typing import Literal

from pydantic import BaseModel, Field

# Limite de cada imagem enviada (RF04 e ADR-0003)
MAX_IMAGE_BYTES = 10 * 1024 * 1024

ImageContentType = Literal["image/jpeg", "image/png"]


class ProcessedImage(BaseModel):
    """Imagem validada e regravada sem metadados, pronta para guardar"""

    data: bytes
    content_type: ImageContentType
    width: int = Field(gt=0)
    height: int = Field(gt=0)

    @property
    def extension(self) -> str:
        return ".png" if self.content_type == "image/png" else ".jpg"


class StoredImage(BaseModel):
    """Referência a uma imagem guardada. `key` é o caminho relativo no
    armazenamento (ex.: `photos/<uuid>.jpg`), sempre gerado pela aplicação."""

    key: str
    content_type: ImageContentType
    width: int = Field(gt=0)
    height: int = Field(gt=0)
