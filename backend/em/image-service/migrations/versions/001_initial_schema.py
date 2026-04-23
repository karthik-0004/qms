"""Initial schema — plate_images.

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
        "plate_images",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("plate_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("image_key", sa.String(500), nullable=False),
        sa.Column("image_type", sa.String(50), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("width_px", sa.Integer(), nullable=True),
        sa.Column("height_px", sa.Integer(), nullable=True),
        sa.Column("resolution_dpi", sa.Integer(), nullable=True),
        sa.Column("magnification", sa.Numeric(8, 2), nullable=True),
        sa.Column("camera_settings", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("status", sa.String(50), nullable=False, server_default="uploaded"),
        sa.Column("processing_notes", sa.Text(), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_plate_images_plate", "plate_images", ["plate_id"])
    op.create_index("idx_plate_images_tenant_status", "plate_images", ["tenant_id", "status"])


def downgrade() -> None:
    op.drop_index("idx_plate_images_tenant_status", table_name="plate_images")
    op.drop_index("idx_plate_images_plate", table_name="plate_images")
    op.drop_table("plate_images")
