from pydantic import BaseModel, EmailStr

from .mixins import LifeCycleMixin, UUIDMixin


class User(BaseModel, UUIDMixin, LifeCycleMixin):
    username: str
    email: EmailStr
    hashed_password: str
