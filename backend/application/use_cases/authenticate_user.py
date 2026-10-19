from typing import NamedTuple

from application.interfaces.user_repository import UserRepository
from domain.entities.user import User, normalize_email
from domain.exceptions.auth import InvalidCredentialsError
from domain.ports.password_hasher import PasswordHasher
from domain.ports.token_service import TokenService


class AuthenticatedUser(NamedTuple):
    user: User
    access_token: str


class AuthenticateUserUseCase:
    def __init__(
        self,
        repository: UserRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
        dummy_hash: str,
    ):
        """`dummy_hash` é um hash qualquer do mesmo algoritmo, verificado
        quando o e-mail não existe: assim a resposta leva o mesmo tempo nos
        dois casos e não revela quem tem conta."""
        self.repository = repository
        self.password_hasher = password_hasher
        self.token_service = token_service
        self.dummy_hash = dummy_hash

    async def execute(self, email: str, raw_password: str) -> AuthenticatedUser:
        user = await self.repository.get_by_email(normalize_email(email))

        hashed_password = user.hashed_password if user else self.dummy_hash
        password_matches = await self.password_hasher.verify(
            raw_password, hashed_password
        )
        if user is None or not password_matches:
            raise InvalidCredentialsError()

        return AuthenticatedUser(
            user=user, access_token=self.token_service.create_access_token(user.uid)
        )
