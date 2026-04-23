"""Plate Service — Plate registry API routes."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....domain.services import PlateDomainService
from ....schemas.requests import RegisterPlateRequest, TransitionStatusRequest
from ....schemas.responses import PlateResponse, PlateStatusHistoryResponse

router = APIRouter(prefix="/plates", tags=["Plates"])
logger = structlog.get_logger(__name__)

TenantId = Annotated[str, Header(alias="x-tenant-id")]
UserId = Annotated[str, Header(alias="x-user-id")]


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> PlateDomainService:
    return PlateDomainService(db)


@router.get("", response_model=dict, summary="List plates (paginated)")
async def list_plates(
    tenant_id: TenantId,
    service: Annotated[PlateDomainService, Depends(_get_service)],
    status: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> dict:
    plates, total = await service._repo.list_by_tenant(
        tenant_id=tenant_id, status=status, offset=offset, limit=limit
    )
    return {
        "data": [PlateResponse.model_validate(p, from_attributes=True) for p in plates],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.post("", response_model=PlateResponse, status_code=201, summary="Register a new plate")
async def register_plate(
    payload: RegisterPlateRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[PlateDomainService, Depends(_get_service)],
) -> PlateResponse:
    plate = await service.register_plate(
        tenant_id=tenant_id,
        barcode=payload.barcode,
        sample_type=payload.sample_type,
        media_type=payload.media_type,
        created_by=user_id,
        location_code=payload.location_code,
        lot_number=payload.lot_number,
        notes=payload.notes,
        incubation_temp_celsius=payload.incubation_temp_celsius,
        incubation_hours=payload.incubation_hours,
        metadata=payload.metadata,
    )
    return PlateResponse.model_validate(plate, from_attributes=True)


@router.get("/{plate_id}", response_model=PlateResponse, summary="Get plate details")
async def get_plate(
    plate_id: str,
    tenant_id: TenantId,
    service: Annotated[PlateDomainService, Depends(_get_service)],
) -> PlateResponse:
    plate = await service.get_plate(plate_id=plate_id, tenant_id=tenant_id)
    return PlateResponse.model_validate(plate, from_attributes=True)


@router.post("/{plate_id}/status", response_model=PlateResponse, summary="Transition plate status")
async def transition_status(
    plate_id: str,
    payload: TransitionStatusRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[PlateDomainService, Depends(_get_service)],
) -> PlateResponse:
    plate = await service.transition_status(
        plate_id=plate_id,
        tenant_id=tenant_id,
        new_status=payload.new_status,
        changed_by=user_id,
        reason=payload.reason,
    )
    return PlateResponse.model_validate(plate, from_attributes=True)


@router.get("/{plate_id}/history", response_model=list[PlateStatusHistoryResponse],
            summary="Get plate status history")
async def get_history(
    plate_id: str,
    tenant_id: TenantId,
    service: Annotated[PlateDomainService, Depends(_get_service)],
) -> list[PlateStatusHistoryResponse]:
    history = await service.get_history(plate_id=plate_id, tenant_id=tenant_id)
    return [PlateStatusHistoryResponse.model_validate(h, from_attributes=True) for h in history]
