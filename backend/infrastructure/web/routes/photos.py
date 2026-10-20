from uuid import UUID

from fastapi import APIRouter, Request, Response, status

from application.use_cases.photos import (
    DeletePhotoUseCase,
    GetPhotoUseCase,
    ListPhotosUseCase,
    UploadPhotoUseCase,
)
from config import settings
from infrastructure.web.dependencies import (
    CurrentUserDep,
    ImageStorageDep,
    ImageUploaderDep,
    PhotoRepositoryDep,
)
from infrastructure.web.media import ImageFile, image_response, read_image_upload
from infrastructure.web.rate_limit import limiter
from infrastructure.web.responses import IMAGE_RESPONSES, NOT_FOUND, UNAUTHORIZED
from infrastructure.web.schemas.image_schemes import PhotoPublic

router = APIRouter(prefix="/photos", tags=["photos"], responses=UNAUTHORIZED)


@router.post(
    "/",
    response_model=PhotoPublic,
    status_code=status.HTTP_201_CREATED,
    responses=IMAGE_RESPONSES,
)
@limiter.limit(settings.RATE_LIMIT_UPLOAD)
async def upload_photo(
    request: Request,  # usado pelo rate limiter
    user: CurrentUserDep,
    repository: PhotoRepositoryDep,
    uploader: ImageUploaderDep,
    file: ImageFile,
) -> PhotoPublic:
    """Envia uma foto do usuário. A imagem é regravada sem metadados (EXIF)."""
    data = await read_image_upload(file)
    photo = await UploadPhotoUseCase(repository, uploader).execute(user.uid, data)
    return PhotoPublic.from_entity(photo)


@router.get("/", response_model=list[PhotoPublic])
async def list_photos(
    user: CurrentUserDep, repository: PhotoRepositoryDep
) -> list[PhotoPublic]:
    photos = await ListPhotosUseCase(repository).execute(user.uid)
    return [PhotoPublic.from_entity(photo) for photo in photos]


@router.get(
    "/{uid}/image",
    response_class=Response,
    responses={200: {"content": {"image/jpeg": {}, "image/png": {}}}, **NOT_FOUND},
)
async def get_photo_image(
    uid: UUID,
    user: CurrentUserDep,
    repository: PhotoRepositoryDep,
    storage: ImageStorageDep,
) -> Response:
    """Arquivo da foto, só para o dono"""
    photo = await GetPhotoUseCase(repository).execute(uid, user.uid)
    return image_response(photo.image, storage)


@router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT, responses=NOT_FOUND)
async def delete_photo(
    uid: UUID,
    user: CurrentUserDep,
    repository: PhotoRepositoryDep,
    storage: ImageStorageDep,
) -> None:
    await DeletePhotoUseCase(repository, storage).execute(uid, user.uid)
