import pytest

from application.use_cases.create_user import CreateUserUseCase
from domain.exceptions.user import UserAlreadyExistsError
from tests.fakes import FakePasswordHasher, FakeUserRepository

pytestmark = pytest.mark.anyio


@pytest.fixture
def repository() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def hasher() -> FakePasswordHasher:
    return FakePasswordHasher()


@pytest.fixture
def use_case(repository, hasher) -> CreateUserUseCase:
    return CreateUserUseCase(repository=repository, password_hasher=hasher)


async def test_create_user_persists_user_with_hashed_password(use_case, repository):
    user = await use_case.execute("joao", "joao@example.com", "senha-segura")

    assert repository.users == [user]
    assert user.username == "joao"
    assert user.email == "joao@example.com"
    assert user.hashed_password == "hashed:senha-segura"


async def test_create_user_preserves_username_case_and_lowercases_email(use_case):
    user = await use_case.execute(" JoaO ", "Joao@Example.COM", "senha-segura")

    assert user.username == "JoaO"
    assert user.email == "joao@example.com"


@pytest.mark.parametrize(
    ("username", "email"),
    [
        ("outro", "joao@example.com"),
        ("outro", "JOAO@example.com"),
        ("joao", "outro@example.com"),
        ("JOAO", "outro@example.com"),
    ],
)
async def test_create_user_rejects_duplicates_ignoring_case(
    use_case, repository, username, email
):
    await use_case.execute("joao", "joao@example.com", "senha-segura")

    with pytest.raises(UserAlreadyExistsError):
        await use_case.execute(username, email, "senha-segura")

    assert len(repository.users) == 1


async def test_create_user_does_not_hash_password_when_user_exists(use_case, hasher):
    await use_case.execute("joao", "joao@example.com", "senha-segura")

    with pytest.raises(UserAlreadyExistsError):
        await use_case.execute("joao", "joao@example.com", "outra-senha")

    assert hasher.hashed == ["senha-segura"]


async def test_create_user_returns_what_repository_saved(hasher):
    class RepositoryReturningCopy(FakeUserRepository):
        async def save(self, user):
            await super().save(user)
            return user.model_copy(update={"username": "salvo"})

    use_case = CreateUserUseCase(
        repository=RepositoryReturningCopy(), password_hasher=hasher
    )

    user = await use_case.execute("joao", "joao@example.com", "senha-segura")

    assert user.username == "salvo"
