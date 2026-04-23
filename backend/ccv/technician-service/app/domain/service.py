import uuid
from datetime import datetime, timezone
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.db.repository import (
    TechnicianRepository,
    TechnicianCertificationRepository,
    TechnicianAvailabilityRepository,
)
from app.infra.db.models import Technician, TechnicianCertification, TechnicianAvailability

logger = structlog.get_logger()

VALID_TECHNICIAN_TRANSITIONS: dict[str, list[str]] = {
    "available":      ["on_assignment", "on_leave", "inactive"],
    "on_assignment":  ["available", "on_leave"],
    "on_leave":       ["available", "inactive"],
    "inactive":       ["available"],
}

VALID_AVAILABILITY_TYPES = {
    "available", "unavailable", "on_leave", "training", "holiday"
}


class TechnicianDomainService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._technicians = TechnicianRepository(session)
        self._certifications = TechnicianCertificationRepository(session)
        self._availability = TechnicianAvailabilityRepository(session)

    async def register_technician(
        self,
        tenant_id: uuid.UUID,
        created_by: uuid.UUID,
        employee_number: str,
        first_name: str,
        last_name: str,
        email: str,
        **kwargs,
    ) -> Technician:
        existing_emp = await self._technicians.get_by_employee_number(employee_number, tenant_id)
        if existing_emp:
            raise ValueError(f"Employee number '{employee_number}' already registered")
        existing_email = await self._technicians.get_by_email(email, tenant_id)
        if existing_email:
            raise ValueError(f"Email '{email}' already registered")

        tech = await self._technicians.create({
            "tenant_id": tenant_id,
            "created_by": created_by,
            "employee_number": employee_number,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "status": "available",
            **kwargs,
        })
        logger.info("technician.registered", tech_id=str(tech.id))
        return tech

    async def get_technician(self, tech_id: uuid.UUID, tenant_id: uuid.UUID) -> Technician:
        tech = await self._technicians.get_by_id(tech_id, tenant_id)
        if not tech:
            raise LookupError(f"Technician {tech_id} not found")
        return tech

    async def list_technicians(
        self,
        tenant_id: uuid.UUID,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Technician]:
        return await self._technicians.list(tenant_id, status=status, skip=skip, limit=limit)

    async def transition_status(
        self,
        tech_id: uuid.UUID,
        tenant_id: uuid.UUID,
        new_status: str,
        changed_by: uuid.UUID,
    ) -> Technician:
        tech = await self.get_technician(tech_id, tenant_id)
        allowed = VALID_TECHNICIAN_TRANSITIONS.get(tech.status, [])
        if new_status not in allowed:
            raise ValueError(
                f"Cannot transition technician from '{tech.status}' to '{new_status}'"
            )
        tech = await self._technicians.update(
            tech, {"status": new_status, "changed_by": changed_by}
        )
        logger.info("technician.status_changed", tech_id=str(tech_id), to_status=new_status)
        return tech

    async def update_technician(
        self,
        tech_id: uuid.UUID,
        tenant_id: uuid.UUID,
        changed_by: uuid.UUID,
        **kwargs,
    ) -> Technician:
        tech = await self.get_technician(tech_id, tenant_id)
        kwargs["changed_by"] = changed_by
        return await self._technicians.update(tech, kwargs)

    # ─── Certifications ───────────────────────────────────────────────────────

    async def add_certification(
        self,
        tech_id: uuid.UUID,
        tenant_id: uuid.UUID,
        created_by: uuid.UUID,
        certification_name: str,
        **kwargs,
    ) -> TechnicianCertification:
        await self.get_technician(tech_id, tenant_id)
        cert = await self._certifications.create({
            "technician_id": tech_id,
            "created_by": created_by,
            "certification_name": certification_name,
            **kwargs,
        })
        logger.info("certification.added", tech_id=str(tech_id), cert=certification_name)
        return cert

    async def list_certifications(
        self, tech_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> list[TechnicianCertification]:
        await self.get_technician(tech_id, tenant_id)
        return await self._certifications.list_for_technician(tech_id)

    async def revoke_certification(
        self, tech_id: uuid.UUID, tenant_id: uuid.UUID, cert_id: uuid.UUID
    ) -> TechnicianCertification:
        await self.get_technician(tech_id, tenant_id)
        cert = await self._certifications.get_by_id(cert_id, tech_id)
        if not cert:
            raise LookupError(f"Certification {cert_id} not found")
        cert.is_active = False
        await self._session.flush()
        return cert

    # ─── Availability ─────────────────────────────────────────────────────────

    async def set_availability(
        self,
        tech_id: uuid.UUID,
        tenant_id: uuid.UUID,
        availability_type: str,
        start_dt: datetime,
        end_dt: datetime,
        **kwargs,
    ) -> TechnicianAvailability:
        if availability_type not in VALID_AVAILABILITY_TYPES:
            raise ValueError(f"Invalid availability_type: {availability_type}")
        if end_dt <= start_dt:
            raise ValueError("end_dt must be after start_dt")

        await self.get_technician(tech_id, tenant_id)
        avail = await self._availability.create({
            "technician_id": tech_id,
            "availability_type": availability_type,
            "start_dt": start_dt,
            "end_dt": end_dt,
            **kwargs,
        })
        return avail

    async def list_availability(
        self, tech_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> list[TechnicianAvailability]:
        await self.get_technician(tech_id, tenant_id)
        return await self._availability.list_for_technician(tech_id)
