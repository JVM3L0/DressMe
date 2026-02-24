from sqlalchemy import UUID, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
import uuid
import pendulum


class SQLUUIDMixin:
    uid: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )


class SQLLifeCycleMixin:
    created_at: Mapped[pendulum.DateTime] = mapped_column(
        DateTime(timezone=True),
        default=pendulum.now,
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    updated_at: Mapped[pendulum.DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=pendulum.now,
        server_default=func.now(),
        index=True,
    )
