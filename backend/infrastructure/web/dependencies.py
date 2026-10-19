from typing import Annotated

from fastapi import Depends
from fastapi.security import APIKeyCookie
from sqlalchemy.ext.asyncio import AsyncSession

from application.interfaces.user_repository import UserRepository
from application.use_cases.authenticate_user import AuthenticateUserUseCase
from application.use_cases.create_user import CreateUserUseCase
from application.use_cases.get_current_user import GetCurrentUserUseCase
from config import settings
from domain.entities.user import User
from domain.ports.password_hasher import PasswordHasher
from domain.ports.token_service import TokenService
from infrastructure.auth.bcrypt_hasher import BcryptHasher, make_dummy_hash
from infrastructure.auth.jwt_service import JWTService
from infrastructure.persistence.database import get_db_session
from infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)

SESSION_COOKIE = "virtualfit_session"

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


def get_user_repository(session: SessionDep) -> UserRepository:
    return SQLAlchemyUserRepository(session)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


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


# Calculado uma vez, com o mesmo custo dos hashes reais
_dummy_hash = make_dummy_hash()


def get_dummy_hash() -> str:
    return _dummy_hash


# Também descreve o cookie no OpenAPI (cadeado no /docs). Sem `auto_error`,
# a ausência do cookie vira o mesmo 401 de um token inválido.
session_cookie = APIKeyCookie(
    name=SESSION_COOKIE, auto_error=False, description="Sessão criada pelo login."
)


def get_create_user_use_case(
    repository: UserRepositoryDep, password_hasher: PasswordHasherDep
) -> CreateUserUseCase:
    return CreateUserUseCase(repository=repository, password_hasher=password_hasher)


CreateUserUseCaseDep = Annotated[CreateUserUseCase, Depends(get_create_user_use_case)]


def get_authenticate_user_use_case(
    repository: UserRepositoryDep,
    password_hasher: PasswordHasherDep,
    token_service: TokenServiceDep,
    dummy_hash: Annotated[str, Depends(get_dummy_hash)],
) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(
        repository=repository,
        password_hasher=password_hasher,
        token_service=token_service,
        dummy_hash=dummy_hash,
    )


AuthenticateUserUseCaseDep = Annotated[
    AuthenticateUserUseCase, Depends(get_authenticate_user_use_case)
]


def get_current_user_use_case(
    repository: UserRepositoryDep, token_service: TokenServiceDep
) -> GetCurrentUserUseCase:
    return GetCurrentUserUseCase(repository=repository, token_service=token_service)


async def get_current_user(
    access_token: Annotated[str | None, Depends(session_cookie)],
    use_case: Annotated[GetCurrentUserUseCase, Depends(get_current_user_use_case)],
) -> User:
    return await use_case.execute(access_token)


CurrentUserDep = Annotated[User, Depends(get_current_user)]
