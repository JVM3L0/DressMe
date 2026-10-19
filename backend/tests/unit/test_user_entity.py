import uuid

import pytest
from pydantic import ValidationError

from domain.entities.user import normalize_email, normalize_username
from tests.fakes import make_user


def test_normalize_email_lowercases_and_strips():
    assert normalize_email("  Joao@Example.COM ") == "joao@example.com"


def test_normalize_username_strips_and_preserves_case():
    assert normalize_username("  Joao.Silva ") == "Joao.Silva"


def test_user_lowercases_email_and_preserves_username_case():
    user = make_user(username=" JoaO ", email="JOAO@Example.com")

    assert user.username == "JoaO"
    assert user.email == "joao@example.com"


def test_user_generates_uid_and_aware_created_at():
    user = make_user()

    assert isinstance(user.uid, uuid.UUID)
    assert user.created_at.utcoffset() is not None
    assert user.updated_at is None


def test_users_get_distinct_uids():
    assert make_user().uid != make_user().uid


def test_user_rejects_invalid_email():
    with pytest.raises(ValidationError):
        make_user(email="nao-e-email")
