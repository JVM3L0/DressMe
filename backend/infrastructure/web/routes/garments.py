from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Form, Query, Request, Response, status

from application.use_cases.garments import (
    AddGarmentUseCase,
    DeleteGarmentUseCase,
    GetGarmentUseCase,
    ListGarmentsUseCase,
)
from config import settings
from domain.enums.garment_category import GarmentCategory
from infrastructure.web.dependencies import (
    CurrentUserDep,
    GarmentRepositoryDep,
    ImageStorageDep,
    ImageUploaderDep,
)
from infrastructure.web.media import ImageFile, image_response, read_image_upload
from infrastructure.web.rate_limit import limiter
from infrastructure.web.responses import IMAGE_RESPONSES, NOT_FOUND, UNAUTHORIZED
from infrastructure.web.schemas.image_schemes import GarmentName, GarmentPublic

router = APIRouter(prefix="/garments", tags=["garments"], responses=UNAUTHORIZED)


@router.post(
    "/",
    response_model=GarmentPublic,
    status_code=status.HTTP_201_CREATED,
    responses=IMAGE_RESPONSES,
)
@limiter.limit(settings.RATE_LIMIT_UPLOAD)
async def add_garment(
    request: Request,  # usado pelo rate limiter
    user: CurrentUserDep,
    repository: GarmentRepositoryDep,
    uploader: ImageUploaderDep,
    file: ImageFile,
    category: Annotated[GarmentCategory, Form()],
    name: Annotated[GarmentName, Form()] = None,
) -> GarmentPublic:
    """Adiciona uma peça ao guarda-roupa. PNG com fundo transparente fica
    melhor no provador."""
    data = await read_image_upload(file)
    garment = await AddGarmentUseCase(repository, uploader).execute(
        user.uid, data, category=category, name=name
    )
    return GarmentPublic.from_entity(garment)


@router.get("/", response_model=list[GarmentPublic])
async def list_garments(
    user: CurrentUserDep,
    repository: GarmentRepositoryDep,
    category: Annotated[GarmentCategory | None, Query()] = None,
) -> list[GarmentPublic]:
    garments = await ListGarmentsUseCase(repository).execute(user.uid, category)
    return [GarmentPublic.from_entity(garment) for garment in garments]


@router.get(
    "/{uid}/image",
    response_class=Response,
    responses={200: {"content": {"image/jpeg": {}, "image/png": {}}}, **NOT_FOUND},
)
async def get_garment_image(
    uid: UUID,
    user: CurrentUserDep,
    repository: GarmentRepositoryDep,
    storage: ImageStorageDep,
) -> Response:
    """Arquivo da peça, só para o dono"""
    garment = await GetGarmentUseCase(repository).execute(uid, user.uid)
    return image_response(garment.image, storage)


@router.get(
    "/{uid}/thumbnail",
    response_class=Response,
    responses={200: {"content": {"image/jpeg": {}, "image/png": {}}}, **NOT_FOUND},
)
async def get_garment_thumbnail(
    uid: UUID,
    user: CurrentUserDep,
    repository: GarmentRepositoryDep,
    storage: ImageStorageDep,
) -> Response:
    """Miniatura (até 480 px), para as grades, só para o dono"""
    garment = await GetGarmentUseCase(repository).execute(uid, user.uid)
    return image_response(garment.image, storage, thumbnail=True)


@router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT, responses=NOT_FOUND)
async def delete_garment(
    uid: UUID,
    user: CurrentUserDep,
    repository: GarmentRepositoryDep,
    storage: ImageStorageDep,
) -> None:
    await DeleteGarmentUseCase(repository, storage).execute(uid, user.uid)
