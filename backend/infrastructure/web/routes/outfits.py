from uuid import UUID

from fastapi import APIRouter, status

from application.use_cases.outfits import (
    CreateOutfitUseCase,
    DeleteOutfitUseCase,
    ListOutfitsUseCase,
    UpdateOutfitUseCase,
)
from infrastructure.web.dependencies import (
    CurrentUserDep,
    GarmentRepositoryDep,
    OutfitRepositoryDep,
)
from infrastructure.web.responses import INVALID_OUTFIT, NOT_FOUND, UNAUTHORIZED
from infrastructure.web.schemas.outfit_schemes import OutfitInput, OutfitPublic

router = APIRouter(prefix="/outfits", tags=["outfits"], responses=UNAUTHORIZED)


@router.post(
    "/",
    response_model=OutfitPublic,
    status_code=status.HTTP_201_CREATED,
    responses=INVALID_OUTFIT,
)
async def create_outfit(
    data: OutfitInput,
    user: CurrentUserDep,
    outfits: OutfitRepositoryDep,
    garments: GarmentRepositoryDep,
) -> OutfitPublic:
    """Salva um conjunto com as peças do guarda-roupa. As peças são
    conferidas: precisam ser do usuário, uma por categoria."""
    outfit = await CreateOutfitUseCase(outfits, garments).execute(
        user.uid, data.name, data.garment_ids
    )
    return OutfitPublic.from_entity(outfit)


@router.get("/", response_model=list[OutfitPublic])
async def list_outfits(
    user: CurrentUserDep, outfits: OutfitRepositoryDep
) -> list[OutfitPublic]:
    result = await ListOutfitsUseCase(outfits).execute(user.uid)
    return [OutfitPublic.from_entity(outfit) for outfit in result]


@router.put(
    "/{uid}",
    response_model=OutfitPublic,
    responses={**NOT_FOUND, **INVALID_OUTFIT},
)
async def update_outfit(
    uid: UUID,
    data: OutfitInput,
    user: CurrentUserDep,
    outfits: OutfitRepositoryDep,
    garments: GarmentRepositoryDep,
) -> OutfitPublic:
    """Troca o nome e as peças do conjunto"""
    outfit = await UpdateOutfitUseCase(outfits, garments).execute(
        uid, user.uid, data.name, data.garment_ids
    )
    return OutfitPublic.from_entity(outfit)


@router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT, responses=NOT_FOUND)
async def delete_outfit(
    uid: UUID, user: CurrentUserDep, outfits: OutfitRepositoryDep
) -> None:
    """Exclui o conjunto, mas não as peças"""
    await DeleteOutfitUseCase(outfits).execute(uid, user.uid)
