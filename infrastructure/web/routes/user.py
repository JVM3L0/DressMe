from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from application.use_cases.create_user import CreateUserUseCase
from infrastructure.auth.bcrypt_hasher import BcryptHasher
from infrastructure.persistence.database import get_db_session
from infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from infrastructure.web.schemas.user_schemes import UserCreate, UserPublic

router = APIRouter(prefix="/users")


@router.post("/", response_model=UserPublic)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db_session)):
    use_case = CreateUserUseCase(
        repository=SQLAlchemyUserRepository(db), password_hasher=BcryptHasher()
    )
    user_out = await use_case.execute(user_in.username, user_in.email, user_in.password)

    return user_out
