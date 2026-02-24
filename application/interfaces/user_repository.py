from typing import Optional, Protocol
from uuid import UUID

from pydantic import EmailStr

from domain.entities.user import User


class UserRepository(Protocol):
    async def save(self, user: User) -> User: ...

    # async def delete(self, user_id: UUID) -> User: ...

    # async def update(self, user_id: UUID) -> User: ...

    # async def get_by_email(self, email: EmailStr) -> Optional[User]: ...

    # async def get_by_id(self, user_id: UUID) -> Optional[User]: ...
