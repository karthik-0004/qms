import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.infra.db.models import Technician, TechnicianCertification, TechnicianAvailability


class TechnicianRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict) -> Technician:
        tech = Technician(**data)
        self._session.add(tech)
        await self._session.flush()
        await self._session.refresh(tech)
        return tech

    async def get_by_id(self, tech_id: uuid.UUID, tenant_id: uuid.UUID) -> Technician | None:
        result = await self._session.execute(
            select(Technician).where(
                and_(
                    Technician.id == tech_id,
                    Technician.tenant_id == tenant_id,
                    Technician.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_employee_number(self, emp_num: str, tenant_id: uuid.UUID) -> Technician | None:
        result = await self._session.execute(
            select(Technician).where(
                and_(
                    Technician.employee_number == emp_num,
                    Technician.tenant_id == tenant_id,
                    Technician.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str, tenant_id: uuid.UUID) -> Technician | None:
        result = await self._session.execute(
            select(Technician).where(
                and_(
                    Technician.email == email,
                    Technician.tenant_id == tenant_id,
                    Technician.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        tenant_id: uuid.UUID,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Technician]:
        stmt = select(Technician).where(
            and_(Technician.tenant_id == tenant_id, Technician.deleted_at.is_(None))
        )
        if status:
            stmt = stmt.where(Technician.status == status)
        stmt = stmt.offset(skip).limit(limit).order_by(Technician.last_name)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, tech: Technician, data: dict) -> Technician:
        for key, value in data.items():
            setattr(tech, key, value)
        await self._session.flush()
        await self._session.refresh(tech)
        return tech

    async def soft_delete(self, tech: Technician) -> None:
        tech.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()


class TechnicianCertificationRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict) -> TechnicianCertification:
        cert = TechnicianCertification(**data)
        self._session.add(cert)
        await self._session.flush()
        await self._session.refresh(cert)
        return cert

    async def list_for_technician(self, tech_id: uuid.UUID) -> list[TechnicianCertification]:
        result = await self._session.execute(
            select(TechnicianCertification)
            .where(TechnicianCertification.technician_id == tech_id)
            .order_by(TechnicianCertification.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, cert_id: uuid.UUID, tech_id: uuid.UUID) -> TechnicianCertification | None:
        result = await self._session.execute(
            select(TechnicianCertification).where(
                and_(
                    TechnicianCertification.id == cert_id,
                    TechnicianCertification.technician_id == tech_id,
                )
            )
        )
        return result.scalar_one_or_none()


class TechnicianAvailabilityRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict) -> TechnicianAvailability:
        avail = TechnicianAvailability(**data)
        self._session.add(avail)
        await self._session.flush()
        await self._session.refresh(avail)
        return avail

    async def list_for_technician(self, tech_id: uuid.UUID) -> list[TechnicianAvailability]:
        result = await self._session.execute(
            select(TechnicianAvailability)
            .where(TechnicianAvailability.technician_id == tech_id)
            .order_by(TechnicianAvailability.start_dt)
        )
        return list(result.scalars().all())
