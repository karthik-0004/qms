"""Job Service — Pydantic request schemas."""

from pydantic import BaseModel, Field


class EnqueueJobRequest(BaseModel):
    job_type: str = Field(min_length=1)
    payload: dict = {}
    priority: int = Field(default=5, ge=1, le=10)
    max_retries: int | None = None


class ClaimJobRequest(BaseModel):
    worker_id: str = Field(min_length=1)
    job_type: str | None = None


class CompleteJobRequest(BaseModel):
    result: dict = {}


class FailJobRequest(BaseModel):
    error_message: str = Field(min_length=1)
    retry: bool = True
