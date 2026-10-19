"""remove server default de updated_at

Revision ID: afa8286abd67
Revises: e08d8c40f2c0
Create Date: 2026-10-19 18:48:08.561207

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "afa8286abd67"
down_revision: str | Sequence[str] | None = "e08d8c40f2c0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("users", "updated_at", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("users", "updated_at", server_default=sa.text("now()"))
