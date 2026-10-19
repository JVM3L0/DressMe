from pydantic import BaseModel, EmailStr, field_validator

from .mixins import LifeCycleMixin, UUIDMixin


def normalize_email(email: str) -> str:
    """E-mails são únicos sem diferenciar maiúsculas e minúsculas"""
    return email.strip().lower()


def normalize_username(username: str) -> str:
    """Preserva a grafia escolhida pelo usuário. A unicidade não diferencia
    maiúsculas e é garantida pelo repositório e pelo banco."""
    return username.strip()


class User(BaseModel, UUIDMixin, LifeCycleMixin):
    username: str
    email: EmailStr
    hashed_password: str

    @field_validator("username")
    @classmethod
    def _normalize_username(cls, value: str) -> str:
        return normalize_username(value)

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, value: str) -> str:
        return normalize_email(value)
