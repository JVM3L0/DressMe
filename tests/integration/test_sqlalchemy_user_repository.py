import pytest
from sqlalchemy import func, insert, select
from sqlalchemy.exc import IntegrityError

from domain.exceptions.user import UserAlreadyExistsError
from infrastructure.persistence.models.user_model import UserOrm
from infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from tests.fakes import make_user

pytestmark = [pytest.mark.anyio, pytest.mark.integration]


@pytest.fixture
def repository(session) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(session)


async def count_users(session) -> int:
    return await session.scalar(select(func.count()).select_from(UserOrm))


async def test_save_persists_user_with_domain_uid_and_created_at(repository, session):
    user = make_user()

    saved = await repository.save(user)

    row = await session.get(UserOrm, user.uid)
    assert row is not None
    assert row.username == "joao"
    assert row.email == "joao@example.com"
    assert row.hashed_password == "hash"
    assert row.created_at == user.created_at
    assert saved.uid == user.uid
    assert saved.created_at == user.created_at


async def test_save_returns_user_loaded_from_database(repository):
    saved = await repository.save(make_user())

    assert saved.model_dump(exclude={"updated_at"}) == make_user(
        uid=saved.uid, created_at=saved.created_at
    ).model_dump(exclude={"updated_at"})


@pytest.mark.parametrize(
    "duplicate",
    [
        {"username": "outro"},  # mesmo e-mail
        {"email": "outro@example.com"},  # mesmo username
    ],
)
async def test_save_raises_user_already_exists_on_unique_violation(
    repository, session, duplicate
):
    await repository.save(make_user())

    with pytest.raises(UserAlreadyExistsError):
        await repository.save(make_user(**duplicate))

    # A sessão continua utilizável após o rollback
    assert await count_users(session) == 1


async def test_exists_returns_false_when_empty(repository):
    assert (
        await repository.exists_by_email_or_username("joao@example.com", "joao")
        is False
    )


@pytest.mark.parametrize(
    ("email", "username"),
    [
        ("joao@example.com", "outro"),
        ("outro@example.com", "joao"),
        ("joao@example.com", "joao"),
    ],
)
async def test_exists_matches_email_or_username(repository, email, username):
    await repository.save(make_user())

    assert await repository.exists_by_email_or_username(email, username) is True


async def test_exists_returns_false_for_other_user(repository):
    await repository.save(make_user())

    assert (
        await repository.exists_by_email_or_username("outro@example.com", "outro")
        is False
    )


@pytest.mark.parametrize(
    "overrides",
    [{"email": "Joao@example.com"}, {"username": "Joao"}],
)
async def test_database_rejects_non_lowercase_writes_outside_the_app(
    session, overrides
):
    values = {
        "uid": make_user().uid,
        "username": "joao",
        "email": "joao@example.com",
        "hashed_password": "hash",
    } | overrides

    with pytest.raises(IntegrityError, match="lowercase"):
        await session.execute(insert(UserOrm).values(**values))


async def test_database_errors_do_not_expose_query_parameters(repository, session):
    await repository.save(make_user(hashed_password="hash-secreto"))

    with pytest.raises(IntegrityError) as exc:
        await session.execute(
            insert(UserOrm).values(
                uid=make_user().uid,
                username="joao",
                email="joao@example.com",
                hashed_password="hash-secreto",
            )
        )

    assert "hash-secreto" not in str(exc.value)
    assert "parameters hidden" in str(exc.value)
