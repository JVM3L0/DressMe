from uuid import UUID

from domain.entities.user import User


def make_user(**overrides) -> User:
    data = {
        "username": "joao",
        "email": "joao@example.com",
        "hashed_password": "hash",
    }
    return User(**(data | overrides))


class FakeUserRepository:
    def __init__(self) -> None:
        self.users: list[User] = []

    async def save(self, user: User) -> User:
        self.users.append(user)
        return user

    async def exists_by_email_or_username(self, email: str, username: str) -> bool:
        return any(
            u.email == email or u.username.lower() == username.lower()
            for u in self.users
        )

    async def get_by_email(self, email: str) -> User | None:
        return next((u for u in self.users if u.email == email.lower()), None)

    async def get_by_uid(self, uid: UUID) -> User | None:
        return next((u for u in self.users if u.uid == uid), None)


class FakePasswordHasher:
    def __init__(self) -> None:
        self.hashed: list[str] = []

    async def hash(self, password: str) -> str:
        self.hashed.append(password)
        return f"hashed:{password}"

    async def verify(self, password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed:{password}"


class FakeTokenService:
    """Token legível nos testes: `token:<uid>`"""

    def create_access_token(self, user_id: UUID) -> str:
        return f"token:{user_id}"

    def verify_token(self, token: str) -> UUID | None:
        prefix, _, uid = token.partition(":")
        try:
            return UUID(uid) if prefix == "token" else None
        except ValueError:
            return None
