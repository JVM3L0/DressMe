from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import SQLLifeCycleMixin, SQLUUIDMixin


class UserOrm(Base, SQLUUIDMixin, SQLLifeCycleMixin):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(), nullable=False)
