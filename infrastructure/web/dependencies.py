from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from application.use_cases.create_user import CreateUserUseCase
from domain.ports.password_hasher import PasswordHasher
from infrastructure.auth.bcrypt_hasher import BcryptHasher
from infrastructure.persistence.database import get_db_session
from infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


def get_password_hasher() -> PasswordHasher:
    return BcryptHasher()


PasswordHasherDep = Annotated[PasswordHasher, Depends(get_password_hasher)]


def get_create_user_use_case(
    session: SessionDep, password_hasher: PasswordHasherDep
) -> CreateUserUseCase:
    return CreateUserUseCase(
        repository=SQLAlchemyUserRepository(session),
        password_hasher=password_hasher,
    )


CreateUserUseCaseDep = Annotated[CreateUserUseCase, Depends(get_create_user_use_case)]
