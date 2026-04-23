"""Rainer Common — Standard response envelope models."""

from datetime import datetime, timezone
from typing import Any, Generic, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseMeta(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    service: str | None = None
    version: str | None = None


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool

    @classmethod
    def create(cls, page: int, page_size: int, total: int) -> "PaginationMeta":
        total_pages = max(1, (total + page_size - 1) // page_size)
        return cls(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    meta: ResponseMeta = Field(default_factory=ResponseMeta)

    @classmethod
    def of(cls, data: T, request_id: str | None = None) -> "SuccessResponse[T]":
        meta = ResponseMeta()
        if request_id:
            meta.request_id = request_id
        return cls(data=data, meta=meta)


class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    data: list[T]
    pagination: PaginationMeta
    meta: ResponseMeta = Field(default_factory=ResponseMeta)

    @classmethod
    def of(
        cls,
        data: list[T],
        page: int,
        page_size: int,
        total: int,
        request_id: str | None = None,
    ) -> "PaginatedResponse[T]":
        meta = ResponseMeta()
        if request_id:
            meta.request_id = request_id
        return cls(
            data=data,
            pagination=PaginationMeta.create(page=page, page_size=page_size, total=total),
            meta=meta,
        )


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str
    code: str | None = None


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorBody
    meta: ResponseMeta = Field(default_factory=ResponseMeta)

    @classmethod
    def of(
        cls,
        code: str,
        message: str,
        details: list[dict[str, Any]] | None = None,
        request_id: str | None = None,
    ) -> "ErrorResponse":
        meta = ResponseMeta()
        if request_id:
            meta.request_id = request_id
        error_details = [ErrorDetail(**d) for d in (details or [])]
        return cls(
            error=ErrorBody(code=code, message=message, details=error_details),
            meta=meta,
        )


class MessageResponse(BaseModel):
    success: bool = True
    message: str
    meta: ResponseMeta = Field(default_factory=ResponseMeta)

