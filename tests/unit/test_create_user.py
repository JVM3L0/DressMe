import pytest

from application.use_cases.create_user import CreateUserUseCase
from domain.entities.user import User
from domain.exceptions.user import UserAlreadyExistsError

pytestmark = pytest.mark.anyio


class FakeUserRepository:
    def __init__(self):
        self.users: list[User] = []

    async def save(self, user: User) -> User:
        self.users.append(user)
        return user

    async def exists_by_email_or_username(self, email: str, username: str) -> bool:
        return any(u.email == email or u.username == username for u in self.users)


class FakePasswordHasher:
    def hash(self, password: str) -> str:
        return f"hashed:{password}"

    def verify(self, password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed:{password}"


@pytest.fixture
def repository():
    return FakeUserRepository()


@pytest.fixture
def use_case(repository):
    return CreateUserUseCase(
        repository=repository, password_hasher=FakePasswordHasher()
    )


async def test_create_user_persists_user_with_hashed_password(use_case, repository):
    user = await use_case.execute("joao", "joao@example.com", "senha-segura")

    assert repository.users == [user]
    assert user.username == "joao"
    assert user.email == "joao@example.com"
    assert user.hashed_password == "hashed:senha-segura"


async def test_create_user_rejects_duplicate_email(use_case):
    await use_case.execute("joao", "joao@example.com", "senha-segura")

    with pytest.raises(UserAlreadyExistsError):
        await use_case.execute("outro", "joao@example.com", "senha-segura")


async def test_create_user_rejects_duplicate_username(use_case):
    await use_case.execute("joao", "joao@example.com", "senha-segura")

    with pytest.raises(UserAlreadyExistsError):
        await use_case.execute("joao", "outro@example.com", "senha-segura")
