import pytest
from pydantic import ValidationError

from infrastructure.web.schemas.user_schemes import UserCreate, UserPublic
from tests.fakes import make_user

VALID = {"username": "joao", "email": "joao@example.com", "password": "senha-segura"}


def make_user_create(**overrides) -> UserCreate:
    return UserCreate(**(VALID | overrides))


def error_fields(exc: pytest.ExceptionInfo[ValidationError]) -> set[str]:
    return {str(error["loc"][0]) for error in exc.value.errors()}


def test_user_create_accepts_valid_payload():
    user = make_user_create()

    assert user.model_dump() == VALID


def test_user_create_strips_username_preserving_case_and_lowercases_email():
    user = make_user_create(username="  Joao.Silva_1 ", email="Joao@Example.COM")

    assert user.username == "Joao.Silva_1"
    assert user.email == "joao@example.com"


@pytest.mark.parametrize(
    "username",
    ["ab", "   ab  ", "", "a" * 256, "joao silva", "joão", "joao@x", "joao!"],
)
def test_user_create_rejects_invalid_username(username):
    with pytest.raises(ValidationError) as exc:
        make_user_create(username=username)

    assert error_fields(exc) == {"username"}


@pytest.mark.parametrize("username", [123, None, ["joao"]])
def test_user_create_rejects_non_string_username(username):
    with pytest.raises(ValidationError) as exc:
        make_user_create(username=username)

    assert error_fields(exc) == {"username"}


@pytest.mark.parametrize("email", ["joao", "joao@", "@example.com", ""])
def test_user_create_rejects_invalid_email(email):
    with pytest.raises(ValidationError) as exc:
        make_user_create(email=email)

    assert error_fields(exc) == {"email"}


def test_user_create_rejects_email_longer_than_column():
    domain = f"{'b' * 63}.{'c' * 63}.{'d' * 63}.com"
    email = f"{'a' * 64}@{domain}"
    assert len(email) > 255

    with pytest.raises(ValidationError) as exc:
        make_user_create(email=email)

    assert error_fields(exc) == {"email"}


@pytest.mark.parametrize("password", ["", "1234567"])
def test_user_create_rejects_short_password(password):
    with pytest.raises(ValidationError) as exc:
        make_user_create(password=password)

    assert error_fields(exc) == {"password"}


def test_user_create_accepts_password_with_exactly_72_bytes():
    assert make_user_create(password="a" * 72).password == "a" * 72


@pytest.mark.parametrize(
    "password",
    [
        "a" * 73,
        "é" * 37,  # 37 caracteres, mas 74 bytes em UTF-8
    ],
)
def test_user_create_rejects_password_longer_than_72_bytes(password):
    with pytest.raises(ValidationError) as exc:
        make_user_create(password=password)

    assert error_fields(exc) == {"password"}
    assert "72 bytes" in str(exc.value)


def test_user_public_does_not_expose_password():
    public = UserPublic.model_validate(make_user(), from_attributes=True)

    assert "hashed_password" not in public.model_dump()


@pytest.mark.parametrize(
    ("overrides", "error_type"),
    [
        ({"password": "12345678"}, "password_common"),
        ({"password": "joao-1234567"}, "password_personal"),
        (
            {"email": "mariana@example.com", "password": "mariana-2026"},
            "password_personal",
        ),
    ],
)
def test_user_create_applies_password_policy(overrides, error_type):
    with pytest.raises(ValidationError) as exc:
        make_user_create(**overrides)

    [error] = exc.value.errors()
    assert error["loc"] == ("password",)
    assert error["type"] == error_type


def test_user_create_checks_policy_even_when_username_is_invalid():
    with pytest.raises(ValidationError) as exc:
        make_user_create(username="x", password="12345678")

    assert {e["type"] for e in exc.value.errors()} >= {"password_common"}
