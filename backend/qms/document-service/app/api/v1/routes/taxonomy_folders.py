"""Document Service — Taxonomy and Folder API routes (§7.1)."""

from uuid import uuid4
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from rainer_auth_lib.dependencies import CurrentUser, require_permission
from rainer_auth_lib.permissions import Permission
from rainer_common.exceptions import NotFoundError, RainerException
from rainer_common.responses import MessageResponse, SuccessResponse

from ....core.database import get_db
from ....infra.db.repositories import FolderRepository, TaxonomyRepository
from ....schemas.requests import CreateFolderRequest, CreateTaxonomyRequest, UpdateFolderRequest, UpdateTaxonomyRequest
from ....schemas.responses import FolderResponse, TaxonomyResponse

router = APIRouter(prefix="/taxonomies", tags=["Taxonomies & Folders"])
logger = structlog.get_logger(__name__)


def _get_taxonomy_repo(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaxonomyRepository:
    return TaxonomyRepository(db)


def _get_folder_repo(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> FolderRepository:
    return FolderRepository(db)


# ── Taxonomy CRUD ───────────────────────────────────────────────────────────

@router.get("",
            response_model=SuccessResponse[list[TaxonomyResponse]],
            dependencies=[Depends(require_permission(Permission.DOCUMENT_READ))],
            summary="List taxonomies")
async def list_taxonomies(
    current_user: CurrentUser,
    repo: Annotated[TaxonomyRepository, Depends(_get_taxonomy_repo)],
) -> SuccessResponse[list[TaxonomyResponse]]:
    rows = await repo.list(current_user.tenant_id or "")
    return SuccessResponse.of(
        [TaxonomyResponse.model_validate(r, from_attributes=True) for r in rows]
    )


@router.get("/{taxonomy_id}",
            response_model=SuccessResponse[TaxonomyResponse],
            dependencies=[Depends(require_permission(Permission.DOCUMENT_READ))],
            summary="Get taxonomy by ID")
async def get_taxonomy(
    taxonomy_id: str,
    repo: Annotated[TaxonomyRepository, Depends(_get_taxonomy_repo)],
) -> SuccessResponse[TaxonomyResponse]:
    row = await repo.get_by_id(taxonomy_id)
    if not row:
        raise NotFoundError("Taxonomy", taxonomy_id)
    return SuccessResponse.of(TaxonomyResponse.model_validate(row, from_attributes=True))


@router.post("",
            response_model=SuccessResponse[TaxonomyResponse],
            status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(require_permission(Permission.DOCUMENT_WRITE))],
            summary="Create a taxonomy")
async def create_taxonomy(
    payload: CreateTaxonomyRequest,
    current_user: CurrentUser,
    repo: Annotated[TaxonomyRepository, Depends(_get_taxonomy_repo)],
) -> SuccessResponse[TaxonomyResponse]:
    row = await repo.create(
        tenant_id=current_user.tenant_id or "",
        name=payload.name,
        description=payload.description,
        sort_order=payload.sort_order,
        created_by=current_user.sub,
    )
    return SuccessResponse.of(TaxonomyResponse.model_validate(row, from_attributes=True))


@router.patch("/{taxonomy_id}",
              response_model=SuccessResponse[TaxonomyResponse],
              dependencies=[Depends(require_permission(Permission.DOCUMENT_WRITE))],
              summary="Update a taxonomy")
async def update_taxonomy(
    taxonomy_id: str,
    payload: UpdateTaxonomyRequest,
    repo: Annotated[TaxonomyRepository, Depends(_get_taxonomy_repo)],
) -> SuccessResponse[TaxonomyResponse]:
    existing = await repo.get_by_id(taxonomy_id)
    if not existing:
        raise NotFoundError("Taxonomy", taxonomy_id)
    fields = payload.model_dump(exclude_none=True)
    if fields:
        await repo.update(taxonomy_id, **fields)
    row = await repo.get_by_id(taxonomy_id)
    return SuccessResponse.of(TaxonomyResponse.model_validate(row, from_attributes=True))


@router.delete("/{taxonomy_id}",
               response_model=MessageResponse,
               dependencies=[Depends(require_permission(Permission.DOCUMENT_DELETE))],
               summary="Delete a taxonomy")
async def delete_taxonomy(
    taxonomy_id: str,
    repo: Annotated[TaxonomyRepository, Depends(_get_taxonomy_repo)],
) -> MessageResponse:
    existing = await repo.get_by_id(taxonomy_id)
    if not existing:
        raise NotFoundError("Taxonomy", taxonomy_id)
    await repo.delete(taxonomy_id)
    return MessageResponse(message="Taxonomy deleted successfully")


# ── Folder CRUD ─────────────────────────────────────────────────────────────

@router.get("/{taxonomy_id}/folders",
            response_model=SuccessResponse[list[FolderResponse]],
            dependencies=[Depends(require_permission(Permission.DOCUMENT_READ))],
            summary="List folders in a taxonomy")
async def list_folders(
    taxonomy_id: str,
    repo: Annotated[FolderRepository, Depends(_get_folder_repo)],
) -> SuccessResponse[list[FolderResponse]]:
    rows = await repo.list(taxonomy_id)
    return SuccessResponse.of(
        [FolderResponse.model_validate(r, from_attributes=True) for r in rows]
    )


@router.get("/{taxonomy_id}/folders/{folder_id}",
            response_model=SuccessResponse[FolderResponse],
            dependencies=[Depends(require_permission(Permission.DOCUMENT_READ))],
            summary="Get folder by ID")
async def get_folder(
    folder_id: str,
    repo: Annotated[FolderRepository, Depends(_get_folder_repo)],
) -> SuccessResponse[FolderResponse]:
    row = await repo.get_by_id(folder_id)
    if not row:
        raise NotFoundError("Folder", folder_id)
    return SuccessResponse.of(FolderResponse.model_validate(row, from_attributes=True))


@router.post("/{taxonomy_id}/folders",
             response_model=SuccessResponse[FolderResponse],
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_permission(Permission.DOCUMENT_WRITE))],
             summary="Create a folder in a taxonomy")
