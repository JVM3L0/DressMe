from pydantic import BaseModel, EmailStr

from .mixins import LifeCycleMixin, UUIDMixin


class User(BaseModel, UUIDMixin, LifeCycleMixin, from_attributes=True):
    username: str
    email: EmailStr
    hashed_password: str
