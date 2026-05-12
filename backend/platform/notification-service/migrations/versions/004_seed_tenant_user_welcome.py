"""Seed tenant_user_welcome email template.

Revision ID: 004_seed_tenant_user_welcome
Revises: 003_seed_company_templates
Create Date: 2026-05-12
"""

import os
import time
import uuid as _uuid_mod
from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op

revision = "004_seed_tenant_user_welcome"
down_revision = "003_seed_company_templates"
branch_labels = None
depends_on = None


def _uuid7() -> str:
    ts_ms = int(time.time() * 1000) & 0xFFFF_FFFF_FFFF
    rand = int.from_bytes(os.urandom(10), "big")
    upper = (ts_ms << 16) | (0x7 << 12) | ((rand >> 68) & 0xFFF)
    lower = 0x8000_0000_0000_0000 | (rand & 0x3FFF_FFFF_FFFF_FFFF)
    return str(_uuid_mod.UUID(int=(upper << 64) | lower))


_SUBJECT = "Welcome — your account is ready"

_HTML = """\
<html><body>
<p>Hello {{first_name}} {{last_name}},</p>
<p>An account has been created for you on the platform.</p>
<ul>
  <li><strong>Your email:</strong> {{email}}</li>
  <li><strong>Temporary password:</strong> <code>{{temporary_password}}</code></li>
  <li><strong>Login URL:</strong> <a href="{{login_url}}">{{login_url}}</a></li>
</ul>
<p>Please sign in and change your password after first login.</p>
</body></html>"""

_TEXT = """\
Hello {{first_name}} {{last_name}},

An account has been created for you on the platform.

Email: {{email}}
Temporary password: {{temporary_password}}
Login: {{login_url}}

Please sign in and change your password after first login.
"""

_VARS = ["first_name", "last_name", "email", "temporary_password", "login_url"]


def upgrade() -> None:
    import json

    conn = op.get_bind()
    exists = conn.execute(
        sa.text("SELECT 1 FROM notification_templates WHERE name = :n"),
        {"n": "tenant_user_welcome"},
    ).scalar()
    if exists:
        return

    now = datetime.now(timezone.utc)
    conn.execute(
        sa.text("""
            INSERT INTO notification_templates
                (id, name, subject, body_html, body_text, channel,
                 variables, is_active, created_at, updated_at)
            VALUES
                (:id, :name, :subject, :body_html, :body_text, 'email',
                 CAST(:vars AS JSONB), true, :created_at, :updated_at)
        """),
        {
            "id": _uuid7(),
            "name": "tenant_user_welcome",
            "subject": _SUBJECT,
            "body_html": _HTML,
            "body_text": _TEXT,
            "vars": json.dumps(_VARS),
            "created_at": now,
            "updated_at": now,
        },
    )


def downgrade() -> None:
    op.execute(
        sa.text("DELETE FROM notification_templates WHERE name = 'tenant_user_welcome'")
    )
