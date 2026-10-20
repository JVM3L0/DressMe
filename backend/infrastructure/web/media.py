from typing import Annotated

from fastapi import File, Response, UploadFile
from fastapi.responses import FileResponse

from config import settings
from domain.entities.image import MAX_IMAGE_BYTES, StoredImage
from domain.exceptions.image import ImageTooLargeError
from infrastructure.storage.local_image_storage import LocalImageStorage

# Location `internal` do nginx que aponta para o volume das imagens
ACCEL_REDIRECT_PREFIX = "/_media/"

# A imagem de um id nunca muda (uma nova foto ganha outro id), então o
# navegador pode guardá-la. `private`: só no navegador, nunca num cache
# compartilhado, porque a imagem depende da sessão.
IMAGE_CACHE_CONTROL = "private, max-age=31536000, immutable"

_CHUNK = 1024 * 1024

ImageFile = Annotated[UploadFile, File(description="Imagem JPEG ou PNG de até 10 MB.")]


async def read_image_upload(file: UploadFile) -> bytes:
    """Lê o arquivo enviado, parando assim que ele passa do limite. O nginx
    já recusa corpos grandes, mas sem ele (desenvolvimento) o limite é este."""
    data = bytearray()
    while chunk := await file.read(_CHUNK):
        data += chunk
        if len(data) > MAX_IMAGE_BYTES:
            raise ImageTooLargeError()
    return bytes(data)


def image_response(
    image: StoredImage, storage: LocalImageStorage, *, thumbnail: bool = False
) -> Response:
    """Entrega a imagem, ou a miniatura (mesmo formato), ao dono"""
    key = image.thumbnail_key if thumbnail else image.key
    headers = {"Cache-Control": IMAGE_CACHE_CONTROL}
    if settings.MEDIA_ACCEL_REDIRECT:
        # A API já conferiu o dono; o nginx entrega o arquivo sem passar os
        # bytes pelo Python
        headers["X-Accel-Redirect"] = ACCEL_REDIRECT_PREFIX + key
        return Response(media_type=image.content_type, headers=headers)
    return FileResponse(
        storage.path(key), media_type=image.content_type, headers=headers
    )
