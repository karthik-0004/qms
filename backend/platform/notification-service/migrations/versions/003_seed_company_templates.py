"""Seed company_admin_welcome and company_user_welcome email templates.

Revision ID: 003_seed_company_templates
Revises: 002_seed_tenant_admin_welcome
Create Date: 2026-05-12
"""

import os
import time
import uuid as _uuid_mod
from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op

revision = "003_seed_company_templates"
down_revision = "002_seed_tenant_admin_welcome"
branch_labels = None
depends_on = None


def _uuid7() -> str:
    ts_ms = int(time.time() * 1000) & 0xFFFF_FFFF_FFFF
    rand = int.from_bytes(os.urandom(10), "big")
    upper = (ts_ms << 16) | (0x7 << 12) | ((rand >> 68) & 0xFFF)
    lower = 0x8000_0000_0000_0000 | (rand & 0x3FFF_FFFF_FFFF_FFFF)
    return str(_uuid_mod.UUID(int=(upper << 64) | lower))


# ── Template definitions ──────────────────────────────────────────────────────

_COMPANY_ADMIN_SUBJECT = "Welcome — you are now admin of {{company_name}}"

_COMPANY_ADMIN_HTML = """\
<html><body>
<p>Hello {{admin_first_name}} {{admin_last_name}},</p>
<p>A new company <strong>{{company_name}}</strong> has been created and you have been
assigned as its administrator.</p>
<ul>
  <li><strong>Company code:</strong> {{company_code}}</li>
  <li><strong>Your email:</strong> {{admin_email}}</li>
  <li><strong>Temporary password:</strong> <code>{{temporary_password}}</code></li>
  <li><strong>Login URL:</strong> <a href="{{login_url}}">{{login_url}}</a></li>
</ul>
<p>Please sign in and change your password after first login.</p>
</body></html>"""

_COMPANY_ADMIN_TEXT = """\
Hello {{admin_first_name}} {{admin_last_name}},

A new company {{company_name}} (code: {{company_code}}) has been created.
You have been assigned as company administrator.

Email: {{admin_email}}
Temporary password: {{temporary_password}}
Login: {{login_url}}

Please sign in and change your password after first login.
"""

_COMPANY_ADMIN_VARS = [
    "company_name",
    "company_code",
    "admin_first_name",
    "admin_last_name",
    "admin_email",
    "temporary_password",
    "login_url",
]

# ─────────────────────────────────────────────────────────────────────────────

_COMPANY_USER_SUBJECT = "Welcome to {{company_name}} — your account is ready"

_COMPANY_USER_HTML = """\
<html><body>
<p>Hello {{first_name}} {{last_name}},</p>
<p>An account has been created for you in the company
<strong>{{company_name}}</strong>.</p>
<ul>
  <li><strong>Your email:</strong> {{email}}</li>
  <li><strong>Temporary password:</strong> <code>{{temporary_password}}</code></li>
  <li><strong>Login URL:</strong> <a href="{{login_url}}">{{login_url}}</a></li>
</ul>
<p>Please sign in and change your password after first login.</p>
</body></html>"""

_COMPANY_USER_TEXT = """\
Hello {{first_name}} {{last_name}},

An account has been created for you in {{company_name}}.

Email: {{email}}
Temporary password: {{temporary_password}}
Login: {{login_url}}

Please sign in and change your password after first login.
"""

_COMPANY_USER_VARS = [
    "company_name",
    "first_name",
    "last_name",
    "email",
    "temporary_password",
    "login_url",
]

# ─────────────────────────────────────────────────────────────────────────────

_TEMPLATES = [
    {
        "name": "company_admin_welcome",
        "subject": _COMPANY_ADMIN_SUBJECT,
        "body_html": _COMPANY_ADMIN_HTML,
        "body_text": _COMPANY_ADMIN_TEXT,
        "vars": _COMPANY_ADMIN_VARS,
    },
    {
        "name": "company_user_welcome",
        "subject": _COMPANY_USER_SUBJECT,
        "body_html": _COMPANY_USER_HTML,
        "body_text": _COMPANY_USER_TEXT,
        "vars": _COMPANY_USER_VARS,
    },
]


def upgrade() -> None:
    import json

    conn = op.get_bind()
    now = datetime.now(timezone.utc)

    for tpl in _TEMPLATES:
        exists = conn.execute(
            sa.text("SELECT 1 FROM notification_templates WHERE name = :n"),
            {"n": tpl["name"]},
        ).scalar()
        if exists:
            continue
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
                "name": tpl["name"],
                "subject": tpl["subject"],
                "body_html": tpl["body_html"],
                "body_text": tpl["body_text"],
                "vars": json.dumps(tpl["vars"]),
                "created_at": now,
                "updated_at": now,
            },
        )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM notification_templates"
            " WHERE name IN ('company_admin_welcome', 'company_user_welcome')"
        )
    )
