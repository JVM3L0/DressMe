import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.user import User
from infrastructure.persistence.models.user_model import UserOrm


class SQLAlchemyUserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, user: User) -> User:

        model = UserOrm(
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
        )

        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        return user

    async def update(self, user: User) -> User:
        user_orm = UserOrm(**user.model_dump())
        user_out = await self.session.merge(instance=user_orm)
        await self.session.commit()

        return User.model_validate(user_out)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserOrm).where(UserOrm.email == email)
        user_orm = (await self.session.execute(statement=stmt)).scalar_one_or_none()

        return User.model_validate(user_orm) if user_orm else None

    async def get_by_id(self, user_uid: uuid.UUID) -> User | None:
        stmt = select(UserOrm).where(UserOrm.uid == user_uid)
        user_orm = (await self.session.execute(statement=stmt)).scalar_one_or_none()

        return User.model_validate(user_orm) if user_orm else None
