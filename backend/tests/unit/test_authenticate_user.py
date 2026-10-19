import pytest

from application.use_cases.authenticate_user import AuthenticateUserUseCase
from domain.exceptions.auth import InvalidCredentialsError
from tests.fakes import (
    FakePasswordHasher,
    FakeTokenService,
    FakeUserRepository,
    make_user,
)

pytestmark = pytest.mark.anyio

DUMMY_HASH = "dummy-hash"


class RecordingHasher(FakePasswordHasher):
    def __init__(self) -> None:
        super().__init__()
        self.verified: list[str] = []

    async def verify(self, password: str, hashed_password: str) -> bool:
        self.verified.append(hashed_password)
        return await super().verify(password, hashed_password)


@pytest.fixture
def hasher() -> RecordingHasher:
    return RecordingHasher()


@pytest.fixture
def repository() -> FakeUserRepository:
    repository = FakeUserRepository()
    repository.users.append(make_user(hashed_password="hashed:senha-segura"))
    return repository


@pytest.fixture
def use_case(repository, hasher) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(
        repository=repository,
        password_hasher=hasher,
        token_service=FakeTokenService(),
        dummy_hash=DUMMY_HASH,
    )


async def test_returns_user_and_token_for_valid_credentials(use_case, repository):
    user, token = await use_case.execute("joao@example.com", "senha-segura")

    assert user == repository.users[0]
    assert token == f"token:{user.uid}"


async def test_email_is_case_insensitive(use_case):
    user, _ = await use_case.execute("  JOAO@Example.com ", "senha-segura")

    assert user.username == "joao"


async def test_rejects_wrong_password(use_case):
    with pytest.raises(InvalidCredentialsError):
        await use_case.execute("joao@example.com", "senha-errada")


async def test_rejects_unknown_email_after_checking_the_dummy_hash(use_case, hasher):
    # Mesmo trabalho que uma senha errada: o tempo não revela quem tem conta
    with pytest.raises(InvalidCredentialsError):
        await use_case.execute("ninguem@example.com", "senha-segura")

    assert hasher.verified == [DUMMY_HASH]


async def test_unknown_email_and_wrong_password_raise_the_same_error(use_case):
    with pytest.raises(InvalidCredentialsError) as unknown:
        await use_case.execute("ninguem@example.com", "x")
    with pytest.raises(InvalidCredentialsError) as wrong:
        await use_case.execute("joao@example.com", "x")

    assert str(unknown.value) == str(wrong.value)
