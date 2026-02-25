import uuid

from domain.ports.token_service import TokenService


class CreateTokenUseCase:
    def __init__(self, token_service: TokenService):
        self.token_service = token_service

    async def execute(self, user_uid: uuid.UUID) -> dict:
        return self.token_service.create_access_token(user_uid)
