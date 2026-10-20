from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from domain.exceptions.outfit import InvalidOutfitError, OutfitProblem


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


async def resource_not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Não encontrado."},
    )


async def image_too_large_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
        content={"detail": "A imagem passa de 10 MB."},
    )


async def invalid_image_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        content={"detail": "Envie uma imagem JPEG ou PNG."},
    )


_OUTFIT_MESSAGES = {
    OutfitProblem.EMPTY: "Escolha ao menos uma peça.",
    OutfitProblem.DUPLICATE_CATEGORY: "Use no máximo uma peça por categoria.",
    OutfitProblem.ONE_PIECE_CONFLICT: (
        "Uma peça única não combina com parte de cima ou de baixo."
    ),
    OutfitProblem.DUPLICATE_GARMENT: "Não repita a mesma peça.",
    OutfitProblem.TOO_MANY_ACCESSORIES: "Use no máximo 4 acessórios.",
    OutfitProblem.UNKNOWN_GARMENT: "Alguma das peças não existe mais.",
}


async def invalid_outfit_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, InvalidOutfitError)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": _OUTFIT_MESSAGES[exc.problem], "code": exc.problem.value},
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
