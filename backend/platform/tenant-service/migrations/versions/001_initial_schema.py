"""Initial schema — tenants, tenant_settings.

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
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("db_name", sa.String(100), nullable=False),
        sa.Column("db_user", sa.String(100), nullable=False),
        sa.Column("db_host", sa.String(255), nullable=False, server_default="postgres"),
        sa.Column("db_port", sa.Integer(), nullable=False, server_default="5432"),
        sa.Column("status", sa.String(20), nullable=False, server_default="provisioning"),
        sa.Column("tier", sa.String(20), nullable=False, server_default="starter"),
        sa.Column("products", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("region", sa.String(50), nullable=False, server_default="us-east-1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_name"),
        sa.UniqueConstraint("slug"),
        sa.UniqueConstraint("db_name"),
        sa.UniqueConstraint("db_user"),
    )

    op.create_table(
        "tenant_settings",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("max_users", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("max_storage_gb", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("features", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("branding", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("smtp_config", postgresql.JSONB(), nullable=True),
        sa.Column("webhook_urls", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("timezone", sa.String(100), nullable=False, server_default="UTC"),
        sa.Column("locale", sa.String(20), nullable=False, server_default="en-US"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id"),
    )


def downgrade() -> None:
    op.drop_table("tenant_settings")
    op.drop_table("tenants")
