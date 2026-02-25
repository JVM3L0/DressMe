from fastapi import Request, status
from fastapi.responses import JSONResponse


async def invalid_credentials_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "E-mail ou senha incorretos."},
    )


async def user_already_exists_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Já existe um usuário com esse e-mail."},
    )
