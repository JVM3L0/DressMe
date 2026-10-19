from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded

from config import APP_VERSION
from domain.exceptions.auth import InvalidCredentialsError, NotAuthenticatedError
from domain.exceptions.user import UserAlreadyExistsError
from infrastructure.persistence.database import sessionmanager
from infrastructure.web.handlers import (
    invalid_credentials_handler,
    not_authenticated_handler,
    rate_limit_exceeded_handler,
    request_validation_handler,
    user_already_exists_handler,
)
from infrastructure.web.rate_limit import limiter
from infrastructure.web.routes.auth import router as auth_router
from infrastructure.web.routes.healthcheck import router as healthcheck_router
from infrastructure.web.routes.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    await sessionmanager.close()


app = FastAPI(title="VirtualFit API", version=APP_VERSION, lifespan=lifespan)
app.state.limiter = limiter

app.include_router(healthcheck_router)
app.include_router(user_router)
app.include_router(auth_router)

app.add_exception_handler(UserAlreadyExistsError, user_already_exists_handler)
app.add_exception_handler(InvalidCredentialsError, invalid_credentials_handler)
app.add_exception_handler(NotAuthenticatedError, not_authenticated_handler)
app.add_exception_handler(RequestValidationError, request_validation_handler)
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
