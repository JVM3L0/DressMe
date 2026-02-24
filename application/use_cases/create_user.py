from domain.ports.password_hasher import PasswordHasher
from application.interfaces.user_repository import UserRepository
from domain.entities.user import User


class CreateUserUseCase:
    def __init__(self, repository: UserRepository, password_hasher: PasswordHasher):
        self.repository = repository
        self.password_hasher = password_hasher

    async def execute(self, username: str, email: str, raw_password: str) -> User:
        hashed_password = self.password_hasher.hash(password=raw_password)

        new_user = User(username=username, email=email, hashed_password=hashed_password)

        return await self.repository.save(new_user)
