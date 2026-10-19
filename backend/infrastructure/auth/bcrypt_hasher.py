import secrets

import bcrypt
from anyio import to_thread

# O bcrypt só considera os primeiros 72 bytes da senha (e a versão 5+ recusa
# senhas maiores)
BCRYPT_MAX_PASSWORD_BYTES = 72

DEFAULT_ROUNDS = 12


def make_dummy_hash(rounds: int = DEFAULT_ROUNDS) -> str:
    """Hash de uma senha aleatória, para verificar quando o usuário não
    existe e igualar o tempo de resposta do login"""
    password = secrets.token_urlsafe(16).encode("utf-8")
    return bcrypt.hashpw(password, bcrypt.gensalt(rounds)).decode("utf-8")


class BcryptHasher:
    def __init__(self, rounds: int = DEFAULT_ROUNDS) -> None:
        self.rounds = rounds

    async def hash(self, password: str) -> str:
        return await to_thread.run_sync(self._hash, password)

    async def verify(self, password: str, hashed_password: str) -> bool:
        return await to_thread.run_sync(self._verify, password, hashed_password)

    def _hash(self, password: str) -> str:
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(self.rounds))

        return hashed.decode("utf-8")

    def _verify(self, password: str, hashed_password: str) -> bool:
        pwd_bytes = password.encode("utf-8")
        if len(pwd_bytes) > BCRYPT_MAX_PASSWORD_BYTES:
            return False

        return bcrypt.checkpw(pwd_bytes, hashed_password.encode("utf-8"))
