"""Document Service — Repository layer (tenant-scoped)."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    ControlledCopy,
    Document,
    DocumentAcknowledgment,
    DocumentDistribution,
    DocumentVersion,
    Folder,
    Taxonomy,
)


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
        taxonomy_id: str | None = None,
        folder_id: str | None = None,
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
        if folder_id:
            query = query.where(Document.folder_id == folder_id)
            count_q = count_q.where(Document.folder_id == folder_id)
        elif taxonomy_id:
            query = query.where(Document.taxonomy_id == taxonomy_id)
            count_q = count_q.where(Document.taxonomy_id == taxonomy_id)
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
                    Document.status.in_(["approved", "effective"]),
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

    async def list_for_user(self, user_id: str) -> list[DocumentDistribution]:
        result = await self._db.execute(
            select(DocumentDistribution)
            .where(DocumentDistribution.user_id == user_id)
            .order_by(DocumentDistribution.created_at.desc())
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


class AcknowledgmentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        document_id: str,
        user_id: str,
        version: str,
        signature_hash: str | None = None,
        ip_address: str | None = None,
    ) -> DocumentAcknowledgment:
        row = DocumentAcknowledgment(
            id=str(uuid4()),
            document_id=document_id,
            user_id=user_id,
            acknowledged_at=datetime.now(timezone.utc),
            version=version,
            signature_hash=signature_hash,
            ip_address=ip_address,
        )
        self._db.add(row)
        await self._db.flush()
        return row

    async def list_for_document(self, document_id: str) -> list[DocumentAcknowledgment]:
        result = await self._db.execute(
            select(DocumentAcknowledgment)
            .where(DocumentAcknowledgment.document_id == document_id)
            .order_by(DocumentAcknowledgment.acknowledged_at.asc())
        )
        return list(result.scalars().all())

    async def list_for_user(self, user_id: str) -> list[DocumentAcknowledgment]:
        result = await self._db.execute(
            select(DocumentAcknowledgment)
            .where(DocumentAcknowledgment.user_id == user_id)
            .order_by(DocumentAcknowledgment.acknowledged_at.desc())
        )
        return list(result.scalars().all())

    async def get_for_document_and_user(
        self, document_id: str, user_id: str
    ) -> DocumentAcknowledgment | None:
        result = await self._db.execute(
            select(DocumentAcknowledgment).where(
                DocumentAcknowledgment.document_id == document_id,
                DocumentAcknowledgment.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_compliance_stats(self, document_id: str) -> dict:
        from sqlalchemy import func as sa_func
        total = await self._db.execute(
            select(sa_func.count()).select_from(DocumentDistribution).where(
                DocumentDistribution.document_id == document_id
            )
        )
        total_count = total.scalar_one()
        ack_result = await self._db.execute(
            select(sa_func.count()).select_from(DocumentAcknowledgment).where(
                DocumentAcknowledgment.document_id == document_id
            )
        )
        ack_count = ack_result.scalar_one()
        return {
            "total_distribution": total_count,
            "acknowledged": ack_count,
            "pending": total_count - ack_count,
            "compliance_pct": round((ack_count / total_count * 100) if total_count > 0 else 0, 1),
        }


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


class TaxonomyRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list(self, tenant_id: str) -> list[Taxonomy]:
        result = await self._db.execute(
            select(Taxonomy)
            .where(Taxonomy.tenant_id == tenant_id)
            .order_by(Taxonomy.sort_order.asc(), Taxonomy.name.asc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, taxonomy_id: str) -> Taxonomy | None:
        result = await self._db.execute(
            select(Taxonomy).where(Taxonomy.id == taxonomy_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self, tenant_id: str, name: str, description: str | None = None,
        sort_order: int = 0, created_by: str = "",
    ) -> Taxonomy:
        now = datetime.now(timezone.utc)
        row = Taxonomy(
            id=str(uuid4()), tenant_id=tenant_id, name=name,
            description=description, sort_order=sort_order,
            created_by=created_by, created_at=now, updated_at=now,
        )
        self._db.add(row)
        await self._db.flush()
        return row

    async def update(self, taxonomy_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(
            update(Taxonomy).where(Taxonomy.id == taxonomy_id).values(**fields)
        )

    async def delete(self, taxonomy_id: str) -> None:
        await self._db.execute(
            update(Taxonomy).where(Taxonomy.id == taxonomy_id).values(deleted_at=datetime.now(timezone.utc))
        )


class FolderRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list(self, taxonomy_id: str) -> list[Folder]:
        result = await self._db.execute(
            select(Folder)
            .where(Folder.taxonomy_id == taxonomy_id)
            .order_by(Folder.sort_order.asc(), Folder.name.asc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, folder_id: str) -> Folder | None:
        result = await self._db.execute(
            select(Folder).where(Folder.id == folder_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self, tenant_id: str, taxonomy_id: str, name: str,
        parent_id: str | None = None, description: str | None = None,
        path: str = "", sort_order: int = 0, created_by: str = "",
    ) -> Folder:
        now = datetime.now(timezone.utc)
        row = Folder(
            id=str(uuid4()), tenant_id=tenant_id, taxonomy_id=taxonomy_id,
            parent_id=parent_id, name=name, description=description,
            path=path, sort_order=sort_order,
            created_by=created_by, created_at=now, updated_at=now,
        )
        self._db.add(row)
        await self._db.flush()
        return row

    async def update(self, folder_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(
            update(Folder).where(Folder.id == folder_id).values(**fields)
        )

    async def delete(self, folder_id: str) -> None:
        await self._db.execute(
            update(Folder).where(Folder.id == folder_id).values(deleted_at=datetime.now(timezone.utc))
        )


class ControlledCopyRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_for_document(self, document_id: str) -> list[ControlledCopy]:
        result = await self._db.execute(
            select(ControlledCopy)
            .where(ControlledCopy.document_id == document_id)
            .order_by(ControlledCopy.issued_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, copy_id: str) -> ControlledCopy | None:
        result = await self._db.execute(
            select(ControlledCopy).where(ControlledCopy.id == copy_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self, document_id: str, version: str, copy_number: str,
        issued_to: str, issued_by: str, notes: str | None = None,
    ) -> ControlledCopy:
        now = datetime.now(timezone.utc)
        row = ControlledCopy(
            id=str(uuid4()), document_id=document_id, version=version,
            copy_number=copy_number, issued_to=issued_to,
            issued_by=issued_by, issued_at=now, status="active", notes=notes,
        )
        self._db.add(row)
        await self._db.flush()
        return row

    async def recall(self, copy_id: str) -> None:
        now = datetime.now(timezone.utc)
        await self._db.execute(
            update(ControlledCopy)
            .where(ControlledCopy.id == copy_id)
            .values(status="recalled", recalled_at=now)
        )
