"""Document Service — Repository layer (tenant-scoped)."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Document, DocumentAcknowledgment, DocumentDistribution, DocumentVersion


class DocumentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, document_id: str) -> Document | None:
        result = await self._db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_number(self, tenant_id: str, doc_number: str) -> Document | None:
        result = await self._db.execute(
            select(Document).where(
                Document.tenant_id == tenant_id,
                Document.doc_number == doc_number,
                Document.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_documents(
        self,
        tenant_id: str,
        status: str | None = None,
        doc_type: str | None = None,
        department: str | None = None,
        owner_id: str | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Document], int]:
        query = select(Document).where(
            Document.tenant_id == tenant_id,
            Document.deleted_at.is_(None),
        )
        count_q = select(func.count()).select_from(Document).where(
            Document.tenant_id == tenant_id,
            Document.deleted_at.is_(None),
        )

        if status:
            query = query.where(Document.status == status)
            count_q = count_q.where(Document.status == status)
        if doc_type:
            query = query.where(Document.doc_type == doc_type)
            count_q = count_q.where(Document.doc_type == doc_type)
        if department:
            query = query.where(Document.department == department)
            count_q = count_q.where(Document.department == department)
        if owner_id:
            query = query.where(Document.owner_id == owner_id)
            count_q = count_q.where(Document.owner_id == owner_id)
        if search:
            search_filter = Document.title.ilike(f"%{search}%")
            query = query.where(search_filter)
            count_q = count_q.where(search_filter)

        query = query.offset(offset).limit(limit).order_by(Document.created_at.desc())
        result = await self._db.execute(query)
        count_result = await self._db.execute(count_q)
        return list(result.scalars().all()), count_result.scalar_one()

    async def create(
        self,
        tenant_id: str,
        doc_number: str,
        title: str,
        doc_type: str,
        created_by: str,
        **kwargs,
    ) -> Document:
        now = datetime.now(timezone.utc)
        doc = Document(
            id=str(uuid4()),
            tenant_id=tenant_id,
            doc_number=doc_number,
            title=title,
            doc_type=doc_type,
            status="draft",
            current_version="1.0",
            created_by=created_by,
            created_at=now,
            updated_at=now,
            **kwargs,
        )
        self._db.add(doc)
        await self._db.flush()
        return doc

    async def update(self, document_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(
            update(Document).where(Document.id == document_id).values(**fields)
        )

    async def soft_delete(self, document_id: str) -> None:
        now = datetime.now(timezone.utc)
        await self._db.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(deleted_at=now, updated_at=now)
        )

    async def get_due_for_review(
        self, tenant_id: str, days_ahead: int = 30
    ) -> list[Document]:
        from datetime import timedelta
        threshold = datetime.now(timezone.utc) + timedelta(days=days_ahead)
        try:
            result = await self._db.execute(
                select(Document).where(
                    Document.tenant_id == tenant_id,
                    Document.status == "approved",
                    Document.review_date.is_not(None),
                    Document.review_date <= threshold,
                    Document.deleted_at.is_(None),
                )
            )
            return list(result.scalars().all())
        except Exception as e:
            # Return empty list for any database error to prevent 500
            import structlog
            logger = structlog.get_logger(__name__)
            logger.error("get_due_for_review_failed", tenant_id=tenant_id, error=str(e))
            return []


class DocumentDistributionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_for_document(self, document_id: str) -> list[DocumentDistribution]:
        result = await self._db.execute(
            select(DocumentDistribution)
            .where(DocumentDistribution.document_id == document_id)
            .order_by(DocumentDistribution.created_at.asc())
        )
        return list(result.scalars().all())

    async def add_member(
        self, document_id: str, user_id: str, added_by: str
    ) -> DocumentDistribution:
        row = DocumentDistribution(
            id=str(uuid4()),
            document_id=document_id,
            user_id=user_id,
            added_by=added_by,
            created_at=datetime.now(timezone.utc),
        )
        self._db.add(row)
        await self._db.flush()
        return row


class DocumentVersionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        document_id: str,
        version: str,
        created_by: str,
        file_id: str | None = None,
        change_summary: str | None = None,
        approved_by: str | None = None,
        approved_at: datetime | None = None,
        signature_hash: str | None = None,
    ) -> DocumentVersion:
        dv = DocumentVersion(
            id=str(uuid4()),
            document_id=document_id,
            version=version,
            file_id=file_id,
            change_summary=change_summary,
            approved_by=approved_by,
            approved_at=approved_at,
            signature_hash=signature_hash,
            created_by=created_by,
            created_at=datetime.now(timezone.utc),
        )
        self._db.add(dv)
        await self._db.flush()
        return dv

    async def list_by_document(self, document_id: str) -> list[DocumentVersion]:
        result = await self._db.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.created_at.desc())
        )
        return list(result.scalars().all())
