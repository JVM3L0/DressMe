from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded


async def user_already_exists_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Já existe um usuário com esse e-mail ou username."},
    )


async def invalid_credentials_handler(request: Request, exc: Exception) -> JSONResponse:
    # A mesma mensagem para e-mail inexistente e senha errada
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "E-mail ou senha incorretos."},
    )


async def not_authenticated_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Faça login para continuar."},
    )


async def request_validation_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Igual ao handler padrão do FastAPI, mas sem ecoar o valor enviado
    (`input`), que pode conter senhas."""
    errors = [
        {key: value for key, value in error.items() if key != "input"}
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": jsonable_encoder(errors)},
    )


async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    # Retry-After com a duração da janela: limite superior seguro para o cliente
    retry_after = exc.limit.limit.get_expiry()
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Muitas requisições. Tente novamente mais tarde."},
        headers={"Retry-After": str(retry_after)},
    )
