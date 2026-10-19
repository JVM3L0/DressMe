from sqlalchemy import exists, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.user import User
from domain.exceptions.user import UserAlreadyExistsError
from infrastructure.persistence.models.user_model import UserOrm


class SQLAlchemyUserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, user: User) -> User:

        model = UserOrm(
            uid=user.uid,
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            created_at=user.created_at,
        )

        self.session.add(model)
        try:
            await self.session.commit()
        except IntegrityError as exc:
            # Cadastro concorrente que passou pela checagem do caso de uso
            await self.session.rollback()
            raise UserAlreadyExistsError() from exc
        await self.session.refresh(model)

        return User.model_validate(model, from_attributes=True)

    async def exists_by_email_or_username(self, email: str, username: str) -> bool:
        stmt = select(
            exists().where(
                or_(
                    UserOrm.email == email,
                    func.lower(UserOrm.username) == username.lower(),
                )
            )
        )

        return bool(await self.session.scalar(stmt))
