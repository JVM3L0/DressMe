import uuid
from typing import Annotated, Any

from pydantic import (
    AwareDatetime,
    BaseModel,
    BeforeValidator,
    EmailStr,
    Field,
    StringConstraints,
    field_validator,
)

from domain.entities.user import normalize_email, normalize_username
from infrastructure.auth.bcrypt_hasher import BCRYPT_MAX_PASSWORD_BYTES


def _normalize_username_input(value: Any) -> Any:
    # Remove espaços antes das restrições; valores que não são texto seguem
    # para a validação de tipo do Pydantic (422)
    return normalize_username(value) if isinstance(value, str) else value


Username = Annotated[
    str,
    BeforeValidator(_normalize_username_input),
    StringConstraints(
        min_length=3,
        max_length=255,
        pattern=r"^[A-Za-z0-9_.-]+$",
    ),
    Field(
        description="Letras, números, `_`, `.` ou `-`. A grafia é preservada, mas "
        "a unicidade não diferencia maiúsculas.",
        examples=["Joao.Silva"],
    ),
]


class UserCreate(BaseModel):
    username: Username
    email: Annotated[EmailStr, Field(max_length=255, examples=["joao@example.com"])]
    password: Annotated[
        str,
        Field(
            min_length=8,
            description=f"Mínimo de 8 caracteres e máximo de "
            f"{BCRYPT_MAX_PASSWORD_BYTES} bytes.",
        ),
    ]

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, value: str) -> str:
        return normalize_email(value)

    @field_validator("password")
    @classmethod
    def _password_fits_bcrypt(cls, value: str) -> str:
        if len(value.encode("utf-8")) > BCRYPT_MAX_PASSWORD_BYTES:
            raise ValueError(
                f"A senha deve ter no máximo {BCRYPT_MAX_PASSWORD_BYTES} bytes."
            )
        return value


class UserPublic(BaseModel, from_attributes=True):
    uid: uuid.UUID
    username: str
    email: EmailStr
    created_at: AwareDatetime
