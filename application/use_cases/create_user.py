from application.interfaces.user_repository import UserRepository
from domain.entities.user import User
from domain.exceptions.http_exceptions import UserAlreadyExistsError
from domain.ports.password_hasher import PasswordHasher


class CreateUserUseCase:
    def __init__(self, repository: UserRepository, password_hasher: PasswordHasher):
        self.repository = repository
        self.password_hasher = password_hasher

    async def execute(self, username: str, email: str, raw_password: str) -> User:

        if await self.repository.get_by_email(email):
            raise UserAlreadyExistsError()

        hashed_password = self.password_hasher.hash(password=raw_password)

        new_user = User(username=username, email=email, hashed_password=hashed_password)

        return await self.repository.save(new_user)
