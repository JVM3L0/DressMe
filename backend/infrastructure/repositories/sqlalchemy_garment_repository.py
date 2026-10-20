from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.garment import Garment
from domain.enums.garment_category import GarmentCategory
from infrastructure.persistence.models.garment_model import GarmentOrm


class SQLAlchemyGarmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, garment: Garment) -> Garment:
        model = GarmentOrm(
            uid=garment.uid,
            owner_id=garment.owner_id,
            category=garment.category,
            name=garment.name,
            created_at=garment.created_at,
            **GarmentOrm.image_columns(garment.image),
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return _to_entity(model)

    async def list_by_owner(
        self, owner_id: UUID, category: GarmentCategory | None = None
    ) -> list[Garment]:
        stmt = select(GarmentOrm).where(GarmentOrm.owner_id == owner_id)
        if category is not None:
            stmt = stmt.where(GarmentOrm.category == category)
        stmt = stmt.order_by(GarmentOrm.created_at.desc(), GarmentOrm.uid)
        return [_to_entity(model) for model in await self.session.scalars(stmt)]

    async def get_for_owner(self, uid: UUID, owner_id: UUID) -> Garment | None:
        model = await self.session.scalar(
            select(GarmentOrm).where(
                GarmentOrm.uid == uid, GarmentOrm.owner_id == owner_id
            )
        )
        return _to_entity(model) if model else None

    async def delete(self, garment: Garment) -> None:
        await self.session.execute(
            delete(GarmentOrm).where(GarmentOrm.uid == garment.uid)
        )
        await self.session.commit()


def _to_entity(model: GarmentOrm) -> Garment:
    return Garment(
        uid=model.uid,
        owner_id=model.owner_id,
        category=model.category,
        name=model.name,
        created_at=model.created_at,
        updated_at=model.updated_at,
        image=model.image_entity(),
    )
