"""preserva grafia do username com unicidade case-insensitive

Revision ID: 20504914f2f0
Revises: afa8286abd67
Create Date: 2026-10-19 19:16:52.792024

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20504914f2f0"
down_revision: str | Sequence[str] | None = "afa8286abd67"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Unicidade do username passa a ser por lower(username), o que permite
    # preservar a grafia original
    op.drop_constraint(op.f("ck_users_username_lowercase"), "users", type_="check")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.create_index(
        "uq_users_username_lower",
        "users",
        [sa.literal_column("lower(username)")],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("uq_users_username_lower", table_name="users")
    op.execute("UPDATE users SET username = lower(username)")
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_check_constraint(
        "username_lowercase", "users", "username = lower(username)"
    )
