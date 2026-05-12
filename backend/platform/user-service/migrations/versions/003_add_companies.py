"""Add companies table; add company_id to users; add scope + company_id to roles.

Revision ID: 003_add_companies
Revises: 002_seed_system_roles
Create Date: 2026-05-11
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "003_add_companies"
down_revision = "002_seed_system_roles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. companies table ───────────────────────────────────────────────
    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("company_code", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("admin_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("employee_limit", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("company_code"),
    )
    op.create_index("idx_companies_tenant", "companies", ["tenant_id"])
    op.create_index("idx_companies_email", "companies", ["email"])

    # ── 2. users — add company_id FK ─────────────────────────────────────
    op.add_column("users", sa.Column("company_id", postgresql.UUID(as_uuid=False), nullable=True))
    op.create_foreign_key(
        "fk_users_company_id",
        "users", "companies",
        ["company_id"], ["id"],
        ondelete="SET NULL",
    )
    op.create_index("idx_users_company", "users", ["company_id"])

    # ── 3. roles — add scope + company_id ────────────────────────────────
    op.add_column("roles", sa.Column("scope", sa.String(20), nullable=False, server_default="tenant"))
    op.add_column("roles", sa.Column("company_id", postgresql.UUID(as_uuid=False), nullable=True))
    op.create_foreign_key(
        "fk_roles_company_id",
        "roles", "companies",
        ["company_id"], ["id"],
        ondelete="CASCADE",
    )
    op.create_index("idx_roles_scope_company", "roles", ["scope", "company_id"])

    # Drop the global UNIQUE(name) constraint and replace with scoped indexes
    op.drop_constraint("roles_name_key", "roles", type_="unique")
    # Tenant-level roles: unique name where company_id IS NULL
    op.execute(
        "CREATE UNIQUE INDEX idx_roles_name_tenant ON roles (name) WHERE company_id IS NULL"
    )
    # Company-level roles: unique (company_id, name) pair
    op.execute(
        "CREATE UNIQUE INDEX idx_roles_name_company ON roles (company_id, name) WHERE company_id IS NOT NULL"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_roles_name_company")
    op.execute("DROP INDEX IF EXISTS idx_roles_name_tenant")
    op.create_unique_constraint("roles_name_key", "roles", ["name"])
    op.drop_index("idx_roles_scope_company", table_name="roles")
    op.drop_constraint("fk_roles_company_id", "roles", type_="foreignkey")
    op.drop_column("roles", "company_id")
    op.drop_column("roles", "scope")
    op.drop_index("idx_users_company", table_name="users")
    op.drop_constraint("fk_users_company_id", "users", type_="foreignkey")
    op.drop_column("users", "company_id")
    op.drop_index("idx_companies_email", table_name="companies")
    op.drop_index("idx_companies_tenant", table_name="companies")
    op.drop_table("companies")
