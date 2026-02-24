import uuid

from pydantic import BaseModel, EmailStr, AwareDatetime


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel, from_attributes=True):
    uid: uuid.UUID
    username: str
    email: EmailStr
    created_at: AwareDatetime
