import uuid

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
        ("outro@example.com", "JOAO"),
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


def user_row(**overrides) -> dict:
    return {
        "uid": make_user().uid,
        "username": "joao",
        "email": "joao@example.com",
        "hashed_password": "hash",
    } | overrides


async def test_save_preserves_username_case(repository, session):
    user = make_user(username="Joao.Silva")

    await repository.save(user)

    assert (await session.get(UserOrm, user.uid)).username == "Joao.Silva"


async def test_database_rejects_non_lowercase_email_outside_the_app(session):
    with pytest.raises(IntegrityError, match="ck_users_email_lowercase"):
        await session.execute(
            insert(UserOrm).values(**user_row(email="Joao@example.com"))
        )


async def test_database_rejects_case_insensitive_duplicate_username(session):
    await session.execute(insert(UserOrm).values(**user_row(username="Joao")))

    with pytest.raises(IntegrityError, match="uq_users_username_lower"):
        await session.execute(
            insert(UserOrm).values(
                **user_row(username="JOAO", email="outro@example.com")
            )
        )


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


async def test_get_by_email_returns_saved_user(repository):
    saved = await repository.save(make_user())

    found = await repository.get_by_email("JOAO@example.com")

    assert found is not None
    assert found.uid == saved.uid
    assert found.hashed_password == "hash"


async def test_get_by_email_returns_none_when_missing(repository):
    assert await repository.get_by_email("ninguem@example.com") is None


async def test_get_by_uid_returns_saved_user_or_none(repository):
    saved = await repository.save(make_user())

    assert (await repository.get_by_uid(saved.uid)).email == "joao@example.com"
    assert await repository.get_by_uid(uuid.uuid4()) is None
