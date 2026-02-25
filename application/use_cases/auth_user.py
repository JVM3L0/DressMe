from application.interfaces.user_repository import UserRepository
from domain.entities.user import User
from domain.ports.password_hasher import PasswordHasher


class AuthUserUseCase:
    def __init__(self, repository: UserRepository, password_hasher: PasswordHasher):
        self.repository = repository
        self.password_hasher = password_hasher

    async def execute(self, email: str, raw_password: str) -> User | None:
        user = await self.repository.get_by_email(email)
        if not user:
            return None

        return (
            user
            if self.password_hasher.verify(
                hashed_password=user.hashed_password, password=raw_password
            )
            else None
        )
