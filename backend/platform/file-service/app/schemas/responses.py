"""File Service — Pydantic response schemas."""

from datetime import datetime
from pydantic import BaseModel


class FileResponse(BaseModel):
    id: str
    tenant_id: str | None
    uploaded_by: str | None
    filename: str
    original_filename: str
    content_type: str
    size_bytes: int
    entity_type: str | None
    entity_id: str | None
    module: str | None
    is_public: bool
    virus_scan_status: str
    current_version: int
    metadata: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}

    @classmethod
    def model_validate(cls, obj, **kwargs):
        if hasattr(obj, 'metadata_'):
            return cls(
                id=obj.id,
                tenant_id=obj.tenant_id,
                uploaded_by=obj.uploaded_by,
                filename=obj.filename,
                original_filename=obj.original_filename,
                content_type=obj.content_type,
                size_bytes=obj.size_bytes,
                entity_type=obj.entity_type,
                entity_id=obj.entity_id,
                module=obj.module,
                is_public=obj.is_public,
                virus_scan_status=obj.virus_scan_status,
                current_version=obj.current_version,
                metadata=obj.metadata_,
                created_at=obj.created_at,
                updated_at=obj.updated_at,
            )
        return super().model_validate(obj, **kwargs)


class FileVersionResponse(BaseModel):
    id: str
    file_id: str
    version: int
    s3_key: str
    size_bytes: int
    uploaded_by: str | None
    comment: str | None
    created_at: datetime


class DownloadUrlResponse(BaseModel):
    file_id: str
    url: str
    expires_in: int
