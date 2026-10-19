import threading

import pytest

from infrastructure.auth import bcrypt_hasher
from infrastructure.auth.bcrypt_hasher import BcryptHasher

pytestmark = pytest.mark.anyio


@pytest.fixture
def hasher() -> BcryptHasher:
    # Custo mínimo do bcrypt para os testes rodarem rápido
    return BcryptHasher(rounds=4)


async def test_hash_is_not_plain_text_and_uses_configured_rounds(hasher):
    hashed = await hasher.hash("senha-segura")

    assert hashed != "senha-segura"
    assert hashed.startswith("$2b$04$")


async def test_hash_uses_random_salt(hasher):
    assert await hasher.hash("senha-segura") != await hasher.hash("senha-segura")


async def test_default_rounds_is_12():
    assert BcryptHasher().rounds == 12


async def test_verify_accepts_correct_password(hasher):
    hashed = await hasher.hash("senha-segura")

    assert await hasher.verify("senha-segura", hashed) is True


async def test_verify_rejects_wrong_password(hasher):
    hashed = await hasher.hash("senha-segura")

    assert await hasher.verify("senha-errada", hashed) is False


async def test_verify_supports_multibyte_password(hasher):
    hashed = await hasher.hash("çãoé-senha")

    assert await hasher.verify("çãoé-senha", hashed) is True


async def test_verify_rejects_password_longer_than_72_bytes(hasher):
    hashed = await hasher.hash("a" * 72)

    assert await hasher.verify("a" * 73, hashed) is False


async def test_hash_rejects_password_longer_than_72_bytes(hasher):
    with pytest.raises(ValueError):
        await hasher.hash("a" * 73)


async def test_hash_runs_outside_event_loop_thread(hasher, monkeypatch):
    threads: list[threading.Thread] = []
    original_hashpw = bcrypt_hasher.bcrypt.hashpw

    def spy_hashpw(*args):
        threads.append(threading.current_thread())
        return original_hashpw(*args)

    monkeypatch.setattr(bcrypt_hasher.bcrypt, "hashpw", spy_hashpw)

    await hasher.hash("senha-segura")

    assert threads
    assert threads[0] is not threading.current_thread()
