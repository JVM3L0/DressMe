"""Imagens reais, geradas em memória, para os testes"""

import io

from PIL import Image

# Tags EXIF: orientação, modelo do aparelho e bloco de GPS
EXIF_ORIENTATION = 0x0112
EXIF_MODEL = 0x0110
EXIF_GPS_IFD = 0x8825


def jpeg_bytes(
    width: int = 40, height: int = 20, *, orientation: int | None = None
) -> bytes:
    """JPEG com metadados de celular: modelo, localização e, opcionalmente,
    a orientação (6 = girar 90° para a direita ao exibir)"""
    image = Image.new("RGB", (width, height), "red")
    exif = Image.Exif()
    exif[EXIF_MODEL] = "Celular de Teste"
    exif[EXIF_GPS_IFD] = {1: "S", 2: (23.0, 33.0, 0.0), 3: "W", 4: (46.0, 38.0, 0.0)}
    if orientation:
        exif[EXIF_ORIENTATION] = orientation
    output = io.BytesIO()
    image.save(output, "JPEG", exif=exif)
    return output.getvalue()


def png_bytes(width: int = 30, height: int = 50, *, mode: str = "RGBA") -> bytes:
    image = Image.new(mode, (width, height))
    output = io.BytesIO()
    image.save(output, "PNG")
    return output.getvalue()


def image_bytes(format: str, size: tuple[int, int] = (10, 10)) -> bytes:
    output = io.BytesIO()
    Image.new("RGB", size, "blue").save(output, format)
    return output.getvalue()
