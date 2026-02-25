from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from application.use_cases.auth_user import AuthUserUseCase
from application.use_cases.token_create import CreateTokenUseCase
from domain.exceptions.http_exceptions import InvalidCredentialsError
from infrastructure.auth.bcrypt_hasher import BcryptHasher
from infrastructure.auth.jwt_service import JWTService
from infrastructure.persistence.database import get_db_session
from infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from infrastructure.web.schemas.token_schemes import TokenResponse
from infrastructure.web.schemas.user_schemes import UserLoginRequest

router = APIRouter(prefix="/auth")


@router.post(
    "/login/",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "E-mail ou senha incorretos."},
    },
    description="Recebe as credenciais e retorna o token de acesso."
)
async def auth_user(
    user_in: UserLoginRequest, session: AsyncSession = Depends(get_db_session)
):
    user = await AuthUserUseCase(
        SQLAlchemyUserRepository(session=session), password_hasher=BcryptHasher()
    ).execute(email=user_in.email, raw_password=user_in.password)

    if user:
        return await CreateTokenUseCase(token_service=JWTService()).execute(
            user_uid=user.uid
        )

    raise InvalidCredentialsError()
