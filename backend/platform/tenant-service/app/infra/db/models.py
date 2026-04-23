"""Tenant Service — SQLAlchemy ORM models (Master DB)."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    db_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    db_user: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    db_host: Mapped[str] = mapped_column(String(255), nullable=False, default="postgres")
    db_port: Mapped[int] = mapped_column(Integer, nullable=False, default=5432)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="provisioning")
    tier: Mapped[str] = mapped_column(String(20), nullable=False, default="starter")
    products: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    region: Mapped[str] = mapped_column(String(50), nullable=False, default="us-east-1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TenantSettings(Base):
    __tablename__ = "tenant_settings"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False, unique=True)
    max_users: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    max_storage_gb: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    features: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    branding: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    smtp_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    webhook_urls: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    timezone: Mapped[str] = mapped_column(String(100), nullable=False, default="UTC")
    locale: Mapped[str] = mapped_column(String(20), nullable=False, default="en-US")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
