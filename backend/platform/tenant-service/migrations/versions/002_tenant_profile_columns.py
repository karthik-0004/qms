"""Add tenant profile JSONB and primary contact columns.

Revision ID: 002_tenant_profile_columns
Revises: 001_initial_schema
Create Date: 2026-05-11
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002_tenant_profile_columns"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tenants",
        sa.Column(
            "company_profile",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.add_column(
        "tenants",
        sa.Column(
            "billing_profile",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.add_column("tenants", sa.Column("primary_contact_first_name", sa.String(100), nullable=True))
    op.add_column("tenants", sa.Column("primary_contact_last_name", sa.String(100), nullable=True))
    op.add_column("tenants", sa.Column("primary_contact_email", sa.String(255), nullable=True))
    op.add_column("tenants", sa.Column("primary_contact_phone", sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column("tenants", "primary_contact_phone")
    op.drop_column("tenants", "primary_contact_email")
    op.drop_column("tenants", "primary_contact_last_name")
    op.drop_column("tenants", "primary_contact_first_name")
    op.drop_column("tenants", "billing_profile")
    op.drop_column("tenants", "company_profile")
