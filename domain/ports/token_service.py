from uuid import UUID
from typing import Protocol, Optional


class TokenService(Protocol):
    def create_access_token(self, user_id: UUID) -> str: ...
    def verify_token(self, token: str) -> Optional[UUID]: ...
