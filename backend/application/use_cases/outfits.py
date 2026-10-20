"""Casos de uso dos conjuntos. Toda operação recebe o dono: um conjunto (ou uma
peça) de outra pessoa se comporta como se não existisse."""

from uuid import UUID

from application.interfaces.garment_repository import GarmentRepository
from application.interfaces.outfit_repository import OutfitRepository
from domain.entities.outfit import Outfit
from domain.exceptions.common import ResourceNotFoundError
from domain.exceptions.outfit import InvalidOutfitError, OutfitProblem
from domain.outfit_rules import check_composition


async def _validated_garment_ids(
    garments: GarmentRepository, owner_id: UUID, garment_ids: list[UUID]
) -> list[UUID]:
    """Confere que as peças são do usuário e que a composição vale"""
    unique_ids = list(dict.fromkeys(garment_ids))
    if len(unique_ids) != len(garment_ids):
        raise InvalidOutfitError(OutfitProblem.DUPLICATE_GARMENT)
    found = await garments.list_by_ids(unique_ids, owner_id)
    if len(found) != len(unique_ids):
        raise InvalidOutfitError(OutfitProblem.UNKNOWN_GARMENT)
    check_composition(garment.category for garment in found)
    return unique_ids


class CreateOutfitUseCase:
    def __init__(self, outfits: OutfitRepository, garments: GarmentRepository):
        self.outfits = outfits
        self.garments = garments

    async def execute(
        self, owner_id: UUID, name: str, garment_ids: list[UUID]
    ) -> Outfit:
        ids = await _validated_garment_ids(self.garments, owner_id, garment_ids)
        return await self.outfits.save(
            Outfit(owner_id=owner_id, name=name, garment_ids=ids)
        )


class ListOutfitsUseCase:
    def __init__(self, outfits: OutfitRepository):
        self.outfits = outfits

    async def execute(self, owner_id: UUID) -> list[Outfit]:
        return await self.outfits.list_by_owner(owner_id)


class UpdateOutfitUseCase:
    def __init__(self, outfits: OutfitRepository, garments: GarmentRepository):
        self.outfits = outfits
        self.garments = garments

    async def execute(
        self, uid: UUID, owner_id: UUID, name: str, garment_ids: list[UUID]
    ) -> Outfit:
        outfit = await self.outfits.get_for_owner(uid, owner_id)
        if outfit is None:
            raise ResourceNotFoundError()
        ids = await _validated_garment_ids(self.garments, owner_id, garment_ids)
        updated = Outfit(
            uid=outfit.uid,
            owner_id=owner_id,
            name=name,
            garment_ids=ids,
            created_at=outfit.created_at,
        )
        return await self.outfits.update(updated)


class DeleteOutfitUseCase:
    def __init__(self, outfits: OutfitRepository):
        self.outfits = outfits

    async def execute(self, uid: UUID, owner_id: UUID) -> None:
        outfit = await self.outfits.get_for_owner(uid, owner_id)
        if outfit is None:
            raise ResourceNotFoundError()
        await self.outfits.delete(outfit)
