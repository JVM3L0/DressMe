import uuid
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, EmailStr, Field, StringConstraints


class UserCreate(BaseModel):
    username: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=3, max_length=255)
    ]
    email: Annotated[EmailStr, Field(max_length=255)]
    password: Annotated[str, Field(min_length=8)]


class UserPublic(BaseModel, from_attributes=True):
    uid: uuid.UUID
    username: str
    email: EmailStr
    created_at: AwareDatetime
