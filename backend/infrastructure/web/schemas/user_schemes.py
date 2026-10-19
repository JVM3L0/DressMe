import uuid
from typing import Annotated, Any

from pydantic import (
    AwareDatetime,
    BaseModel,
    BeforeValidator,
    EmailStr,
    Field,
    StringConstraints,
    ValidationInfo,
    field_validator,
)
from pydantic_core import PydanticCustomError

from domain.entities.user import normalize_email, normalize_username
from domain.password_policy import PasswordProblem, password_problem
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
            f"{BCRYPT_MAX_PASSWORD_BYTES} bytes. Senhas comuns e senhas que "
            "contêm o username ou o e-mail são recusadas.",
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

    @field_validator("password")
    @classmethod
    def _password_follows_policy(cls, value: str, info: ValidationInfo) -> str:
        # `info.data` só tem os campos anteriores que passaram na validação
        problem = password_problem(
            value,
            username=info.data.get("username", ""),
            email=info.data.get("email", ""),
        )
        if problem:
            raise PydanticCustomError(problem.value, _PASSWORD_MESSAGES[problem])
        return value


_PASSWORD_MESSAGES = {
    PasswordProblem.COMMON: "Essa senha é muito comum. Escolha outra.",
    PasswordProblem.PERSONAL: "A senha não pode conter o username ou o e-mail.",
}


class UserPublic(BaseModel, from_attributes=True):
    uid: uuid.UUID
    username: str
    email: EmailStr
    created_at: AwareDatetime
