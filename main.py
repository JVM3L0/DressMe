from fastapi import FastAPI

from infrastructure.web.routes.healthcheck import router as healthcheck_router
from infrastructure.web.routes.user import router as user_router

app = FastAPI()

app.include_router(healthcheck_router)
app.include_router(user_router)
