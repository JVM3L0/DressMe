"""garante email e username em minusculas

Revision ID: e08d8c40f2c0
Revises: 61b394fd8bf1
Create Date: 2026-10-19 19:02:17.106090

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e08d8c40f2c0"
down_revision: str | Sequence[str] | None = "61b394fd8bf1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Normaliza registros antigos. Se existirem duplicados que só diferem em
    # maiúsculas, o índice único faz a migração falhar e eles precisam ser
    # resolvidos manualmente antes.
    op.execute("UPDATE users SET email = lower(email), username = lower(username)")
    op.create_check_constraint("email_lowercase", "users", "email = lower(email)")
    op.create_check_constraint(
        "username_lowercase", "users", "username = lower(username)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f("ck_users_username_lowercase"), "users", type_="check")
    op.drop_constraint(op.f("ck_users_email_lowercase"), "users", type_="check")
