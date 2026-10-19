import uuid

import pytest

from application.use_cases.get_current_user import GetCurrentUserUseCase
from domain.exceptions.auth import NotAuthenticatedError
from tests.fakes import FakeTokenService, FakeUserRepository, make_user

pytestmark = pytest.mark.anyio


@pytest.fixture
def repository() -> FakeUserRepository:
    repository = FakeUserRepository()
    repository.users.append(make_user())
    return repository


@pytest.fixture
def use_case(repository) -> GetCurrentUserUseCase:
    return GetCurrentUserUseCase(
        repository=repository, token_service=FakeTokenService()
    )


async def test_returns_user_of_valid_token(use_case, repository):
    user = repository.users[0]

    assert await use_case.execute(f"token:{user.uid}") == user


@pytest.mark.parametrize("token", [None, "", "invalido", "token:nao-e-uuid"])
async def test_rejects_missing_or_invalid_token(use_case, token):
    with pytest.raises(NotAuthenticatedError):
        await use_case.execute(token)


async def test_rejects_token_of_removed_user(use_case):
    with pytest.raises(NotAuthenticatedError):
        await use_case.execute(f"token:{uuid.uuid4()}")
