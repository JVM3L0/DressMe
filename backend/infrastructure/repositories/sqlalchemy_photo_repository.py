from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.photo import Photo
from infrastructure.persistence.models.photo_model import PhotoOrm


class SQLAlchemyPhotoRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, photo: Photo) -> Photo:
        model = PhotoOrm(
            uid=photo.uid,
            owner_id=photo.owner_id,
            created_at=photo.created_at,
            **PhotoOrm.image_columns(photo.image),
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return _to_entity(model)

    async def list_by_owner(self, owner_id: UUID) -> list[Photo]:
        stmt = (
            select(PhotoOrm)
            .where(PhotoOrm.owner_id == owner_id)
            .order_by(PhotoOrm.created_at.desc(), PhotoOrm.uid)
        )
        return [_to_entity(model) for model in await self.session.scalars(stmt)]

    async def get_for_owner(self, uid: UUID, owner_id: UUID) -> Photo | None:
        model = await self.session.scalar(
            select(PhotoOrm).where(PhotoOrm.uid == uid, PhotoOrm.owner_id == owner_id)
        )
        return _to_entity(model) if model else None

    async def delete(self, photo: Photo) -> None:
        await self.session.execute(delete(PhotoOrm).where(PhotoOrm.uid == photo.uid))
        await self.session.commit()


def _to_entity(model: PhotoOrm) -> Photo:
    return Photo(
        uid=model.uid,
        owner_id=model.owner_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
        image=model.image_entity(),
    )
