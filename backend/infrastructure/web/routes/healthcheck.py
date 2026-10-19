from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from config import APP_VERSION

router = APIRouter(prefix="/healthcheck", tags=["healthcheck"])


class HealthcheckResponse(BaseModel):
    status: Literal["healthy"]
    version: str


@router.get("/")
async def healthcheck() -> HealthcheckResponse:
    return HealthcheckResponse(status="healthy", version=APP_VERSION)
