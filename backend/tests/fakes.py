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


class FakePasswordHasher:
    def __init__(self) -> None:
        self.hashed: list[str] = []

    async def hash(self, password: str) -> str:
        self.hashed.append(password)
        return f"hashed:{password}"

    async def verify(self, password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed:{password}"
