"""Document Service — Document lifecycle API routes."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from rainer_auth_lib.dependencies import CurrentUser
from rainer_common.responses import MessageResponse, PaginatedResponse, SuccessResponse
from rainer_common.pagination import PaginationParams, pagination_params

from ....core.config import Settings, get_settings
from ....core.database import get_db
from ....domain.services import DocumentDomainService
from ....infra.db.repositories import DocumentRepository, DocumentVersionRepository
from ....schemas.requests import (
    ApproveDocumentRequest,
    CreateDocumentRequest,
    RejectDocumentRequest,
    SubmitForReviewRequest,
    UpdateDocumentRequest,
)
from ....schemas.responses import DocumentResponse, DocumentVersionResponse

router = APIRouter(prefix="/documents", tags=["Documents"])
logger = structlog.get_logger(__name__)


def _get_service(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DocumentDomainService:
    return DocumentDomainService(
        doc_repo=DocumentRepository(db),
        version_repo=DocumentVersionRepository(db),
        tenant_id=current_user.tenant_id or "",
    )


@router.get("", response_model=PaginatedResponse[DocumentResponse],
            summary="List documents (filtered, paginated)")
async def list_documents(
    current_user: CurrentUser,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
    pagination: Annotated[PaginationParams, Depends(pagination_params)],
    status: str | None = Query(default=None),
    doc_type: str | None = Query(default=None),
    department: str | None = Query(default=None),
    owner_id: str | None = Query(default=None),
    search: str | None = Query(default=None),
) -> PaginatedResponse[DocumentResponse]:
    docs, total = await service.list_documents(
        status=status, doc_type=doc_type, department=department,
        owner_id=owner_id, search=search,
        page=pagination.page, page_size=pagination.page_size,
    )
    return PaginatedResponse.of(
        data=[DocumentResponse.model_validate(d, from_attributes=True) for d in docs],
        page=pagination.page, page_size=pagination.page_size, total=total,
    )


@router.post("", response_model=SuccessResponse[DocumentResponse], status_code=201,
             summary="Create a new document")
async def create_document(
    payload: CreateDocumentRequest,
    current_user: CurrentUser,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
) -> SuccessResponse[DocumentResponse]:
    doc = await service.create_document(
        doc_number=payload.doc_number,
        title=payload.title,
        doc_type=payload.doc_type,
        created_by=current_user.sub,
        description=payload.description,
        department=payload.department,
        owner_id=payload.owner_id,
        tags=payload.tags,
        regulatory_frameworks=payload.regulatory_frameworks,
        file_id=payload.file_id,
    )
    return SuccessResponse.of(DocumentResponse.model_validate(doc, from_attributes=True))


@router.get("/{document_id}", response_model=SuccessResponse[DocumentResponse],
            summary="Get document details")
async def get_document(
    document_id: str,
    current_user: CurrentUser,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
) -> SuccessResponse[DocumentResponse]:
    doc = await service.get_document(document_id)
    return SuccessResponse.of(DocumentResponse.model_validate(doc, from_attributes=True))


@router.patch("/{document_id}", response_model=SuccessResponse[DocumentResponse],
              summary="Update draft document")
async def update_document(
    document_id: str,
    payload: UpdateDocumentRequest,
    current_user: CurrentUser,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
) -> SuccessResponse[DocumentResponse]:
    fields = payload.model_dump(exclude_none=True)
    doc = await service.update_document(document_id, updated_by=current_user.sub, **fields)
    return SuccessResponse.of(DocumentResponse.model_validate(doc, from_attributes=True))


@router.delete("/{document_id}", response_model=MessageResponse,
               summary="Delete a draft document")
async def delete_document(
    document_id: str,
    current_user: CurrentUser,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
) -> MessageResponse:
    await service.delete_document(document_id, deleted_by=current_user.sub)
    return MessageResponse(message="Document deleted successfully")


@router.post("/{document_id}/submit-for-review",
             response_model=SuccessResponse[DocumentResponse],
             summary="Submit document for approval review")
async def submit_for_review(
    document_id: str,
    payload: SubmitForReviewRequest,
    current_user: CurrentUser,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
) -> SuccessResponse[DocumentResponse]:
    doc = await service.submit_for_review(
        document_id=document_id,
        submitted_by=current_user.sub,
        approver_id=payload.approver_id,
        comment=payload.comment,
    )
    return SuccessResponse.of(DocumentResponse.model_validate(doc, from_attributes=True))


@router.post("/{document_id}/approve",
             response_model=SuccessResponse[DocumentResponse],
             summary="Approve document (requires e-signature)")
async def approve_document(
    document_id: str,
    payload: ApproveDocumentRequest,
    current_user: CurrentUser,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
) -> SuccessResponse[DocumentResponse]:
    doc = await service.approve_document(
        document_id=document_id,
        approved_by=current_user.sub,
        signature=payload.signature,
        comment=payload.comment,
        effective_date=payload.effective_date,
        review_date=payload.review_date,
    )
    return SuccessResponse.of(DocumentResponse.model_validate(doc, from_attributes=True))


@router.post("/{document_id}/reject",
             response_model=SuccessResponse[DocumentResponse],
             summary="Reject document (returns to draft)")
async def reject_document(
    document_id: str,
    payload: RejectDocumentRequest,
    current_user: CurrentUser,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
) -> SuccessResponse[DocumentResponse]:
    doc = await service.reject_document(
        document_id=document_id,
        rejected_by=current_user.sub,
        reason=payload.reason,
    )
    return SuccessResponse.of(DocumentResponse.model_validate(doc, from_attributes=True))


@router.post("/{document_id}/make-obsolete",
             response_model=SuccessResponse[DocumentResponse],
             summary="Mark approved document as obsolete")
async def make_obsolete(
    document_id: str,
    current_user: CurrentUser,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
) -> SuccessResponse[DocumentResponse]:
    doc = await service.make_obsolete(document_id, updated_by=current_user.sub)
    return SuccessResponse.of(DocumentResponse.model_validate(doc, from_attributes=True))


@router.get("/{document_id}/versions",
            response_model=SuccessResponse[list[DocumentVersionResponse]],
            summary="Get document version history")
async def get_versions(
    document_id: str,
    current_user: CurrentUser,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
) -> SuccessResponse[list[DocumentVersionResponse]]:
    versions = await service.get_versions(document_id)
    return SuccessResponse.of(
        [DocumentVersionResponse.model_validate(v, from_attributes=True) for v in versions]
    )


@router.get("/due-for-review",
            response_model=SuccessResponse[list[DocumentResponse]],
            summary="Get documents due for periodic review")
async def due_for_review(
    current_user: CurrentUser,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
    days_ahead: int = Query(default=30, ge=1, le=365),
) -> SuccessResponse[list[DocumentResponse]]:
    docs = await service.get_due_for_review(days_ahead=days_ahead)
    return SuccessResponse.of(
        [DocumentResponse.model_validate(d, from_attributes=True) for d in docs]
    )
