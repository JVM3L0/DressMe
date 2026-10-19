from typing import Protocol
from uuid import UUID

from domain.entities.user import User


class UserRepository(Protocol):
    async def save(self, user: User) -> User: ...

    async def exists_by_email_or_username(self, email: str, username: str) -> bool: ...

    async def get_by_email(self, email: str) -> User | None: ...

    async def get_by_uid(self, uid: UUID) -> User | None: ...
