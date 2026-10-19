from sqlalchemy import CheckConstraint, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import SQLLifeCycleMixin, SQLUUIDMixin


class UserOrm(Base, SQLUUIDMixin, SQLLifeCycleMixin):
    __tablename__ = "users"
    # E-mail é salvo em minúsculas; com o índice único, a unicidade não
    # diferencia maiúsculas mesmo para escritas feitas fora da aplicação
    __table_args__ = (CheckConstraint("email = lower(email)", name="email_lowercase"),)

    # Grafia preservada; unicidade sem diferenciar maiúsculas pelo índice
    # `uq_users_username_lower`, definido abaixo
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(), nullable=False)


Index("uq_users_username_lower", func.lower(UserOrm.username), unique=True)
