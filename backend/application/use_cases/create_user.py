from application.interfaces.user_repository import UserRepository
from domain.entities.user import User, normalize_email, normalize_username
from domain.exceptions.user import UserAlreadyExistsError
from domain.ports.password_hasher import PasswordHasher


class CreateUserUseCase:
    def __init__(self, repository: UserRepository, password_hasher: PasswordHasher):
        self.repository = repository
        self.password_hasher = password_hasher

    async def execute(self, username: str, email: str, raw_password: str) -> User:
        username = normalize_username(username)
        email = normalize_email(email)

        # O hash vem antes da checagem de propósito: assim o cadastro duplicado
        # leva o mesmo tempo que o novo, e o tempo não revela quem tem conta
        hashed_password = await self.password_hasher.hash(raw_password)

        if await self.repository.exists_by_email_or_username(
            email=email, username=username
        ):
            raise UserAlreadyExistsError()

        new_user = User(username=username, email=email, hashed_password=hashed_password)

        return await self.repository.save(new_user)
