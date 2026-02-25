from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from domain.exceptions.http_exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from infrastructure.web.handlers import (
    invalid_credentials_handler,
    user_already_exists_handler,
)
from infrastructure.web.routes.auth import router as auth_router
from infrastructure.web.routes.healthcheck import router as healthcheck_router
from infrastructure.web.routes.user import router as user_router

app = FastAPI()

app.include_router(healthcheck_router)
app.include_router(user_router)
app.include_router(auth_router)

app.add_exception_handler(
    InvalidCredentialsError,
    invalid_credentials_handler,
)
app.add_exception_handler(
    UserAlreadyExistsError,
    user_already_exists_handler,
)


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
    )
