from pathlib import PurePosixPath
from typing import Literal

from pydantic import BaseModel, Field

# Limite de cada imagem enviada (RF04 e ADR-0003)
MAX_IMAGE_BYTES = 10 * 1024 * 1024

# Lado maior, em pixels. O original é reduzido a este tamanho (uma foto de
# celular tem 4.000 px ou mais, e a tela não mostra tanto) e a miniatura, usada
# nas grades, a este outro. Nunca se amplia uma imagem menor.
MAX_IMAGE_SIDE = 2048
THUMBNAIL_SIDE = 480

ImageContentType = Literal["image/jpeg", "image/png"]


class ProcessedImage(BaseModel):
    """Imagem validada e regravada sem metadados, pronta para guardar, com a
    miniatura (no mesmo formato)"""

    data: bytes
    thumbnail: bytes
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

    @property
    def thumbnail_key(self) -> str:
        """Chave da miniatura, derivada da imagem (`photos/<uuid>_thumb.jpg`),
        então não precisa de outra coluna no banco"""
        path = PurePosixPath(self.key)
        return str(path.with_name(f"{path.stem}_thumb{path.suffix}"))
