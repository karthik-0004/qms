"""Unit tests — DocumentDomainService business logic."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from rainer_common.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError

from app.domain.services import DocumentDomainService
from app.infra.db.models import Document, DocumentVersion


def make_doc(**kwargs) -> Document:
    defaults = dict(
        id=str(uuid4()), tenant_id="tenant-1", doc_number="SOP-001",
        title="Standard Operating Procedure", doc_type="SOP",
        department="QA", description=None, status="draft",
        current_version="1.0", owner_id=str(uuid4()), approver_id=None,
        effective_date=None, review_date=None, expiry_date=None,
        workflow_instance_id=None, file_id=None, tags=[], regulatory_frameworks=[],
        is_controlled=True, created_by=str(uuid4()), deleted_at=None,
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    d = MagicMock(spec=Document)
    for k, v in defaults.items():
        setattr(d, k, v)
    return d


@pytest.fixture
def doc_repo():
    return AsyncMock()


@pytest.fixture
def version_repo():
    return AsyncMock()


@pytest.fixture
def svc(doc_repo, version_repo):
    return DocumentDomainService(doc_repo=doc_repo, version_repo=version_repo, tenant_id="tenant-1")


class TestCreateDocument:
    @pytest.mark.asyncio
    async def test_creates_new_document(self, svc, doc_repo, version_repo):
        doc_repo.get_by_number.return_value = None
        mock_doc = make_doc()
        doc_repo.create.return_value = mock_doc
        version_repo.create.return_value = MagicMock()

        result = await svc.create_document(
            doc_number="SOP-001", title="Test SOP",
            doc_type="SOP", created_by=str(uuid4())
        )
        assert result is mock_doc
        doc_repo.create.assert_called_once()
        version_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_conflict_if_number_exists(self, svc, doc_repo):
        doc_repo.get_by_number.return_value = make_doc()
        with pytest.raises(ConflictError, match="already exists"):
            await svc.create_document("SOP-001", "Test", "SOP", str(uuid4()))


class TestGetDocument:
    @pytest.mark.asyncio
    async def test_returns_document(self, svc, doc_repo):
        doc = make_doc()
        doc_repo.get_by_id.return_value = doc
        result = await svc.get_document(doc.id)
        assert result is doc

    @pytest.mark.asyncio
    async def test_raises_not_found(self, svc, doc_repo):
        doc_repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            await svc.get_document("nonexistent")

    @pytest.mark.asyncio
    async def test_raises_forbidden_for_wrong_tenant(self, svc, doc_repo):
        doc = make_doc(tenant_id="other-tenant")
        doc_repo.get_by_id.return_value = doc
        with pytest.raises(ForbiddenError):
            await svc.get_document(doc.id)


class TestDocumentTransitions:
    @pytest.mark.asyncio
    async def test_submit_for_review_from_draft(self, svc, doc_repo):
        doc = make_doc(status="draft")
        doc_repo.get_by_id.return_value = doc
        doc_repo.update.return_value = None
        # After update, return under_review doc
        reviewed_doc = make_doc(status="under_review")
        doc_repo.get_by_id.side_effect = [doc, reviewed_doc]
        
        result = await svc.submit_for_review(doc.id, submitted_by=str(uuid4()))
        doc_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_cannot_submit_approved_for_review(self, svc, doc_repo):
        doc = make_doc(status="approved")
        doc_repo.get_by_id.return_value = doc
        with pytest.raises(ValidationError, match="not allowed"):
            await svc.submit_for_review(doc.id, submitted_by=str(uuid4()))

    @pytest.mark.asyncio
    async def test_approve_requires_signature(self, svc, doc_repo):
        doc = make_doc(status="under_review")
        doc_repo.get_by_id.return_value = doc
        with pytest.raises(ValidationError, match="E-signature"):
            await svc.approve_document(doc.id, approved_by=str(uuid4()), signature="")

    @pytest.mark.asyncio
    async def test_approve_document_success(self, svc, doc_repo, version_repo):
        doc = make_doc(status="under_review")
        doc_repo.get_by_id.return_value = doc
        doc_repo.update.return_value = None
        version_repo.list_by_document.return_value = []
        approved_doc = make_doc(status="approved")
        doc_repo.get_by_id.side_effect = [doc, approved_doc]

        result = await svc.approve_document(
            doc.id, approved_by=str(uuid4()), signature="my-signature-passphrase"
        )
        doc_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_cannot_delete_approved_document(self, svc, doc_repo):
        doc = make_doc(status="approved")
        doc_repo.get_by_id.return_value = doc
        with pytest.raises(ForbiddenError):
            await svc.delete_document(doc.id, deleted_by=str(uuid4()))

    @pytest.mark.asyncio
    async def test_make_obsolete_from_approved(self, svc, doc_repo):
        doc = make_doc(status="approved")
        doc_repo.get_by_id.return_value = doc
        doc_repo.update.return_value = None
        obsolete_doc = make_doc(status="obsolete")
        doc_repo.get_by_id.side_effect = [doc, obsolete_doc]

        result = await svc.make_obsolete(doc.id, updated_by=str(uuid4()))
        doc_repo.update.assert_called_with(doc.id, status="obsolete")
