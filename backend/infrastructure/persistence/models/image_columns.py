from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from domain.entities.image import StoredImage


class SQLImageMixin:
    """Colunas da imagem guardada (`StoredImage`), comuns a fotos e peças"""

    image_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    image_content_type: Mapped[str] = mapped_column(String(20), nullable=False)
    image_width: Mapped[int] = mapped_column(Integer, nullable=False)
    image_height: Mapped[int] = mapped_column(Integer, nullable=False)

    def image_entity(self) -> StoredImage:
        return StoredImage(
            key=self.image_key,
            content_type=self.image_content_type,  # ty:ignore[invalid-argument-type]
            width=self.image_width,
            height=self.image_height,
        )

    @staticmethod
    def image_columns(image: StoredImage) -> dict:
        return {
            "image_key": image.key,
            "image_content_type": image.content_type,
            "image_width": image.width,
            "image_height": image.height,
        }
