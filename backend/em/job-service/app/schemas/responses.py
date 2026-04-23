"""Job Service — Pydantic response schemas."""

from datetime import datetime
from pydantic import BaseModel


class JobResponse(BaseModel):
    id: str
    tenant_id: str
    job_type: str
    payload: dict
    status: str
    priority: int
    created_by: str
    worker_id: str | None
    result: dict | None
    error_message: str | None
    retry_count: int
    max_retries: int
    next_retry_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
