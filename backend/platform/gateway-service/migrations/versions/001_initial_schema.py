"""Initial schema — rate_limit_counters.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-03-06
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rate_limit_counters",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("key", sa.String(500), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_rate_limit_key_window", "rate_limit_counters", ["key", "window_start"], unique=True)


def downgrade() -> None:
    op.drop_index("idx_rate_limit_key_window", table_name="rate_limit_counters")
    op.drop_table("rate_limit_counters")
