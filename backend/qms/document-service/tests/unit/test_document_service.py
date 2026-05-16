"""Unit tests — DocumentDomainService business logic."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from rainer_common.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError

from app.domain.services import DocumentDomainService
from app.infra.db.models import Document, DocumentAcknowledgment, DocumentVersion


def make_doc(**kwargs) -> Document:
    defaults = dict(
        id=str(uuid4()), tenant_id="tenant-1", doc_number="SOP-001",
        title="Standard Operating Procedure", doc_type="SOP",
        department="QA", description=None, status="draft",
        current_version="1.0", owner_id=str(uuid4()), approver_id=None,
        effective_date=None, review_date=None, expiry_date=None,
        workflow_instance_id=None, file_id=None, tags=[], regulatory_frameworks=[],
        is_controlled=True, last_rejection_reason=None,
        authoring_mode="upload", content_ast=None, html_snapshot=None, editor_nonce=None,
        created_by=str(uuid4()), deleted_at=None,
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
def distribution_repo():
    return AsyncMock()


@pytest.fixture
def ack_repo():
    return AsyncMock()


@pytest.fixture
def svc(doc_repo, version_repo, distribution_repo, ack_repo):
    return DocumentDomainService(
        doc_repo=doc_repo,
        version_repo=version_repo,
        distribution_repo=distribution_repo,
        ack_repo=ack_repo,
        tenant_id="tenant-1",
    )


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

    @pytest.mark.asyncio
    async def test_reject_persists_rejection_reason(self, svc, doc_repo):
        """D-1 fix: reject writes last_rejection_reason and subsequent read returns it."""
        doc = make_doc(status="under_review")
        doc_repo.get_by_id.return_value = doc
        doc_repo.update.return_value = None
        rejected_doc = make_doc(status="draft", last_rejection_reason="Missing required section 4.2")
        doc_repo.get_by_id.side_effect = [doc, rejected_doc]

        result = await svc.reject_document(doc.id, rejected_by=str(uuid4()), reason="Missing required section 4.2")

        doc_repo.update.assert_called_once()
        call_kwargs = doc_repo.update.call_args[1]
        assert call_kwargs["last_rejection_reason"] == "Missing required section 4.2"
        assert result.last_rejection_reason == "Missing required section 4.2"

    @pytest.mark.asyncio
    async def test_submit_for_review_clears_rejection_reason(self, svc, doc_repo):
        """After rejection, resubmitting clears last_rejection_reason."""
        doc = make_doc(status="draft", last_rejection_reason="Previous rejection reason")
        doc_repo.get_by_id.return_value = doc
        doc_repo.update.return_value = None
        submitted_doc = make_doc(status="under_review", last_rejection_reason=None)
        doc_repo.get_by_id.side_effect = [doc, submitted_doc]

        result = await svc.submit_for_review(doc.id, submitted_by=str(uuid4()))

        doc_repo.update.assert_called_once()
        call_kwargs = doc_repo.update.call_args[1]
        assert call_kwargs["last_rejection_reason"] is None

    # ── D-4: EFFECTIVE / SUPERSEDED state machine ──────────────────────

    @pytest.mark.asyncio
    async def test_make_effective_from_approved(self, svc, doc_repo):
        doc = make_doc(status="approved")
        doc_repo.get_by_id.return_value = doc
        doc_repo.update.return_value = None
        effective_doc = make_doc(status="effective")
        doc_repo.get_by_id.side_effect = [doc, effective_doc]

        result = await svc.make_effective(doc.id, updated_by=str(uuid4()))
        doc_repo.update.assert_called_with(doc.id, status="effective")
        assert result.status == "effective"

    @pytest.mark.asyncio
    async def test_make_superseded_from_effective(self, svc, doc_repo):
        doc = make_doc(status="effective")
        doc_repo.get_by_id.return_value = doc
        doc_repo.update.return_value = None
        superseded_doc = make_doc(status="superseded")
        doc_repo.get_by_id.side_effect = [doc, superseded_doc]

        result = await svc.make_superseded(doc.id, updated_by=str(uuid4()))
        doc_repo.update.assert_called_with(doc.id, status="superseded")
        assert result.status == "superseded"

    @pytest.mark.asyncio
    async def test_cannot_make_effective_from_draft(self, svc, doc_repo):
        doc = make_doc(status="draft")
        doc_repo.get_by_id.return_value = doc
        with pytest.raises(ValidationError, match="not allowed"):
            await svc.make_effective(doc.id, updated_by=str(uuid4()))

    @pytest.mark.asyncio
    async def test_cannot_make_superseded_from_approved(self, svc, doc_repo):
        doc = make_doc(status="approved")
        doc_repo.get_by_id.return_value = doc
        with pytest.raises(ValidationError, match="not allowed"):
            await svc.make_superseded(doc.id, updated_by=str(uuid4()))

    @pytest.mark.asyncio
    async def test_make_obsolete_from_effective(self, svc, doc_repo):
        doc = make_doc(status="effective")
        doc_repo.get_by_id.return_value = doc
        doc_repo.update.return_value = None
        doc_repo.get_by_id.side_effect = [doc, make_doc(status="obsolete")]

        result = await svc.make_obsolete(doc.id, updated_by=str(uuid4()))
        doc_repo.update.assert_called_with(doc.id, status="obsolete")

    @pytest.mark.asyncio
    async def test_make_obsolete_from_superseded(self, svc, doc_repo):
        doc = make_doc(status="superseded")
        doc_repo.get_by_id.return_value = doc
        doc_repo.update.return_value = None
        doc_repo.get_by_id.side_effect = [doc, make_doc(status="obsolete")]

        result = await svc.make_obsolete(doc.id, updated_by=str(uuid4()))
        doc_repo.update.assert_called_with(doc.id, status="obsolete")

    @pytest.mark.asyncio
    async def test_cannot_delete_effective_document(self, svc, doc_repo):
        doc = make_doc(status="effective")
        doc_repo.get_by_id.return_value = doc
        with pytest.raises(ForbiddenError):
            await svc.delete_document(doc.id, deleted_by=str(uuid4()))

    @pytest.mark.asyncio
    async def test_cannot_submit_effective_for_review(self, svc, doc_repo):
        doc = make_doc(status="effective")
        doc_repo.get_by_id.return_value = doc
        with pytest.raises(ValidationError, match="not allowed"):
            await svc.submit_for_review(doc.id, submitted_by=str(uuid4()))


class TestAcknowledgment:
    @pytest.mark.asyncio
    async def test_acknowledge_document_success(self, svc, doc_repo, ack_repo):
        doc = make_doc(status="effective", current_version="2.0")
        doc_repo.get_by_id.return_value = doc
        ack_repo.get_for_document_and_user.return_value = None
        mock_ack = MagicMock(spec=DocumentAcknowledgment)
        mock_ack.id = str(uuid4())
        mock_ack.document_id = doc.id
        mock_ack.user_id = str(uuid4())
        mock_ack.version = "2.0"
        mock_ack.signature_hash = "abc123"
        mock_ack.ip_address = "127.0.0.1"
        ack_repo.create.return_value = mock_ack

        result = await svc.acknowledge_document(
            doc.id, user_id=mock_ack.user_id, signature="my-esig"
        )
        ack_repo.create.assert_called_once()
        assert result.signature_hash is not None

    @pytest.mark.asyncio
    async def test_acknowledge_requires_effective_or_approved(self, svc, doc_repo):
        doc = make_doc(status="draft")
        doc_repo.get_by_id.return_value = doc
        with pytest.raises(ValidationError, match="effective or approved"):
            await svc.acknowledge_document(doc.id, user_id=str(uuid4()), signature="sig")

    @pytest.mark.asyncio
    async def test_cannot_acknowledge_twice(self, svc, doc_repo, ack_repo):
        doc = make_doc(status="effective")
        doc_repo.get_by_id.return_value = doc
        ack_repo.get_for_document_and_user.return_value = MagicMock()
        with pytest.raises(ConflictError, match="already acknowledged"):
            await svc.acknowledge_document(doc.id, user_id=str(uuid4()), signature="sig")

    @pytest.mark.asyncio
    async def test_list_acknowledgments(self, svc, doc_repo, ack_repo):
        doc = make_doc()
        doc_repo.get_by_id.return_value = doc
        mock_acks = [MagicMock(spec=DocumentAcknowledgment) for _ in range(3)]
        ack_repo.list_for_document.return_value = mock_acks

        result = await svc.list_acknowledgments(doc.id)
        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_get_my_pending_acknowledgments(self, svc, doc_repo, ack_repo, distribution_repo):
        user_id = str(uuid4())
        doc = make_doc(status="effective", doc_number="SOP-001", title="Test SOP")
        distribution_repo.list_for_user.return_value = [
            MagicMock(document_id=doc.id)
        ]
        doc_repo.get_by_id.return_value = doc
        ack_repo.get_for_document_and_user.return_value = None

        pending = await svc.get_my_pending_acknowledgments(user_id)
        assert len(pending) == 1
        assert pending[0]["doc_number"] == "SOP-001"

    @pytest.mark.asyncio
    async def test_create_new_version_from_approved_major(self, svc, doc_repo, version_repo):
        doc = make_doc(status="approved", current_version="1.0",
                       authoring_mode="embedded_editor", content_ast={"doc": {"type": "doc"}},
                       html_snapshot="<p>Hello</p>")
        doc_repo.get_by_id.return_value = doc
        doc_repo.update.return_value = None
        version_repo.list_by_document.return_value = [MagicMock(id=str(uuid4()))]
        version_repo.create.return_value = MagicMock()
        new_doc = make_doc(status="draft", current_version="2.0")
        doc_repo.get_by_id.side_effect = [doc, new_doc]

        result = await svc.create_new_version(
            doc.id, change_type="major", change_summary="Major update", created_by=str(uuid4())
        )
        version_repo.create.assert_called_once()
        # Should have been called with version=2.0
        call_kwargs = version_repo.create.call_args[1]
        assert call_kwargs["version"] == "2.0"
        assert result.current_version == "2.0"

    @pytest.mark.asyncio
    async def test_create_new_version_from_effective_minor(self, svc, doc_repo, version_repo):
        doc = make_doc(status="effective", current_version="2.0")
        doc_repo.get_by_id.return_value = doc
        doc_repo.update.return_value = None
        version_repo.list_by_document.return_value = [MagicMock(id=str(uuid4()))]
        version_repo.create.return_value = MagicMock()
        new_doc = make_doc(status="draft", current_version="2.1")
        doc_repo.get_by_id.side_effect = [doc, new_doc]

        result = await svc.create_new_version(
            doc.id, change_type="minor", change_summary="Minor tweak", created_by=str(uuid4())
        )
        call_kwargs = version_repo.create.call_args[1]
        assert call_kwargs["version"] == "2.1"

    @pytest.mark.asyncio
    async def test_cannot_create_new_version_from_draft(self, svc, doc_repo):
        doc = make_doc(status="draft")
        doc_repo.get_by_id.return_value = doc
        with pytest.raises(ValidationError, match="not allowed"):
            await svc.create_new_version(
                doc.id, change_type="major", change_summary="test", created_by=str(uuid4())
            )

    @pytest.mark.asyncio
    async def test_create_new_version_snapshots_content(self, svc, doc_repo, version_repo):
        """Verify that prior version's content_ast/html_snapshot are snapshotted."""
        doc = make_doc(status="approved", current_version="1.0",
                       authoring_mode="embedded_editor",
                       content_ast={"doc": {"type": "doc"}},
                       html_snapshot="<p>Original content</p>")
        doc_repo.get_by_id.return_value = doc
        doc_repo.update.return_value = None
        latest_version = MagicMock(spec=DocumentVersion, id=str(uuid4()))
        version_repo.list_by_document.return_value = [latest_version]
        version_repo.create.return_value = MagicMock()
        new_doc = make_doc(status="draft", current_version="2.0")
        doc_repo.get_by_id.side_effect = [doc, new_doc]

        await svc.create_new_version(
            doc.id, change_type="major", change_summary="v2", created_by=str(uuid4())
        )
        # Should have snapshotted content into the prior version row
        doc_repo._db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_compliance_stats(self, svc, doc_repo, ack_repo):
        doc = make_doc()
        doc_repo.get_by_id.return_value = doc
        ack_repo.get_compliance_stats.return_value = {
            "total_distribution": 10, "acknowledged": 7, "pending": 3, "compliance_pct": 70.0,
        }

        stats = await svc.get_acknowledgment_compliance_stats(doc.id)
        assert stats["compliance_pct"] == 70.0
