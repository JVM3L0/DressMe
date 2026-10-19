from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from application.use_cases.create_user import CreateUserUseCase
from config import settings
from domain.ports.password_hasher import PasswordHasher
from domain.ports.token_service import TokenService
from infrastructure.auth.bcrypt_hasher import BcryptHasher
from infrastructure.auth.jwt_service import JWTService
from infrastructure.persistence.database import get_db_session
from infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


def get_password_hasher() -> PasswordHasher:
    return BcryptHasher()


PasswordHasherDep = Annotated[PasswordHasher, Depends(get_password_hasher)]


# Criado na importação: configuração inválida (ex.: chave curta para o
# algoritmo) impede a aplicação de subir, em vez de falhar na primeira requisição
_token_service = JWTService(
    secret_key=settings.SECRET_KEY,
    algorithm=settings.JWT_ALGORITHM,
    expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
)


def get_token_service() -> TokenService:
    return _token_service


TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]


def get_create_user_use_case(
    session: SessionDep, password_hasher: PasswordHasherDep
) -> CreateUserUseCase:
    return CreateUserUseCase(
        repository=SQLAlchemyUserRepository(session),
        password_hasher=password_hasher,
    )


CreateUserUseCaseDep = Annotated[CreateUserUseCase, Depends(get_create_user_use_case)]
