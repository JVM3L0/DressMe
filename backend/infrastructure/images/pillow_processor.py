import io
import warnings

from anyio import to_thread
from PIL import Image, ImageOps, UnidentifiedImageError

from domain.entities.image import (
    MAX_IMAGE_SIDE,
    THUMBNAIL_SIDE,
    ImageContentType,
    ProcessedImage,
)
from domain.exceptions.image import InvalidImageError

# Uma foto de celular tem de 12 a 50 megapixels. Acima disso, o arquivo
# provavelmente é uma "bomba de descompressão": pequeno em disco, mas que
# ocupa gigabytes de memória ao ser aberto.
MAX_PIXELS = 60_000_000

# Formatos aceitos, identificados pelo conteúdo (nunca pela extensão)
_CONTENT_TYPES: dict[str, ImageContentType] = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
}

JPEG_QUALITY = 90


class PillowImageProcessor:
    async def process(self, data: bytes) -> ProcessedImage:
        # Decodificar imagem é custoso de CPU: fora do event loop
        return await to_thread.run_sync(self._process, data)

    def _process(self, data: bytes) -> ProcessedImage:
        try:
            with warnings.catch_warnings():
                # O aviso de imagem grande do Pillow vira erro; o limite
                # efetivo é o MAX_PIXELS, conferido antes de decodificar
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(io.BytesIO(data)) as source:
                    content_type = _CONTENT_TYPES.get(source.format or "")
                    if content_type is None:
                        raise InvalidImageError()
                    if source.width * source.height > MAX_PIXELS:
                        raise InvalidImageError()
                    # Aplica a rotação do EXIF antes de descartá-lo; sem
                    # isso, fotos de celular apareceriam deitadas
                    image = ImageOps.exif_transpose(source)
                    return _encode(image, content_type)
        except (
            UnidentifiedImageError,
            Image.DecompressionBombError,
            Image.DecompressionBombWarning,
            OSError,
            SyntaxError,  # alguns PNGs corrompidos
            ValueError,
        ) as exc:
            raise InvalidImageError() from exc


def _encode(image: Image.Image, content_type: ImageContentType) -> ProcessedImage:
    """Grava uma cópia nova, só com os pixels: sem EXIF (localização GPS,
    modelo do aparelho, data) nem outros metadados. O original é reduzido a
    `MAX_IMAGE_SIDE`, e a miniatura sai dele, em `THUMBNAIL_SIDE`."""
    # `thumbnail` só reduz, mantém a proporção e nunca amplia uma imagem menor
    icc_profile = image.info.get("icc_profile")
    image.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE), Image.Resampling.LANCZOS)
    thumbnail = image.copy()
    thumbnail.thumbnail((THUMBNAIL_SIDE, THUMBNAIL_SIDE), Image.Resampling.LANCZOS)
    return ProcessedImage(
        data=_save(image, content_type, icc_profile),
        thumbnail=_save(thumbnail, content_type, icc_profile),
        content_type=content_type,
        width=image.width,
        height=image.height,
    )


def _save(
    image: Image.Image, content_type: ImageContentType, icc_profile: bytes | None
) -> bytes:
    """O perfil de cor é mantido, para as cores não mudarem"""
    output = io.BytesIO()
    if content_type == "image/png":
        # PNG mantém a transparência, útil para peças recortadas
        if image.mode not in ("RGB", "RGBA", "L", "LA"):
            image = image.convert("RGBA")
        image.save(output, "PNG", optimize=True, icc_profile=icc_profile)
    else:
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(
            output, "JPEG", quality=JPEG_QUALITY, optimize=True, icc_profile=icc_profile
        )
    return output.getvalue()
