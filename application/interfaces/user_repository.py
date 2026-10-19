from typing import Protocol

from domain.entities.user import User


class UserRepository(Protocol):
    async def save(self, user: User) -> User: ...

    async def exists_by_email_or_username(self, email: str, username: str) -> bool: ...
