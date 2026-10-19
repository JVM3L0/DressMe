from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import SQLLifeCycleMixin, SQLUUIDMixin


class UserOrm(Base, SQLUUIDMixin, SQLLifeCycleMixin):
    __tablename__ = "users"
    # Com os índices únicos, garante unicidade sem diferenciar maiúsculas
    # mesmo para escritas feitas fora da aplicação
    __table_args__ = (
        CheckConstraint("email = lower(email)", name="email_lowercase"),
        CheckConstraint("username = lower(username)", name="username_lowercase"),
    )

    username: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(), nullable=False)
