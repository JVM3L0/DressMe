"""Política de senha (NIST SP 800-63B): recusa senhas comuns e senhas que
contêm o próprio username ou e-mail, sem regras de composição ("1 maiúscula,
1 símbolo"), que pouco ajudam e levam a senhas previsíveis."""

import gzip
from enum import StrEnum
from functools import cache
from pathlib import Path

# Senhas de 8+ caracteres da lista das 100 mil mais usadas em vazamentos, do
# NCSC do Reino Unido (via SecLists, licença MIT), em minúsculas
_COMMON_PASSWORDS_FILE = Path(__file__).parent / "data" / "common_passwords.txt.gz"

# Trechos mais curtos que isso aparecem por acaso em senhas boas (ex.: "ana")
_MIN_PERSONAL_FRAGMENT = 4


class PasswordProblem(StrEnum):
    COMMON = "password_common"
    PERSONAL = "password_personal"


@cache
def _common_passwords() -> frozenset[str]:
    with gzip.open(_COMMON_PASSWORDS_FILE, "rt", encoding="utf-8") as file:
        return frozenset(line.strip() for line in file if line.strip())


def password_problem(
    password: str, *, username: str = "", email: str = ""
) -> PasswordProblem | None:
    """Motivo para recusar a senha, ou `None` se ela for aceitável"""
    lowered = password.lower()
    if lowered in _common_passwords():
        return PasswordProblem.COMMON

    personal = (username.strip(), email.strip().partition("@")[0])
    if any(
        len(fragment) >= _MIN_PERSONAL_FRAGMENT and fragment.lower() in lowered
        for fragment in personal
    ):
        return PasswordProblem.PERSONAL

    return None
