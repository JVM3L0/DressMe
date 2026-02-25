from typing import Protocol
import uuid

from domain.entities.user import User


class UserRepository(Protocol):
    async def save(self, user: User) -> User: ...

    async def update(self, user: User) -> User: ...

    async def get_by_email(self, email: str) -> User | None: ...

    async def get_by_id(self, user_uid: uuid.UUID) -> User | None: ...
