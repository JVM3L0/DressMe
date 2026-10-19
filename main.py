from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from domain.exceptions.user import UserAlreadyExistsError
from infrastructure.persistence.database import sessionmanager
from infrastructure.web.handlers import (
    request_validation_handler,
    user_already_exists_handler,
)
from infrastructure.web.routes.healthcheck import router as healthcheck_router
from infrastructure.web.routes.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    await sessionmanager.close()


app = FastAPI(lifespan=lifespan)

app.include_router(healthcheck_router)
app.include_router(user_router)

app.add_exception_handler(UserAlreadyExistsError, user_already_exists_handler)
app.add_exception_handler(RequestValidationError, request_validation_handler)
