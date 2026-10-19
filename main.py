from fastapi import FastAPI

from domain.exceptions.user import UserAlreadyExistsError
from infrastructure.web.handlers import user_already_exists_handler
from infrastructure.web.routes.healthcheck import router as healthcheck_router
from infrastructure.web.routes.user import router as user_router

app = FastAPI()

app.include_router(healthcheck_router)
app.include_router(user_router)

app.add_exception_handler(UserAlreadyExistsError, user_already_exists_handler)
