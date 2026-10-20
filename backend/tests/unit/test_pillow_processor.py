import io

import pytest
from PIL import Image

from domain.entities.image import MAX_IMAGE_SIDE, THUMBNAIL_SIDE
from domain.exceptions.image import InvalidImageError
from infrastructure.images import pillow_processor
from infrastructure.images.pillow_processor import PillowImageProcessor
from tests.images import EXIF_GPS_IFD, EXIF_MODEL, image_bytes, jpeg_bytes, png_bytes

pytestmark = pytest.mark.anyio


@pytest.fixture
def processor() -> PillowImageProcessor:
    return PillowImageProcessor()


def open_image(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data))


async def test_jpeg_is_reencoded_without_exif(processor):
    original = jpeg_bytes()
    assert open_image(original).getexif().get(EXIF_MODEL) == "Celular de Teste"

    result = await processor.process(original)

    assert result.content_type == "image/jpeg"
    assert (result.width, result.height) == (40, 20)
    image = open_image(result.data)
    assert image.format == "JPEG"
    exif = image.getexif()
    assert EXIF_MODEL not in exif
    assert EXIF_GPS_IFD not in exif
    assert b"Celular de Teste" not in result.data


async def test_jpeg_orientation_is_applied_before_dropping_exif(processor):
    # Foto "deitada" no arquivo, com a orientação 6 (em pé ao exibir)
    result = await processor.process(jpeg_bytes(40, 20, orientation=6))

    assert (result.width, result.height) == (20, 40)


async def test_png_keeps_transparency(processor):
    result = await processor.process(png_bytes(30, 50))

    assert result.content_type == "image/png"
    assert (result.width, result.height) == (30, 50)
    assert open_image(result.data).mode == "RGBA"


async def test_palette_png_becomes_rgba(processor):
    result = await processor.process(png_bytes(mode="P"))

    assert open_image(result.data).mode == "RGBA"


@pytest.mark.parametrize("format", ["GIF", "BMP", "WEBP", "TIFF"])
async def test_rejects_other_image_formats(processor, format):
    with pytest.raises(InvalidImageError):
        await processor.process(image_bytes(format))


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"nao sou uma imagem",
        b"<svg xmlns='http://www.w3.org/2000/svg'></svg>",
        jpeg_bytes()[:200],  # JPEG truncado
        b"\x89PNG\r\n\x1a\n" + b"\x00" * 50,  # cabeçalho de PNG sem conteúdo
    ],
)
async def test_rejects_invalid_or_corrupted_files(processor, data):
    with pytest.raises(InvalidImageError):
        await processor.process(data)


async def test_rejects_images_with_too_many_pixels(processor, monkeypatch):
    # "Bomba de descompressão": recusada antes de decodificar os pixels
    monkeypatch.setattr(pillow_processor, "MAX_PIXELS", 40 * 20 - 1)

    with pytest.raises(InvalidImageError):
        await processor.process(jpeg_bytes(40, 20))


class TestSizes:
    async def test_small_image_is_not_enlarged(self, processor):
        result = await processor.process(jpeg_bytes(40, 20))

        assert (result.width, result.height) == (40, 20)
        assert open_image(result.thumbnail).size == (40, 20)

    async def test_original_is_reduced_keeping_the_proportion(self, processor):
        result = await processor.process(jpeg_bytes(MAX_IMAGE_SIDE * 2, MAX_IMAGE_SIDE))

        assert (result.width, result.height) == (MAX_IMAGE_SIDE, MAX_IMAGE_SIDE // 2)
        assert open_image(result.data).size == (result.width, result.height)

    async def test_thumbnail_fits_in_the_thumbnail_side(self, processor):
        result = await processor.process(jpeg_bytes(1200, 1800))

        width, height = open_image(result.thumbnail).size
        assert (width, height) == (THUMBNAIL_SIDE * 2 // 3, THUMBNAIL_SIDE)
        assert len(result.thumbnail) < len(result.data)

    async def test_thumbnail_has_the_same_format_and_no_metadata(self, processor):
        jpeg = await processor.process(jpeg_bytes(1000, 600, orientation=6))
        png = await processor.process(png_bytes(900, 900))

        thumbnail = open_image(jpeg.thumbnail)
        assert thumbnail.format == "JPEG"
        assert thumbnail.size == (THUMBNAIL_SIDE * 6 // 10, THUMBNAIL_SIDE)  # girada
        assert not thumbnail.getexif()
        assert b"Celular de Teste" not in jpeg.thumbnail
        assert open_image(png.thumbnail).format == "PNG"
        assert open_image(png.thumbnail).mode == "RGBA"
