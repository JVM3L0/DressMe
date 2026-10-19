from application.interfaces.user_repository import UserRepository
from domain.entities.user import User
from domain.exceptions.auth import NotAuthenticatedError
from domain.ports.token_service import TokenService


class GetCurrentUserUseCase:
    def __init__(self, repository: UserRepository, token_service: TokenService):
        self.repository = repository
        self.token_service = token_service

    async def execute(self, access_token: str | None) -> User:
        if not access_token:
            raise NotAuthenticatedError()
        user_id = self.token_service.verify_token(access_token)
        # O token pode ser válido e o usuário já ter sido removido
        user = await self.repository.get_by_uid(user_id) if user_id else None
        if user is None:
            raise NotAuthenticatedError()
        return user
