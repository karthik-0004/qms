"""Equipment Service — Equipment asset management API routes."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from rainer_auth_lib.dependencies import CurrentUser, require_permission
from rainer_auth_lib.permissions import Permission
from rainer_common.responses import MessageResponse, PaginatedResponse, SuccessResponse
from rainer_common.pagination import PaginationParams, pagination_params

from ....core.database import get_db
from ....domain.services import EquipmentDomainService
from ....infra.db.repositories import EquipmentRepository
from ....schemas.requests import (
    CreateEquipmentRequest,
    DecommissionRequest,
    RecordCalibrationRequest,
    UpdateEquipmentRequest,
)
from ....schemas.responses import CalibrationRecordResponse, EquipmentResponse

router = APIRouter(prefix="/equipment", tags=["Equipment"])
logger = structlog.get_logger(__name__)


def _get_service(current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]) -> EquipmentDomainService:
    return EquipmentDomainService(repo=EquipmentRepository(db), tenant_id=current_user.tenant_id or "")


@router.get("", response_model=PaginatedResponse[EquipmentResponse],
            dependencies=[Depends(require_permission(Permission.EQUIPMENT_READ))],
            summary="List equipment assets")
async def list_equipment(
    current_user: CurrentUser,
    service: Annotated[EquipmentDomainService, Depends(_get_service)],
    pagination: Annotated[PaginationParams, Depends(pagination_params)],
    status: str | None = Query(default=None),
    equipment_type: str | None = Query(default=None),
    department: str | None = Query(default=None),
    requires_calibration: bool | None = Query(default=None),
) -> PaginatedResponse[EquipmentResponse]:
    items, total = await service.list_equipment(
        status=status, equipment_type=equipment_type,
        department=department, requires_calibration=requires_calibration,
        page=pagination.page, page_size=pagination.page_size,
    )
    return PaginatedResponse.of(
        data=[EquipmentResponse.model_validate(e, from_attributes=True) for e in items],
        page=pagination.page, page_size=pagination.page_size, total=total,
    )


@router.post("", response_model=SuccessResponse[EquipmentResponse], status_code=201,
             dependencies=[Depends(require_permission(Permission.EQUIPMENT_WRITE))],
             summary="Register equipment asset")
async def create_equipment(
    payload: CreateEquipmentRequest,
    current_user: CurrentUser,
    service: Annotated[EquipmentDomainService, Depends(_get_service)],
) -> SuccessResponse[EquipmentResponse]:
    fields = payload.model_dump(exclude={"asset_tag", "name", "equipment_type"})
    equipment = await service.create_equipment(
        asset_tag=payload.asset_tag,
        name=payload.name,
        equipment_type=payload.equipment_type,
        created_by=current_user.sub,
        **fields,
    )
    return SuccessResponse.of(EquipmentResponse.model_validate(equipment, from_attributes=True))


@router.get("/due-for-calibration", response_model=SuccessResponse[list[EquipmentResponse]],
            dependencies=[Depends(require_permission(Permission.EQUIPMENT_READ))],
            summary="Get equipment due for calibration")
async def due_for_calibration(
    current_user: CurrentUser,
    service: Annotated[EquipmentDomainService, Depends(_get_service)],
    days_ahead: int = Query(default=30, ge=1, le=365),
) -> SuccessResponse[list[EquipmentResponse]]:
    items = await service.get_due_for_calibration(days_ahead=days_ahead)
    return SuccessResponse.of([EquipmentResponse.model_validate(e, from_attributes=True) for e in items])


@router.get("/{equipment_id}", response_model=SuccessResponse[EquipmentResponse],
            dependencies=[Depends(require_permission(Permission.EQUIPMENT_READ))],
            summary="Get equipment details")
async def get_equipment(
    equipment_id: str,
    current_user: CurrentUser,
    service: Annotated[EquipmentDomainService, Depends(_get_service)],
) -> SuccessResponse[EquipmentResponse]:
    equipment = await service.get_equipment(equipment_id)
    return SuccessResponse.of(EquipmentResponse.model_validate(equipment, from_attributes=True))


@router.patch("/{equipment_id}", response_model=SuccessResponse[EquipmentResponse],
              dependencies=[Depends(require_permission(Permission.EQUIPMENT_WRITE))],
              summary="Update equipment")
async def update_equipment(
    equipment_id: str,
    payload: UpdateEquipmentRequest,
    current_user: CurrentUser,
    service: Annotated[EquipmentDomainService, Depends(_get_service)],
) -> SuccessResponse[EquipmentResponse]:
    fields = payload.model_dump(exclude_none=True)
    equipment = await service.update_equipment(equipment_id, updated_by=current_user.sub, **fields)
    return SuccessResponse.of(EquipmentResponse.model_validate(equipment, from_attributes=True))


@router.post("/{equipment_id}/calibrate", response_model=SuccessResponse[EquipmentResponse],
             dependencies=[Depends(require_permission(Permission.EQUIPMENT_WRITE))],
             summary="Record equipment calibration")
async def record_calibration(
    equipment_id: str,
    payload: RecordCalibrationRequest,
    current_user: CurrentUser,
    service: Annotated[EquipmentDomainService, Depends(_get_service)],
) -> SuccessResponse[EquipmentResponse]:
    equipment = await service.record_calibration(
        equipment_id=equipment_id,
        calibrated_by=current_user.sub,
        calibration_date=payload.calibration_date,
        passed=payload.passed,
        certificate_file_id=payload.certificate_file_id,
        notes=payload.notes,
    )
    return SuccessResponse.of(EquipmentResponse.model_validate(equipment, from_attributes=True))


@router.post("/{equipment_id}/decommission", response_model=SuccessResponse[EquipmentResponse],
             dependencies=[Depends(require_permission(Permission.EQUIPMENT_WRITE))],
             summary="Decommission equipment")
async def decommission(
    equipment_id: str,
    payload: DecommissionRequest,
    current_user: CurrentUser,
    service: Annotated[EquipmentDomainService, Depends(_get_service)],
) -> SuccessResponse[EquipmentResponse]:
    equipment = await service.decommission(
        equipment_id=equipment_id,
        decommissioned_by=current_user.sub,
        reason=payload.reason,
    )
    return SuccessResponse.of(EquipmentResponse.model_validate(equipment, from_attributes=True))


@router.get("/{equipment_id}/calibrations", response_model=SuccessResponse[list[CalibrationRecordResponse]],
            dependencies=[Depends(require_permission(Permission.EQUIPMENT_READ))],
            summary="List calibration history for equipment")
async def list_calibration_records(
    equipment_id: str,
    current_user: CurrentUser,
    service: Annotated[EquipmentDomainService, Depends(_get_service)],
) -> SuccessResponse[list[CalibrationRecordResponse]]:
    records = await service.list_calibration_records(equipment_id)
    return SuccessResponse.of(
        [CalibrationRecordResponse.model_validate(r, from_attributes=True) for r in records]
    )


@router.delete("/{equipment_id}", response_model=MessageResponse,
               dependencies=[Depends(require_permission(Permission.EQUIPMENT_WRITE))],
               summary="Delete equipment")
async def delete_equipment(
    equipment_id: str,
    current_user: CurrentUser,
    service: Annotated[EquipmentDomainService, Depends(_get_service)],
) -> MessageResponse:
    await service.delete_equipment(equipment_id, deleted_by=current_user.sub)
    return MessageResponse(message="Equipment deleted successfully")
