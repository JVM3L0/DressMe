from typing import Protocol


class PasswordHasher(Protocol):
    """Protocolo para serviço de hashing.

    Os métodos são assíncronos porque hashing é custoso de CPU e as
    implementações não devem bloquear o event loop.
    """

    async def hash(self, password: str) -> str: ...
    async def verify(self, password: str, hashed_password: str) -> bool: ...
