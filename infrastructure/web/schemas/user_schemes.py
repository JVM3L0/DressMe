import uuid
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: Annotated[str, Field(description="Nome de usuário.")]
    email: Annotated[
        EmailStr, Field(description="E-mail de acesso.", example="user@example.com")
    ]
    password: Annotated[str, Field(description="Senha de acesso.", min_length=8)]


class UserLoginRequest(BaseModel):
    email: Annotated[
        EmailStr, Field(description="E-mail de acesso.", example="user@example.com")
    ]
    password: Annotated[str, Field(description="Senha de acesso.", min_length=8)]


class UserPublic(BaseModel, from_attributes=True):
    uid: uuid.UUID
    username: str
    email: EmailStr
    created_at: AwareDatetime