async def create_folder(
    taxonomy_id: str,
    payload: CreateFolderRequest,
    current_user: CurrentUser,
    repo: Annotated[FolderRepository, Depends(_get_folder_repo)],
) -> SuccessResponse[FolderResponse]:
    row = await repo.create(
        tenant_id=current_user.tenant_id or "",
        taxonomy_id=taxonomy_id,
        name=payload.name,
        parent_id=payload.parent_id,
        description=payload.description,
        path=payload.path,
        sort_order=payload.sort_order,
        created_by=current_user.sub,
    )
    return SuccessResponse.of(FolderResponse.model_validate(row, from_attributes=True))


@router.patch("/{taxonomy_id}/folders/{folder_id}",
              response_model=SuccessResponse[FolderResponse],
              dependencies=[Depends(require_permission(Permission.DOCUMENT_WRITE))],
              summary="Update a folder")
async def update_folder(
    folder_id: str,
    payload: UpdateFolderRequest,
    repo: Annotated[FolderRepository, Depends(_get_folder_repo)],
) -> SuccessResponse[FolderResponse]:
    existing = await repo.get_by_id(folder_id)
    if not existing:
        raise NotFoundError("Folder", folder_id)
    fields = payload.model_dump(exclude_none=True)
    if fields:
        await repo.update(folder_id, **fields)
    row = await repo.get_by_id(folder_id)
    return SuccessResponse.of(FolderResponse.model_validate(row, from_attributes=True))


@router.delete("/{taxonomy_id}/folders/{folder_id}",
               response_model=MessageResponse,
               dependencies=[Depends(require_permission(Permission.DOCUMENT_DELETE))],
               summary="Delete a folder")
async def delete_folder(
    folder_id: str,
    repo: Annotated[FolderRepository, Depends(_get_folder_repo)],
) -> MessageResponse:
    existing = await repo.get_by_id(folder_id)
    if not existing:
        raise NotFoundError("Folder", folder_id)
    await repo.delete(folder_id)
    return MessageResponse(message="Folder deleted successfully")
