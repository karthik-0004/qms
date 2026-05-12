"""Add company_id to platform_users; add bootstrap endpoints for company roles.

Revision ID: 002_add_company_id
Revises: 001_initial_master_schema
Create Date: 2026-05-11
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002_add_company_id"
down_revision = "001_initial_master_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "platform_users",
        sa.Column("company_id", postgresql.UUID(as_uuid=False), nullable=True),
    )
    op.create_index("idx_platform_users_company", "platform_users", ["company_id"])


def downgrade() -> None:
    op.drop_index("idx_platform_users_company", table_name="platform_users")
    op.drop_column("platform_users", "company_id")
