from fastapi import APIRouter, status

from domain.entities.user import User
from infrastructure.web.dependencies import CreateUserUseCaseDep
from infrastructure.web.schemas.user_schemes import UserCreate, UserPublic

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "E-mail ou username já registrado."}},
)
async def create_user(user_in: UserCreate, use_case: CreateUserUseCaseDep) -> User:
    return await use_case.execute(
        username=user_in.username, email=user_in.email, raw_password=user_in.password
    )
