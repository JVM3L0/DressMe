from fastapi import APIRouter, Request, status

from config import settings
from domain.entities.user import User
from infrastructure.web.dependencies import CreateUserUseCaseDep
from infrastructure.web.rate_limit import limiter
from infrastructure.web.schemas.user_schemes import UserCreate, UserPublic

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"description": "E-mail ou username já registrado."},
        429: {"description": "Limite de cadastros por IP atingido."},
    },
)
@limiter.limit(settings.RATE_LIMIT_SIGNUP)
async def create_user(
    request: Request,  # usado pelo rate limiter
    user_in: UserCreate,
    use_case: CreateUserUseCaseDep,
) -> User:
    return await use_case.execute(
        username=user_in.username, email=user_in.email, raw_password=user_in.password
    )
