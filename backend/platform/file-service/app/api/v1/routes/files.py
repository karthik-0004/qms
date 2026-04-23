"""File Service — File upload, download, and management API routes."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from rainer_auth_lib.dependencies import CurrentUser
from rainer_common.responses import MessageResponse, PaginatedResponse, SuccessResponse
from rainer_common.pagination import PaginationParams, pagination_params

from ....core.config import Settings, get_settings
from ....core.database import get_db
from ....domain.services import FileDomainService
from ....infra.db.repositories import FileRepository, FileVersionRepository
from ....schemas.responses import FileResponse, FileVersionResponse, DownloadUrlResponse

router = APIRouter(prefix="/files", tags=["Files"])
logger = structlog.get_logger(__name__)


def _get_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> FileDomainService:
    return FileDomainService(
        file_repo=FileRepository(db),
        version_repo=FileVersionRepository(db),
        settings=settings,
    )


@router.post(
    "/upload",
    response_model=SuccessResponse[FileResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload a file",
)
async def upload_file(
    current_user: CurrentUser,
    service: Annotated[FileDomainService, Depends(_get_service)],
    file: UploadFile = File(...),
    entity_type: str | None = Form(default=None),
    entity_id: str | None = Form(default=None),
    module: str | None = Form(default=None),
    is_public: bool = Form(default=False),
) -> SuccessResponse[FileResponse]:
    content = await file.read()
    content_type = file.content_type or "application/octet-stream"
    record = await service.upload_file(
        file_content=content,
        original_filename=file.filename or "upload",
        content_type=content_type,
        tenant_id=current_user.tenant_id,
        uploaded_by=current_user.sub,
        entity_type=entity_type,
        entity_id=entity_id,
        module=module,
        is_public=is_public,
    )
    return SuccessResponse.of(FileResponse.model_validate(record, from_attributes=True))


@router.get(
    "",
    response_model=PaginatedResponse[FileResponse],
    summary="List files (filtered, paginated)",
)
async def list_files(
    current_user: CurrentUser,
    service: Annotated[FileDomainService, Depends(_get_service)],
    pagination: Annotated[PaginationParams, Depends(pagination_params)],
    entity_type: str | None = Query(default=None),
    module: str | None = Query(default=None),
) -> PaginatedResponse[FileResponse]:
    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id
    files, total = await service.list_files(
        tenant_id=tenant_id,
        entity_type=entity_type,
        module=module,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return PaginatedResponse.of(
        data=[FileResponse.model_validate(f, from_attributes=True) for f in files],
        page=pagination.page,
        page_size=pagination.page_size,
        total=total,
    )


@router.get(
    "/{file_id}",
    response_model=SuccessResponse[FileResponse],
    summary="Get file metadata",
)
async def get_file(
    file_id: str,
    current_user: CurrentUser,
    service: Annotated[FileDomainService, Depends(_get_service)],
) -> SuccessResponse[FileResponse]:
    file = await service.get_file(file_id)
    return SuccessResponse.of(FileResponse.model_validate(file, from_attributes=True))


@router.get(
    "/{file_id}/download",
    response_model=SuccessResponse[DownloadUrlResponse],
    summary="Get presigned download URL for a file",
)
async def get_download_url(
    file_id: str,
    current_user: CurrentUser,
    service: Annotated[FileDomainService, Depends(_get_service)],
    expires_in: int = Query(default=3600, ge=60, le=86400),
) -> SuccessResponse[DownloadUrlResponse]:
    url = await service.get_download_url(file_id, expires_in_seconds=expires_in)
    return SuccessResponse.of(DownloadUrlResponse(file_id=file_id, url=url, expires_in=expires_in))


@router.get(
    "/{file_id}/versions",
    response_model=SuccessResponse[list[FileVersionResponse]],
    summary="Get version history of a file",
)
async def get_versions(
    file_id: str,
    current_user: CurrentUser,
    service: Annotated[FileDomainService, Depends(_get_service)],
) -> SuccessResponse[list[FileVersionResponse]]:
    versions = await service.get_versions(file_id)
    return SuccessResponse.of(
        [FileVersionResponse.model_validate(v, from_attributes=True) for v in versions]
    )


@router.post(
    "/{file_id}/versions",
    response_model=SuccessResponse[FileResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new version of a file",
)
async def upload_version(
    file_id: str,
    current_user: CurrentUser,
    service: Annotated[FileDomainService, Depends(_get_service)],
    file: UploadFile = File(...),
    comment: str | None = Form(default=None),
) -> SuccessResponse[FileResponse]:
    content = await file.read()
    updated_file, _ = await service.upload_new_version(
        file_id=file_id,
        file_content=content,
        uploaded_by=current_user.sub,
        comment=comment,
    )
    return SuccessResponse.of(FileResponse.model_validate(updated_file, from_attributes=True))


@router.delete(
    "/{file_id}",
    response_model=MessageResponse,
    summary="Soft-delete a file",
)
async def delete_file(
    file_id: str,
    current_user: CurrentUser,
    service: Annotated[FileDomainService, Depends(_get_service)],
) -> MessageResponse:
    await service.delete_file(file_id)
    return MessageResponse(message="File deleted successfully")
