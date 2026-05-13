"""Document Service — Core document lifecycle domain service."""

import hashlib
from datetime import datetime, timezone

import structlog

from rainer_common.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError

from ..infra.db.models import Document, DocumentDistribution, DocumentVersion
from ..infra.db.repositories import DocumentDistributionRepository, DocumentRepository, DocumentVersionRepository

logger = structlog.get_logger(__name__)

VALID_STATUSES = {"draft", "under_review", "approved", "obsolete"}
VALID_TRANSITIONS = {
    "draft": {"submit_for_review"},
    "under_review": {"approve", "reject"},
    "approved": {"make_obsolete", "create_new_version"},
    "obsolete": set(),
}


class DocumentDomainService:
    """Core document lifecycle business logic: create → review → approve → obsolete."""

    def __init__(
        self,
        doc_repo: DocumentRepository,
        version_repo: DocumentVersionRepository,
        distribution_repo: DocumentDistributionRepository,
        tenant_id: str,
    ) -> None:
        self._docs = doc_repo
        self._versions = version_repo
        self._distribution = distribution_repo
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

        logger.info("document_submitted_for_review", doc_id=document_id, submitted_by=submitted_by)
        return await self.get_document(document_id)

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

        logger.info("document_approved", doc_id=document_id, approved_by=approved_by)
        return await self.get_document(document_id)

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
        logger.info("document_rejected", doc_id=document_id, rejected_by=rejected_by)
        return await self.get_document(document_id)

    async def make_obsolete(self, document_id: str, updated_by: str) -> Document:
        """Mark an approved document as Obsolete."""
        doc = await self.get_document(document_id)
        self._assert_transition(doc.status, "make_obsolete")

        await self._docs.update(document_id, status="obsolete")
        logger.info("document_made_obsolete", doc_id=document_id, updated_by=updated_by)
        return await self.get_document(document_id)

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
        if doc.status == "approved":
            raise ForbiddenError("Cannot delete approved documents. Use 'make_obsolete' instead.")
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
