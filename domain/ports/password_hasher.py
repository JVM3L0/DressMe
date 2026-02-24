from typing import Protocol


class PasswordHasher(Protocol):
    """Protocolo para serviço de hashing"""

    def hash(self, password: str) -> str: ...
    def verify(self, password: str, hashed_password: str) -> bool: ...
