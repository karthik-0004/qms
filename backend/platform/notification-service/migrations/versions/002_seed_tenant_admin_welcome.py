"""Seed tenant_admin_welcome email template.

Revision ID: 002_seed_tenant_admin_welcome
Revises: 001_initial_schema
Create Date: 2026-05-11
"""

import os
import time
import uuid as _uuid_mod
from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op


def _uuid7() -> str:
    ts_ms = int(time.time() * 1000) & 0xFFFF_FFFF_FFFF
    rand = int.from_bytes(os.urandom(10), "big")
    upper = (ts_ms << 16) | (0x7 << 12) | ((rand >> 68) & 0xFFF)
    lower = 0x8000_0000_0000_0000 | (rand & 0x3FFF_FFFF_FFFF_FFFF)
    return str(_uuid_mod.UUID(int=(upper << 64) | lower))
revision = "002_seed_tenant_admin_welcome"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    exists = conn.execute(
        sa.text("SELECT 1 FROM notification_templates WHERE name = :n"),
        {"n": "tenant_admin_welcome"},
    ).scalar()
    if exists:
        return

    now = datetime.now(timezone.utc)
    tid = _uuid7()
    subject = "Welcome — your {{tenant_name}} workspace"
    html = """<html><body>
<p>Hello {{admin_first_name}} {{admin_last_name}},</p>
<p>Your company workspace <strong>{{tenant_name}}</strong> has been created.</p>
<ul>
<li><strong>Tenant slug:</strong> {{slug}}</li>
<li><strong>Login URL:</strong> <a href="{{login_url}}">{{login_url}}</a></li>
<li><strong>Email:</strong> {{admin_email}}</li>
<li><strong>Temporary password:</strong> {{temporary_password}}</li>
<li><strong>Tier:</strong> {{tier}} &mdash; <strong>Region:</strong> {{region}}</li>
<li><strong>Products:</strong> {{products}}</li>
</ul>
<pre style="white-space:pre-wrap;">{{address_summary}}</pre>
<p>Please sign in and change your password after first login.</p>
</body></html>"""
    text_body = """Hello {{admin_first_name}} {{admin_last_name}},

Your workspace {{tenant_name}} is ready.

Login: {{login_url}}
Email: {{admin_email}}
Temporary password: {{temporary_password}}

Tenant slug: {{slug}}
Tier: {{tier}}, Region: {{region}}
Products: {{products}}

{{address_summary}}
"""

    conn.execute(
        sa.text("""
            INSERT INTO notification_templates
            (id, name, subject, body_html, body_text, channel, variables, is_active, created_at, updated_at)
            VALUES
            (:id, :name, :subject, :body_html, :body_text, 'email',
             CAST(:vars AS JSONB), true, :created_at, :updated_at)
        """),
        {
            "id": tid,
            "name": "tenant_admin_welcome",
            "subject": subject,
            "body_html": html,
            "body_text": text_body,
            "vars": '["tenant_name","slug","login_url","admin_email","temporary_password","admin_first_name","admin_last_name","tier","region","products","address_summary"]',
            "created_at": now,
            "updated_at": now,
        },
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM notification_templates WHERE name = 'tenant_admin_welcome'"))
