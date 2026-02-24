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
