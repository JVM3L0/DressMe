import uuid
from typing import Optional

import pendulum
from pydantic import AwareDatetime, Field


class UUIDMixin:
    uid: uuid.UUID = Field(default_factory=uuid.uuid4)


class LifeCycleMixin:
    created_at: AwareDatetime = Field(default_factory=lambda: pendulum.now("UTC"))
    updated_at: Optional[AwareDatetime] = None
