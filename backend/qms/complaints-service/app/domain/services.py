"""Complaints Service — Complaint lifecycle domain service."""

from datetime import datetime, timezone

import structlog

from rainer_common.exceptions import ForbiddenError, NotFoundError

from ..infra.db.models import Complaint
from ..infra.db.repositories import ComplaintRepository

logger = structlog.get_logger(__name__)


class ComplaintDomainService:
    """Complaint lifecycle management: open → investigate → respond → close."""

    def __init__(self, complaint_repo: ComplaintRepository, tenant_id: str) -> None:
        self._complaints = complaint_repo
        self._tenant_id = tenant_id

    async def list_complaints(
        self,
        status: str | None = None,
        severity: str | None = None,
        category: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Complaint], int]:
        return await self._complaints.list_complaints(
            tenant_id=self._tenant_id,
            status=status, severity=severity, category=category,
            offset=(page - 1) * page_size, limit=page_size,
        )

    async def create_complaint(
        self,
        complaint_number: str,
        description: str,
        received_at: datetime,
        created_by: str,
        customer_name: str | None = None,
        received_via: str = "email",
        severity: str = "minor",
        category: str | None = None,
        investigator_id: str | None = None,
    ) -> Complaint:
        complaint = await self._complaints.create(
            tenant_id=self._tenant_id,
            complaint_number=complaint_number,
            description=description,
            received_at=received_at,
            created_by=created_by,
            customer_name=customer_name,
            received_via=received_via,
            severity=severity,
            category=category,
            investigator_id=investigator_id,
        )
        logger.info("complaint_created", complaint_id=complaint.id, tenant=self._tenant_id)
        return complaint

    async def get_complaint(self, complaint_id: str) -> Complaint:
        complaint = await self._complaints.get_by_id(complaint_id)
        if not complaint:
            raise NotFoundError("Complaint", complaint_id)
        if complaint.tenant_id != self._tenant_id:
            raise ForbiddenError("Access denied to this complaint")
        return complaint

    async def update_complaint(self, complaint_id: str, **fields) -> Complaint:
        await self.get_complaint(complaint_id)
        allowed = {"customer_name", "received_via", "severity", "category", "description",
                   "status", "investigator_id", "root_cause", "capa_id"}
        filtered = {k: v for k, v in fields.items() if k in allowed and v is not None}
        if filtered:
            await self._complaints.update(complaint_id, **filtered)
        return await self.get_complaint(complaint_id)

    async def soft_delete_complaint(self, complaint_id: str) -> None:
        await self.get_complaint(complaint_id)
        await self._complaints.soft_delete(complaint_id)
        logger.info("complaint_soft_deleted", complaint_id=complaint_id)

    async def respond_to_complaint(
        self, complaint_id: str, response_text: str
    ) -> Complaint:
        await self.get_complaint(complaint_id)
        await self._complaints.update(
            complaint_id,
            response_text=response_text,
            response_sent_at=datetime.now(timezone.utc),
            status="responded",
        )
        logger.info("complaint_responded", complaint_id=complaint_id)
        return await self.get_complaint(complaint_id)

    async def escalate_to_capa(self, complaint_id: str, capa_id: str) -> Complaint:
        await self.get_complaint(complaint_id)
        await self._complaints.update(
            complaint_id,
            capa_id=capa_id,
            status="investigating",
        )
        logger.info("complaint_escalated_to_capa", complaint_id=complaint_id, capa_id=capa_id)
        return await self.get_complaint(complaint_id)
