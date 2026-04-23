"""Unit tests — NotificationDomainService business logic."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from rainer_common.exceptions import NotFoundError

from app.core.config import Settings
from app.domain.services import NotificationDomainService, _render_template
from app.infra.db.models import NotificationLog, NotificationTemplate


def make_settings() -> Settings:
    return Settings(
        rainer_env="testing",
        database_url="sqlite+aiosqlite:///:memory:",
        smtp_host="localhost",
        smtp_port=1025,
        smtp_use_tls=False,
        smtp_from_email="test@rainer.io",
        smtp_from_name="Test",
    )


@pytest.fixture
def template_repo():
    return AsyncMock()


@pytest.fixture
def log_repo():
    return AsyncMock()


@pytest.fixture
def svc(template_repo, log_repo):
    return NotificationDomainService(
        template_repo=template_repo,
        log_repo=log_repo,
        settings=make_settings(),
    )


class TestRenderTemplate:
    def test_replaces_variables(self):
        template = "Hello {{name}}, your code is {{code}}"
        result = _render_template(template, {"name": "Alice", "code": "1234"})
        assert result == "Hello Alice, your code is 1234"

    def test_missing_variable_left_as_is(self):
        template = "Hello {{name}}"
        result = _render_template(template, {})
        assert result == "Hello {{name}}"

    def test_empty_template(self):
        assert _render_template("", {}) == ""


class TestSendEmail:
    @pytest.mark.asyncio
    async def test_sends_email_successfully(self, svc, template_repo, log_repo):
        mock_log = MagicMock(spec=NotificationLog)
        mock_log.id = "log-id"
        log_repo.create.return_value = mock_log

        with patch("app.domain.services.aiosmtplib.send", new=AsyncMock()):
            result = await svc.send_email(
                recipient_email="user@example.com",
                subject="Test Subject",
                body_html="<p>Hello</p>",
            )

        log_repo.create.assert_called_once()
        log_repo.mark_sent.assert_called_once_with("log-id")
        assert result is mock_log

    @pytest.mark.asyncio
    async def test_marks_failed_on_smtp_error(self, svc, log_repo):
        mock_log = MagicMock(spec=NotificationLog)
        mock_log.id = "log-id"
        log_repo.create.return_value = mock_log

        with patch("app.domain.services.aiosmtplib.send", new=AsyncMock(side_effect=Exception("SMTP error"))):
            await svc.send_email(
                recipient_email="user@example.com",
                subject="Test",
                body_html="<p>Hello</p>",
            )

        log_repo.mark_failed.assert_called_once()


class TestSendFromTemplate:
    @pytest.mark.asyncio
    async def test_sends_from_valid_template(self, svc, template_repo, log_repo):
        template = MagicMock(spec=NotificationTemplate)
        template.subject = "Hello {{name}}"
        template.body_html = "<p>Welcome {{name}}</p>"
        template.body_text = None
        template_repo.get_by_name.return_value = template
        mock_log = MagicMock(spec=NotificationLog)
        mock_log.id = "log-id"
        log_repo.create.return_value = mock_log

        with patch("app.domain.services.aiosmtplib.send", new=AsyncMock()):
            result = await svc.send_from_template(
                template_name="welcome",
                recipient_email="user@example.com",
                variables={"name": "Alice"},
            )
        assert result is mock_log

    @pytest.mark.asyncio
    async def test_raises_if_template_not_found(self, svc, template_repo):
        template_repo.get_by_name.return_value = None
        with pytest.raises(NotFoundError):
            await svc.send_from_template("missing-template", "user@example.com", {})
