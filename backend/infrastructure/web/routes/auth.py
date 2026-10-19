from fastapi import APIRouter, Request, Response, status

from config import settings
from domain.entities.user import User
from infrastructure.web.dependencies import SESSION_COOKIE, AuthenticateUserUseCaseDep
from infrastructure.web.rate_limit import limiter
from infrastructure.web.schemas.auth_schemes import LoginRequest
from infrastructure.web.schemas.user_schemes import UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=UserPublic,
    responses={
        401: {"description": "E-mail ou senha incorretos."},
        429: {"description": "Limite de tentativas por IP atingido."},
    },
)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
async def login(
    request: Request,  # usado pelo rate limiter
    response: Response,
    credentials: LoginRequest,
    use_case: AuthenticateUserUseCaseDep,
) -> User:
    """Inicia a sessão num cookie `HttpOnly`: o JavaScript da página não lê o
    token, então um XSS não consegue roubá-lo. `SameSite=Strict` impede que
    outros sites enviem requisições com a sessão (CSRF)."""
    user, access_token = await use_case.execute(
        email=credentials.email, raw_password=credentials.password
    )
    response.set_cookie(
        SESSION_COOKIE,
        access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite="strict",
    )
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    """Encerra a sessão neste navegador. O token é stateless e continua
    válido até expirar (sem lista de revogação na PoC, ADR-0006)."""
    response.delete_cookie(
        SESSION_COOKIE,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite="strict",
    )
