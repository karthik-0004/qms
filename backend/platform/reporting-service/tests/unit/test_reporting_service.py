"""Unit tests — ReportingDomainService business logic."""

import pytest

from app.domain.services import ReportingDomainService


@pytest.fixture
def svc():
    return ReportingDomainService()


class TestGenerateReport:
    @pytest.mark.asyncio
    async def test_returns_job_id(self, svc):
        result = await svc.generate_report(
            template_key="audit_trail",
            data={"tenant_id": "t1"},
            format="pdf",
        )
        assert "job_id" in result
        assert result["status"] == "queued"
        assert result["template_key"] == "audit_trail"

    @pytest.mark.asyncio
    async def test_generates_unique_job_ids(self, svc):
        r1 = await svc.generate_report("audit_trail", {})
        r2 = await svc.generate_report("audit_trail", {})
        assert r1["job_id"] != r2["job_id"]


class TestListTemplates:
    @pytest.mark.asyncio
    async def test_returns_template_list(self, svc):
        templates = await svc.list_templates()
        assert len(templates) > 0
        keys = {t["key"] for t in templates}
        assert "audit_trail" in keys
        assert "document_register" in keys
        assert "certificate" in keys


class TestGetJobStatus:
    @pytest.mark.asyncio
    async def test_returns_status(self, svc):
        status = await svc.get_job_status("some-job-id")
        assert "job_id" in status
        assert "status" in status
