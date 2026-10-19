from fastapi import APIRouter

router = APIRouter(prefix="/healthcheck")


@router.get("/")
async def healthcheck():
    return {"status": "healthy"}
