import pytest

from domain.password_policy import PasswordProblem, password_problem


@pytest.mark.parametrize(
    "password", ["12345678", "password", "PassWord", "iloveyou", "senha123"]
)
def test_rejects_common_passwords_ignoring_case(password):
    assert password_problem(password) is PasswordProblem.COMMON


@pytest.mark.parametrize(
    ("password", "username", "email"),
    [
        ("Joao.Silva-2026", "joao.silva", "outro@example.com"),
        ("meu-JOAO-favorito", "Joao", "x@example.com"),
        ("mariana@casa!", "outro", "mariana@example.com"),
    ],
)
def test_rejects_passwords_containing_username_or_email(password, username, email):
    assert (
        password_problem(password, username=username, email=email)
        is PasswordProblem.PERSONAL
    )


def test_ignores_short_personal_fragments():
    # "ana" aparece por acaso em "banana"; só trechos de 4+ caracteres contam
    assert password_problem("banana-split-azul", username="ana") is None


@pytest.mark.parametrize(
    "password", ["senha-segura", "cavalo correto bateria", "Tr0ca-de-roupa"]
)
def test_accepts_uncommon_passwords(password):
    assert password_problem(password, username="joao", email="joao@x.com") is None


def test_policy_has_no_composition_rules():
    # NIST SP 800-63B: sem exigir maiúsculas, números ou símbolos
    assert password_problem("roupas do fim de semana") is None
