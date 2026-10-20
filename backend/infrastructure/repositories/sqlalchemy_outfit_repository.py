from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.outfit import Outfit
from infrastructure.persistence.models.garment_model import GarmentOrm
from infrastructure.persistence.models.outfit_model import OutfitOrm


class SQLAlchemyOutfitRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, outfit: Outfit) -> Outfit:
        model = OutfitOrm(
            uid=outfit.uid,
            owner_id=outfit.owner_id,
            name=outfit.name,
            created_at=outfit.created_at,
            garments=await self._garments(outfit.garment_ids),
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return _to_entity(model)

    async def list_by_owner(self, owner_id: UUID) -> list[Outfit]:
        stmt = (
            select(OutfitOrm)
            .where(OutfitOrm.owner_id == owner_id)
            .order_by(OutfitOrm.created_at.desc(), OutfitOrm.uid)
        )
        return [_to_entity(model) for model in await self.session.scalars(stmt)]

    async def get_for_owner(self, uid: UUID, owner_id: UUID) -> Outfit | None:
        model = await self.session.scalar(
            select(OutfitOrm).where(
                OutfitOrm.uid == uid, OutfitOrm.owner_id == owner_id
            )
        )
        return _to_entity(model) if model else None

    async def update(self, outfit: Outfit) -> Outfit:
        model = await self.session.get(OutfitOrm, outfit.uid)
        assert model is not None  # o caso de uso já buscou o conjunto
        model.name = outfit.name
        model.garments = await self._garments(outfit.garment_ids)
        await self.session.commit()
        await self.session.refresh(model)
        return _to_entity(model)

    async def delete(self, outfit: Outfit) -> None:
        await self.session.execute(delete(OutfitOrm).where(OutfitOrm.uid == outfit.uid))
        await self.session.commit()

    async def _garments(self, uids: list[UUID]) -> list[GarmentOrm]:
        if not uids:
            return []
        found = await self.session.scalars(
            select(GarmentOrm).where(GarmentOrm.uid.in_(uids))
        )
        return list(found)


def _to_entity(model: OutfitOrm) -> Outfit:
    return Outfit(
        uid=model.uid,
        owner_id=model.owner_id,
        name=model.name,
        garment_ids=sorted(garment.uid for garment in model.garments),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
