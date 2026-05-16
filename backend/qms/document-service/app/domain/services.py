"""Document Service — Core document lifecycle domain service."""

import hashlib
from datetime import datetime, timezone

import structlog

from rainer_common.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError

from ..events.publisher import (
    publish_document_acknowledged,
    publish_document_approved,
    publish_document_created,
    publish_document_effective,
    publish_document_obsolete,
    publish_document_rejected,
    publish_document_submitted,
    publish_document_superseded,
    publish_document_version_created,
)
from ..infra.db.models import Document, DocumentAcknowledgment, DocumentDistribution, DocumentVersion
from ..infra.db.repositories import (
    AcknowledgmentRepository,
    DocumentDistributionRepository,
    DocumentRepository,
    DocumentVersionRepository,
)

logger = structlog.get_logger(__name__)

VALID_STATUSES = {"draft", "under_review", "approved", "effective", "superseded", "obsolete"}
VALID_TRANSITIONS = {
    "draft": {"submit_for_review"},
    "under_review": {"approve", "reject"},
    "approved": {"make_effective", "make_obsolete", "create_new_version"},
    "effective": {"make_superseded", "make_obsolete", "create_new_version"},
    "superseded": {"make_obsolete"},
    "obsolete": set(),
}


class DocumentDomainService:
    """Core document lifecycle business logic: create → review → approve → obsolete."""

    def __init__(
        self,
        doc_repo: DocumentRepository,
        version_repo: DocumentVersionRepository,
        distribution_repo: DocumentDistributionRepository,
        ack_repo: AcknowledgmentRepository,
        tenant_id: str,
    ) -> None:
        self._docs = doc_repo
        self._versions = version_repo
        self._distribution = distribution_repo
        self._acks = ack_repo
        self._tenant_id = tenant_id

    async def create_document(
        self,
        doc_number: str,
        title: str,
        doc_type: str,
        created_by: str,
        description: str | None = None,
        department: str | None = None,
        owner_id: str | None = None,
        tags: list[str] | None = None,
        regulatory_frameworks: list[str] | None = None,
        file_id: str | None = None,
        review_period_days: int | None = None,
    ) -> Document:
        """Create a new document in Draft status."""
        existing = await self._docs.get_by_number(self._tenant_id, doc_number)
        if existing:
            raise ConflictError(f"Document with number '{doc_number}' already exists")

        doc = await self._docs.create(
            tenant_id=self._tenant_id,
            doc_number=doc_number,
            title=title,
            doc_type=doc_type,
            created_by=created_by,
            description=description,
            department=department,
            owner_id=owner_id or created_by,
            tags=tags or [],
            regulatory_frameworks=regulatory_frameworks or [],
            file_id=file_id,
        )

        # Record initial version
        await self._versions.create(
            document_id=doc.id,
            version="1.0",
            created_by=created_by,
            file_id=file_id,
            change_summary="Initial version",
        )

        await publish_document_created(doc, created_by)
        logger.info("document_created", doc_id=doc.id, doc_number=doc_number, tenant=self._tenant_id)
        return doc

    async def get_document(self, document_id: str) -> Document:
        doc = await self._docs.get_by_id(document_id)
        if not doc:
            raise NotFoundError("Document", document_id)
        if doc.tenant_id != self._tenant_id:
            raise ForbiddenError("Access denied to this document")
        return doc

    async def list_documents(
        self,
        status: str | None = None,
        doc_type: str | None = None,
        department: str | None = None,
        owner_id: str | None = None,
        search: str | None = None,
        taxonomy_id: str | None = None,
        folder_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Document], int]:
        return await self._docs.list_documents(
            tenant_id=self._tenant_id,
            status=status,
            doc_type=doc_type,
            department=department,
            owner_id=owner_id,
            search=search,
            taxonomy_id=taxonomy_id,
            folder_id=folder_id,
            offset=(page - 1) * page_size,
            limit=page_size,
        )

    async def submit_for_review(
        self,
        document_id: str,
        submitted_by: str,
        approver_id: str | None = None,
        comment: str | None = None,
    ) -> Document:
        """Transition document from Draft → Under Review."""
        doc = await self.get_document(document_id)
        self._assert_transition(doc.status, "submit_for_review")

        await self._docs.update(
            document_id,
            status="under_review",
            approver_id=approver_id or doc.approver_id,
            last_rejection_reason=None,
        )

        doc = await self.get_document(document_id)
        await publish_document_submitted(doc, submitted_by, approver_id)
        logger.info("document_submitted_for_review", doc_id=document_id, submitted_by=submitted_by)
        return doc

    async def approve_document(
        self,
        document_id: str,
        approved_by: str,
        signature: str,
        comment: str | None = None,
        effective_date: datetime | None = None,
        review_date: datetime | None = None,
    ) -> Document:
        """Transition document from Under Review → Approved with e-signature."""
        doc = await self.get_document(document_id)
        self._assert_transition(doc.status, "approve")

        if not signature:
            raise ValidationError("E-signature is required for document approval")

        # Hash the e-signature for audit trail
        signature_hash = hashlib.sha256(
            f"{approved_by}:{document_id}:{doc.current_version}:{signature}".encode()
        ).hexdigest()

        now = datetime.now(timezone.utc)
        await self._docs.update(
            document_id,
            status="approved",
            effective_date=effective_date or now,
            review_date=review_date,
        )

        # Record version approval
        versions = await self._versions.list_by_document(document_id)
        if versions:
            latest = versions[0]
            from sqlalchemy import update as sqla_update
            await self._docs._db.execute(
                sqla_update(DocumentVersion)
                .where(DocumentVersion.id == latest.id)
                .values(
                    approved_by=approved_by,
                    approved_at=now,
                    signature_hash=signature_hash,
                )
            )

        doc = await self.get_document(document_id)
        await publish_document_approved(doc, approved_by, signature_hash)
        logger.info("document_approved", doc_id=document_id, approved_by=approved_by)
        return doc

    async def reject_document(
        self,
        document_id: str,
        rejected_by: str,
        reason: str,
    ) -> Document:
        """Return document from Under Review → Draft."""
        doc = await self.get_document(document_id)
        self._assert_transition(doc.status, "reject")

        await self._docs.update(document_id, status="draft", last_rejection_reason=reason)
        doc = await self.get_document(document_id)
        await publish_document_rejected(doc, rejected_by, reason)
        logger.info("document_rejected", doc_id=document_id, rejected_by=rejected_by)
        return doc

    async def make_effective(self, document_id: str, updated_by: str) -> Document:
        """Transition document from Approved → Effective."""
        doc = await self.get_document(document_id)
        self._assert_transition(doc.status, "make_effective")

        await self._docs.update(document_id, status="effective")
        doc = await self.get_document(document_id)
        await publish_document_effective(doc, updated_by)
        logger.info("document_made_effective", doc_id=document_id, updated_by=updated_by)
        return doc

    async def make_superseded(self, document_id: str, updated_by: str) -> Document:
        """Transition document from Effective → Superseded."""
        doc = await self.get_document(document_id)
        self._assert_transition(doc.status, "make_superseded")

        await self._docs.update(document_id, status="superseded")
        doc = await self.get_document(document_id)
        await publish_document_superseded(doc, updated_by)
        logger.info("document_made_superseded", doc_id=document_id, updated_by=updated_by)
        return doc

    async def make_obsolete(self, document_id: str, updated_by: str) -> Document:
        """Mark a document as Obsolete (from approved/effective/superseded)."""
        doc = await self.get_document(document_id)
        self._assert_transition(doc.status, "make_obsolete")
        previous_status = doc.status

        await self._docs.update(document_id, status="obsolete")
        doc = await self.get_document(document_id)
        await publish_document_obsolete(doc, updated_by, previous_status)
        logger.info("document_made_obsolete", doc_id=document_id, updated_by=updated_by)
        return doc

    async def update_document(self, document_id: str, updated_by: str, **fields) -> Document:
        """Update mutable fields of a draft document."""
        doc = await self.get_document(document_id)
        if doc.status not in ("draft",):
            raise ForbiddenError("Only draft documents can be directly edited")

        allowed_fields = {"title", "description", "department", "owner_id", "approver_id",
                          "tags", "regulatory_frameworks", "file_id"}
        filtered = {k: v for k, v in fields.items() if k in allowed_fields}
        if filtered:
            await self._docs.update(document_id, **filtered)

        logger.info("document_updated", doc_id=document_id, updated_by=updated_by)
        return await self.get_document(document_id)

    async def delete_document(self, document_id: str, deleted_by: str) -> None:
        doc = await self.get_document(document_id)
        if doc.status in ("approved", "effective", "superseded"):
            raise ForbiddenError("Cannot delete documents in approved, effective, or superseded status. Use 'make_obsolete' instead.")
        await self._docs.soft_delete(document_id)
        logger.info("document_deleted", doc_id=document_id, deleted_by=deleted_by)

    async def get_versions(self, document_id: str) -> list[DocumentVersion]:
        await self.get_document(document_id)
        return await self._versions.list_by_document(document_id)

    async def get_due_for_review(self, days_ahead: int = 30) -> list[Document]:
        return await self._docs.get_due_for_review(self._tenant_id, days_ahead)

    async def list_distribution(self, document_id: str) -> list[DocumentDistribution]:
        await self.get_document(document_id)
        return await self._distribution.list_for_document(document_id)

    async def acknowledge_document(
        self, document_id: str, user_id: str, signature: str, ip_address: str | None = None
    ) -> DocumentAcknowledgment:
        """Acknowledge a document with e-signature (ISO 17025 compliance)."""
        doc = await self.get_document(document_id)
        if doc.status not in ("effective", "approved"):
            raise ValidationError("Only effective or approved documents can be acknowledged")

        existing = await self._acks.get_for_document_and_user(document_id, user_id)
        if existing:
            raise ConflictError("User has already acknowledged this document")

        signature_hash = hashlib.sha256(
            f"{user_id}:{document_id}:{doc.current_version}:{signature}".encode()
        ).hexdigest()

        ack = await self._acks.create(
            document_id=document_id,
            user_id=user_id,
            version=doc.current_version,
            signature_hash=signature_hash,
            ip_address=ip_address,
        )

        await publish_document_acknowledged(doc, ack, user_id)
        logger.info(
            "document_acknowledged",
            doc_id=document_id,
            user_id=user_id,
            version=doc.current_version,
            tenant=self._tenant_id,
        )
        return ack

    async def list_acknowledgments(self, document_id: str) -> list[DocumentAcknowledgment]:
        await self.get_document(document_id)
        return await self._acks.list_for_document(document_id)

    async def get_my_pending_acknowledgments(self, user_id: str) -> list[dict]:
        """Return documents on the user's distribution list they haven't acknowledged."""
        pending = []
        try:
            dist_entries = await self._distribution.list_for_user(user_id)
            for entry in dist_entries:
                doc = await self._docs.get_by_id(entry.document_id)
                if not doc or doc.deleted_at:
                    continue
                ack = await self._acks.get_for_document_and_user(entry.document_id, user_id)
                if not ack:
                    pending.append({
                        "document_id": entry.document_id,
                        "doc_number": doc.doc_number,
                        "title": doc.title,
                        "version": doc.current_version,
                        "status": doc.status,
                    })
        except Exception as e:
            logger.error("pending_acks_failed", user_id=user_id, error=str(e))
        return pending

    async def get_acknowledgment_compliance_stats(self, document_id: str) -> dict:
        await self.get_document(document_id)
        return await self._acks.get_compliance_stats(document_id)

    async def create_new_version(
        self,
        document_id: str,
        change_type: str,
        change_summary: str,
        created_by: str,
        new_file_id: str | None = None,
    ) -> Document:
        """Create a new version of an approved/effective document.

        - Snapshots the prior version's content_ast/html_snapshot into the prior DocumentVersion row
        - Creates a new DocumentVersion row for the incoming version
        - Bumps the document's current_version
        - Sets document status back to draft for the new edit cycle
        """
        doc = await self.get_document(document_id)
        self._assert_transition(doc.status, "create_new_version")

        old_version = doc.current_version

        # Compute next version number
        parts = old_version.split(".")
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
        if change_type == "major":
            new_version = f"{major + 1}.0"
        else:
            new_version = f"{major}.{minor + 1}"

        # Snapshot prior version's content into the latest DocumentVersion row
        versions = await self._versions.list_by_document(document_id)
        if versions:
            latest_version_row = versions[0]
            if doc.content_ast or doc.html_snapshot:
                from sqlalchemy import update as sqla_update
                await self._docs._db.execute(
                    sqla_update(DocumentVersion)
                    .where(DocumentVersion.id == latest_version_row.id)
                    .values(
                        authoring_mode=doc.authoring_mode,
                        content_ast=doc.content_ast,
                        html_snapshot=doc.html_snapshot,
                    )
                )

        # Create new version row
        await self._versions.create(
            document_id=document_id,
            version=new_version,
            created_by=created_by,
            file_id=new_file_id,
            change_summary=change_summary,
        )

        # Update parent document
        await self._docs.update(
            document_id,
            status="draft",
            current_version=new_version,
            file_id=new_file_id,
        )

        doc = await self.get_document(document_id)
        await publish_document_version_created(
            doc, created_by, change_summary, old_version, new_version
        )
        logger.info(
            "document_new_version",
            doc_id=document_id,
            prev_version=old_version,
            new_version=new_version,
            change_type=change_type,
            created_by=created_by,
            tenant=self._tenant_id,
        )
        return doc

    async def add_distribution_member(
        self, document_id: str, user_id: str, added_by: str
    ) -> DocumentDistribution:
        await self.get_document(document_id)
        existing = await self._distribution.list_for_document(document_id)
        if any(m.user_id == user_id for m in existing):
            raise ConflictError("User is already on the distribution list for this document")
        return await self._distribution.add_member(document_id, user_id, added_by)

    def _assert_transition(self, current_status: str, action: str) -> None:
        allowed_actions = VALID_TRANSITIONS.get(current_status, set())
        if action not in allowed_actions:
            raise ValidationError(
                f"Action '{action}' is not allowed for document in '{current_status}' status. "
                f"Allowed: {allowed_actions}"
            )
