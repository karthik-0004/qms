"""Audit Service — Pydantic response schemas."""

from datetime import datetime

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: str
    tenant_id: str | None
    user_id: str | None
    action: str
    resource_type: str | None
    resource_id: str | None
    ip_address: str | None
    user_agent: str | None
    metadata: dict
    severity: str
    source_service: str | None
    event_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}

    @classmethod
    def model_validate(cls, obj, **kwargs):
        if hasattr(obj, 'metadata_'):
            data = {c.key: getattr(obj, c.key) for c in obj.__table__.columns}
            data['metadata'] = obj.metadata_
            return cls(**data)
        return super().model_validate(obj, **kwargs)
