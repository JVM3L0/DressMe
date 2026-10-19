import uuid

import jwt
import pendulum
import pytest

from config import settings
from infrastructure.auth.jwt_service import JWTService
from infrastructure.web.dependencies import get_token_service

SECRET = "s" * 32
USER_ID = uuid.UUID("12345678-1234-5678-1234-567812345678")


@pytest.fixture
def service() -> JWTService:
    return JWTService(secret_key=SECRET)


def encode(payload: dict, key: str = SECRET, algorithm: str = "HS256") -> str:
    return jwt.encode(payload, key, algorithm=algorithm)


def valid_claims(**overrides) -> dict:
    now = pendulum.now("UTC")
    return {
        "sub": str(USER_ID),
        "iat": now,
        "exp": now.add(minutes=5),
    } | overrides


def test_created_token_is_verified(service):
    token = service.create_access_token(USER_ID)

    assert service.verify_token(token) == USER_ID


def test_created_token_has_expected_claims(service):
    token = service.create_access_token(USER_ID)

    claims = jwt.decode(token, SECRET, algorithms=["HS256"])
    assert claims["sub"] == str(USER_ID)
    assert claims["exp"] - claims["iat"] == 15 * 60
    assert jwt.get_unverified_header(token)["alg"] == "HS256"


def test_expire_minutes_is_configurable():
    token = JWTService(SECRET, expire_minutes=60).create_access_token(USER_ID)

    claims = jwt.decode(token, SECRET, algorithms=["HS256"])
    assert claims["exp"] - claims["iat"] == 60 * 60


def test_expired_token_is_rejected(service):
    past = pendulum.now("UTC").subtract(hours=1)
    token = encode(valid_claims(iat=past, exp=past.add(minutes=15)))

    assert service.verify_token(token) is None


def test_token_signed_with_other_key_is_rejected(service):
    assert service.verify_token(encode(valid_claims(), key="o" * 32)) is None


def test_tampered_token_is_rejected(service):
    header, _, signature = service.create_access_token(USER_ID).split(".")
    forged_payload = encode(valid_claims(sub=str(uuid.uuid4()))).split(".")[1]

    assert service.verify_token(f"{header}.{forged_payload}.{signature}") is None


def test_unsigned_token_with_alg_none_is_rejected(service):
    token = jwt.encode(valid_claims(), key=None, algorithm="none")

    assert service.verify_token(token) is None


def test_token_with_other_algorithm_is_rejected(service):
    token = encode(valid_claims(), key=SECRET * 2, algorithm="HS512")

    assert service.verify_token(token) is None


@pytest.mark.parametrize(("algorithm", "key_bytes"), [("HS384", 48), ("HS512", 64)])
def test_stronger_algorithms_work_with_matching_key_size(algorithm, key_bytes):
    service = JWTService("k" * key_bytes, algorithm=algorithm)

    assert service.verify_token(service.create_access_token(USER_ID)) == USER_ID


@pytest.mark.parametrize("missing", ["sub", "exp", "iat"])
def test_token_missing_required_claim_is_rejected(service, missing):
    claims = {k: v for k, v in valid_claims().items() if k != missing}

    assert service.verify_token(encode(claims)) is None


@pytest.mark.parametrize("sub", ["nao-e-uuid", "", 123])
def test_token_with_invalid_subject_is_rejected(service, sub):
    assert service.verify_token(encode(valid_claims(sub=sub))) is None


@pytest.mark.parametrize("token", ["", "lixo", "a.b.c", "a.b"])
def test_malformed_token_is_rejected(service, token):
    assert service.verify_token(token) is None


@pytest.mark.parametrize("algorithm", ["none", "RS256", "ES256", "hs256"])
def test_unsupported_algorithm_is_refused(algorithm):
    with pytest.raises(ValueError, match="não suportado"):
        JWTService(SECRET, algorithm=algorithm)


@pytest.mark.parametrize(
    ("algorithm", "key_bytes"), [("HS256", 31), ("HS384", 47), ("HS512", 63)]
)
def test_secret_key_shorter_than_hash_is_refused(algorithm, key_bytes):
    with pytest.raises(ValueError, match=f"bytes para {algorithm}"):
        JWTService("k" * key_bytes, algorithm=algorithm)


def test_secret_key_length_is_measured_in_bytes():
    # 16 caracteres, mas 32 bytes em UTF-8
    assert JWTService("é" * 16).verify_token("lixo") is None
    with pytest.raises(ValueError):
        JWTService("é" * 15)


@pytest.mark.parametrize("minutes", [0, -1])
def test_non_positive_expiration_is_refused(minutes):
    with pytest.raises(ValueError, match="positivo"):
        JWTService(SECRET, expire_minutes=minutes)


def test_token_service_provider_uses_settings_and_is_reused():
    service = get_token_service()

    assert get_token_service() is service

    assert isinstance(service, JWTService)
    assert service.secret_key == settings.SECRET_KEY
    assert service.algorithm == settings.JWT_ALGORITHM
    assert service.expire_minutes == settings.ACCESS_TOKEN_EXPIRE_MINUTES
