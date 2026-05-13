"""Analytics Service — Read-only mirror models for cross-service aggregation.

These models map to tables owned by document-service and capa-service.
They are declared with extend_existing=True so that if the same Python
process happens to import the owning service's models they won't clash.
No migrations are generated from this Base — migrations are the sole
responsibility of the owning services.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DocumentMirror(Base):
    """Read-only mirror of document-service `documents` table."""

    __tablename__ = "documents"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CAPAMirror(Base):
    """Read-only mirror of capa-service `capas` table."""

    __tablename__ = "capas"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
