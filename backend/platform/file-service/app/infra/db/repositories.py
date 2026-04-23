"""File Service — Repository layer."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import FileRecord, FileVersion


class FileRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, file_id: str) -> FileRecord | None:
        result = await self._db.execute(
            select(FileRecord).where(
                FileRecord.id == file_id,
                FileRecord.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def list_by_entity(
        self, entity_type: str, entity_id: str, tenant_id: str | None = None
    ) -> list[FileRecord]:
        query = select(FileRecord).where(
            FileRecord.entity_type == entity_type,
            FileRecord.entity_id == entity_id,
            FileRecord.is_deleted.is_(False),
        )
        if tenant_id:
            query = query.where(FileRecord.tenant_id == tenant_id)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def list_all(
        self,
        tenant_id: str | None = None,
        entity_type: str | None = None,
        module: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[FileRecord], int]:
        query = select(FileRecord).where(FileRecord.is_deleted.is_(False))
        count_query = select(func.count()).select_from(FileRecord).where(FileRecord.is_deleted.is_(False))

        if tenant_id:
            query = query.where(FileRecord.tenant_id == tenant_id)
            count_query = count_query.where(FileRecord.tenant_id == tenant_id)
        if entity_type:
            query = query.where(FileRecord.entity_type == entity_type)
            count_query = count_query.where(FileRecord.entity_type == entity_type)
        if module:
            query = query.where(FileRecord.module == module)
            count_query = count_query.where(FileRecord.module == module)

        query = query.offset(offset).limit(limit).order_by(FileRecord.created_at.desc())
        result = await self._db.execute(query)
        count_result = await self._db.execute(count_query)
        return list(result.scalars().all()), count_result.scalar_one()

    async def create(
        self,
        filename: str,
        original_filename: str,
        content_type: str,
        size_bytes: int,
        s3_key: str,
        s3_bucket: str,
        tenant_id: str | None = None,
        uploaded_by: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        module: str | None = None,
        is_public: bool = False,
        metadata: dict | None = None,
    ) -> FileRecord:
        now = datetime.now(timezone.utc)
        file = FileRecord(
            id=str(uuid4()),
            tenant_id=tenant_id,
            uploaded_by=uploaded_by,
            filename=filename,
            original_filename=original_filename,
            content_type=content_type,
            size_bytes=size_bytes,
            s3_key=s3_key,
            s3_bucket=s3_bucket,
            entity_type=entity_type,
            entity_id=entity_id,
            module=module,
            is_public=is_public,
            is_deleted=False,
            virus_scan_status="pending",
            metadata_=metadata or {},
            current_version=1,
            created_at=now,
            updated_at=now,
        )
        self._db.add(file)
        await self._db.flush()
        return file

    async def soft_delete(self, file_id: str) -> None:
        now = datetime.now(timezone.utc)
        await self._db.execute(
            update(FileRecord)
            .where(FileRecord.id == file_id)
            .values(is_deleted=True, deleted_at=now, updated_at=now)
        )

    async def update_virus_scan(self, file_id: str, status: str) -> None:
        await self._db.execute(
            update(FileRecord)
            .where(FileRecord.id == file_id)
            .values(virus_scan_status=status, updated_at=datetime.now(timezone.utc))
        )

    async def increment_version(self, file_id: str) -> int:
        file = await self.get_by_id(file_id)
        if not file:
            return 0
        new_version = file.current_version + 1
        await self._db.execute(
            update(FileRecord)
            .where(FileRecord.id == file_id)
            .values(current_version=new_version, updated_at=datetime.now(timezone.utc))
        )
        return new_version


class FileVersionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        file_id: str,
        version: int,
        s3_key: str,
        size_bytes: int,
        uploaded_by: str | None = None,
        comment: str | None = None,
    ) -> FileVersion:
        fv = FileVersion(
            id=str(uuid4()),
            file_id=file_id,
            version=version,
            s3_key=s3_key,
            size_bytes=size_bytes,
            uploaded_by=uploaded_by,
            comment=comment,
            created_at=datetime.now(timezone.utc),
        )
        self._db.add(fv)
        await self._db.flush()
        return fv

    async def list_by_file(self, file_id: str) -> list[FileVersion]:
        result = await self._db.execute(
            select(FileVersion)
            .where(FileVersion.file_id == file_id)
            .order_by(FileVersion.version.asc())
        )
        return list(result.scalars().all())
