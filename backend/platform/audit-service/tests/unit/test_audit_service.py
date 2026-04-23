"""Unit tests — AuditDomainService business logic."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from rainer_common.exceptions import NotFoundError

from app.domain.services import AuditDomainService
from app.infra.db.models import PlatformAuditLog


def make_log(**kwargs) -> PlatformAuditLog:
    defaults = dict(
        id=str(uuid4()),
        tenant_id=str(uuid4()),
        user_id=str(uuid4()),
        action="USER_LOGIN",
        resource_type="user",
        resource_id=str(uuid4()),
        ip_address="127.0.0.1",
        user_agent="test-agent",
        metadata_={},
        severity="info",
        source_service="auth-service",
        event_id=str(uuid4()),
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    log = MagicMock(spec=PlatformAuditLog)
    for k, v in defaults.items():
        setattr(log, k, v)
    return log


@pytest.fixture
def repo():
    return AsyncMock()


@pytest.fixture
def svc(repo):
    return AuditDomainService(repo=repo)


class TestAppendLog:
    @pytest.mark.asyncio
    async def test_appends_log_successfully(self, svc, repo):
        mock_log = make_log()
        repo.append.return_value = mock_log
        result = await svc.append(action="USER_LOGIN", tenant_id=str(uuid4()))
        assert result is mock_log
        repo.append.assert_called_once()

    @pytest.mark.asyncio
    async def test_append_with_all_fields(self, svc, repo):
        mock_log = make_log(action="DOCUMENT_APPROVED", severity="warning")
        repo.append.return_value = mock_log
        result = await svc.append(
            action="DOCUMENT_APPROVED",
            tenant_id=str(uuid4()),
            user_id=str(uuid4()),
            resource_type="document",
            resource_id=str(uuid4()),
            severity="warning",
            source_service="document-service",
        )
        assert result.action == "DOCUMENT_APPROVED"
        assert result.severity == "warning"


class TestQueryLogs:
    @pytest.mark.asyncio
    async def test_returns_paginated_logs(self, svc, repo):
        mock_logs = [make_log() for _ in range(5)]
        repo.query.return_value = (mock_logs, 50)
        logs, total = await svc.query_logs(page=1, page_size=5)
        assert len(logs) == 5
        assert total == 50

    @pytest.mark.asyncio
    async def test_restricts_to_tenant(self, svc, repo):
        tenant_id = str(uuid4())
        repo.query.return_value = ([], 0)
        await svc.query_logs(tenant_id=tenant_id)
        repo.query.assert_called_once()
        call_kwargs = repo.query.call_args.kwargs
        assert call_kwargs.get("tenant_id") == tenant_id


class TestGetLog:
    @pytest.mark.asyncio
    async def test_returns_log_by_id(self, svc, repo):
        mock_log = make_log()
        repo.get_by_id.return_value = mock_log
        result = await svc.get_log(mock_log.id)
        assert result is mock_log

    @pytest.mark.asyncio
    async def test_raises_not_found(self, svc, repo):
        repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            await svc.get_log("nonexistent-id")


class TestProcessKafkaEvent:
    @pytest.mark.asyncio
    async def test_processes_kafka_event(self, svc, repo):
        repo.append.return_value = make_log()
        event = {
            "event_id": str(uuid4()),
            "event_type": "document.document.approved",
            "tenant_id": str(uuid4()),
            "actor_id": str(uuid4()),
            "payload": {"document_id": str(uuid4())},
            "source_service": "document-service",
        }
        await svc.process_kafka_event(event)
        repo.append.assert_called_once()
        call_kwargs = repo.append.call_args.kwargs
        assert call_kwargs["action"] == "document.document.approved"
