"""Image Service — Plate image API routes."""

from datetime import datetime
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....domain.services import ImageDomainService
from ....schemas.requests import RegisterImageRequest
from ....schemas.responses import ImageResponse

router = APIRouter(prefix="/images", tags=["Images"])
logger = structlog.get_logger(__name__)

TenantId = Annotated[str, Header(alias="x-tenant-id")]
UserId = Annotated[str, Header(alias="x-user-id")]


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> ImageDomainService:
    return ImageDomainService(db)


@router.get("", response_model=dict, summary="List images (paginated)")
async def list_images(
    tenant_id: TenantId,
    service: Annotated[ImageDomainService, Depends(_get_service)],
    status: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> dict:
    images, total = await service.list_images(
        tenant_id=tenant_id, status=status, offset=offset, limit=limit
    )
    return {
        "data": [ImageResponse.model_validate(i, from_attributes=True) for i in images],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.post("", response_model=ImageResponse, status_code=201, summary="Register a plate image")
async def register_image(
    payload: RegisterImageRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[ImageDomainService, Depends(_get_service)],
) -> ImageResponse:
    image = await service.register_image(
        tenant_id=tenant_id,
        plate_id=payload.plate_id,
        image_key=payload.image_key,
        image_type=payload.image_type,
        captured_at=payload.captured_at,
        uploaded_by=user_id,
        file_size_bytes=payload.file_size_bytes,
        width_px=payload.width_px,
        height_px=payload.height_px,
        resolution_dpi=payload.resolution_dpi,
        magnification=payload.magnification,
        camera_settings=payload.camera_settings,
        is_primary=payload.is_primary,
    )
    return ImageResponse.model_validate(image, from_attributes=True)


@router.get("/{image_id}", response_model=ImageResponse, summary="Get image details")
async def get_image(
    image_id: str,
    tenant_id: TenantId,
    service: Annotated[ImageDomainService, Depends(_get_service)],
) -> ImageResponse:
    image = await service.get_image(image_id)
    return ImageResponse.model_validate(image, from_attributes=True)


@router.post("/{image_id}/set-primary", response_model=ImageResponse, summary="Set image as primary for plate")
async def set_primary(
    image_id: str,
    plate_id: str = Query(...),
    tenant_id: TenantId = None,
    service: Annotated[ImageDomainService, Depends(_get_service)] = None,
) -> ImageResponse:
    image = await service.set_primary(plate_id=plate_id, image_id=image_id)
    return ImageResponse.model_validate(image, from_attributes=True)


@router.delete("/{image_id}", status_code=204, summary="Soft-delete an image")
async def delete_image(
    image_id: str,
    tenant_id: TenantId,
    service: Annotated[ImageDomainService, Depends(_get_service)],
) -> None:
    await service.delete_image(image_id)
