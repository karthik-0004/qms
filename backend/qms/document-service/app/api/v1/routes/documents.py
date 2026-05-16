"""Document Service — Document lifecycle API routes."""

from datetime import datetime, timezone
from uuid import uuid4
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from rainer_auth_lib.dependencies import CurrentUser, require_permission
from rainer_auth_lib.permissions import Permission
from rainer_common.exceptions import RainerException
from rainer_common.responses import MessageResponse, PaginatedResponse, SuccessResponse
from rainer_common.pagination import PaginationParams, pagination_params

from ....core.config import Settings, get_settings
from ....core.database import get_db
from ....domain.services import DocumentDomainService
from ....events.publisher import publish_controlled_copy_issued, publish_controlled_copy_recalled
from ....infra.db.repositories import (
    AcknowledgmentRepository,
    ControlledCopyRepository,
    DocumentDistributionRepository,
    DocumentRepository,
    DocumentVersionRepository,
)
from ....schemas.requests import (
    AcknowledgeDocumentRequest,
    AddDistributionMemberRequest,
    ApproveDocumentRequest,
    CreateDocumentRequest,
    CreateVersionRequest,
    IssueControlledCopyRequest,
    RejectDocumentRequest,
    SaveContentRequest,
    SubmitForReviewRequest,
    UpdateDocumentRequest,
)
from ....schemas.responses import (
    ComplianceStatsResponse,
    ContentResponse,
    ControlledCopyResponse,
    DocumentAcknowledgmentResponse,
    DocumentDistributionResponse,
    DocumentResponse,
    DocumentVersionResponse,
    PendingAcknowledgmentResponse,
)

router = APIRouter(prefix="/documents", tags=["Documents"])
logger = structlog.get_logger(__name__)


def _get_service(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DocumentDomainService:
    if not getattr(current_user, "tenant_id", None):
        raise RainerException(
            code="TENANT_REQUIRED",
            message="Tenant context is required. Provide a tenant-scoped token or X-Tenant-ID header.",
            status_code=400,
        )
    return DocumentDomainService(
        doc_repo=DocumentRepository(db),
        version_repo=DocumentVersionRepository(db),
        distribution_repo=DocumentDistributionRepository(db),
        ack_repo=AcknowledgmentRepository(db),
        tenant_id=current_user.tenant_id or "",
    )


@router.get("", response_model=PaginatedResponse[DocumentResponse],
            dependencies=[Depends(require_permission(Permission.DOCUMENT_READ))],
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
    taxonomy_id: str | None = Query(default=None),
    folder_id: str | None = Query(default=None),
) -> PaginatedResponse[DocumentResponse]:
    docs, total = await service.list_documents(
        status=status, doc_type=doc_type, department=department,
        owner_id=owner_id, search=search,
        taxonomy_id=taxonomy_id, folder_id=folder_id,
        page=pagination.page, page_size=pagination.page_size,
    )
    return PaginatedResponse.of(
        data=[DocumentResponse.model_validate(d, from_attributes=True) for d in docs],
        page=pagination.page, page_size=pagination.page_size, total=total,
    )


@router.get("/due-for-review",
            response_model=SuccessResponse[list[DocumentResponse]],
            dependencies=[Depends(require_permission(Permission.DOCUMENT_READ))],
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


@router.post("", response_model=SuccessResponse[DocumentResponse], status_code=201,
             dependencies=[Depends(require_permission(Permission.DOCUMENT_WRITE))],
             summary="Create a new document")
async def create_document(
    payload: CreateDocumentRequest,
    current_user: CurrentUser,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> SuccessResponse[DocumentResponse]:
    doc_number = payload.doc_number
    if not doc_number:
        now = datetime.now(timezone.utc)
        doc_number = f"{settings.document_number_prefix}-{now:%Y%m%d}-{uuid4().hex[:8].upper()}"
    doc = await service.create_document(
        doc_number=doc_number,
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
            dependencies=[Depends(require_permission(Permission.DOCUMENT_READ))],
            summary="Get document details")
async def get_document(
    document_id: str,
    current_user: CurrentUser,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
) -> SuccessResponse[DocumentResponse]:
    doc = await service.get_document(document_id)
    return SuccessResponse.of(DocumentResponse.model_validate(doc, from_attributes=True))


@router.patch("/{document_id}", response_model=SuccessResponse[DocumentResponse],
              dependencies=[Depends(require_permission(Permission.DOCUMENT_WRITE))],
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
               dependencies=[Depends(require_permission(Permission.DOCUMENT_DELETE))],
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
             dependencies=[Depends(require_permission(Permission.DOCUMENT_WRITE))],
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
             dependencies=[Depends(require_permission(Permission.DOCUMENT_APPROVE))],
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
             dependencies=[Depends(require_permission(Permission.DOCUMENT_APPROVE))],
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


@router.post("/{document_id}/make-effective",
             response_model=SuccessResponse[DocumentResponse],
             dependencies=[Depends(require_permission(Permission.DOCUMENT_APPROVE))],
             summary="Release approved document to effective status")
async def make_effective(
    document_id: str,
    current_user: CurrentUser,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
) -> SuccessResponse[DocumentResponse]:
    doc = await service.make_effective(document_id, updated_by=current_user.sub)
    return SuccessResponse.of(DocumentResponse.model_validate(doc, from_attributes=True))


@router.post("/{document_id}/make-superseded",
             response_model=SuccessResponse[DocumentResponse],
             dependencies=[Depends(require_permission(Permission.DOCUMENT_APPROVE))],
             summary="Mark effective document as superseded")
async def make_superseded(
    document_id: str,
    current_user: CurrentUser,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
) -> SuccessResponse[DocumentResponse]:
    doc = await service.make_superseded(document_id, updated_by=current_user.sub)
    return SuccessResponse.of(DocumentResponse.model_validate(doc, from_attributes=True))


@router.post("/{document_id}/make-obsolete",
             response_model=SuccessResponse[DocumentResponse],
             dependencies=[Depends(require_permission(Permission.DOCUMENT_APPROVE))],
             summary="Mark a document as obsolete")
async def make_obsolete(
    document_id: str,
    current_user: CurrentUser,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
) -> SuccessResponse[DocumentResponse]:
    doc = await service.make_obsolete(document_id, updated_by=current_user.sub)
    return SuccessResponse.of(DocumentResponse.model_validate(doc, from_attributes=True))


@router.get("/{document_id}/versions",
             response_model=SuccessResponse[list[DocumentVersionResponse]],
             dependencies=[Depends(require_permission(Permission.DOCUMENT_READ))],
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


@router.post("/{document_id}/versions",
             response_model=SuccessResponse[DocumentResponse],
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_permission(Permission.DOCUMENT_WRITE))],
             summary="Create a new version of an approved/effective document")
async def create_version(
    document_id: str,
    payload: CreateVersionRequest,
    current_user: CurrentUser,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
) -> SuccessResponse[DocumentResponse]:
    doc = await service.create_new_version(
        document_id=document_id,
        change_type=payload.change_type,
        change_summary=payload.change_summary,
        created_by=current_user.sub,
        new_file_id=payload.file_id,
    )
    return SuccessResponse.of(DocumentResponse.model_validate(doc, from_attributes=True))


@router.get("/{document_id}/distribution",
            response_model=SuccessResponse[list[DocumentDistributionResponse]],
            dependencies=[Depends(require_permission(Permission.DOCUMENT_READ))],
            summary="List distribution recipients for a document")
async def list_distribution(
    document_id: str,
    current_user: CurrentUser,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
) -> SuccessResponse[list[DocumentDistributionResponse]]:
    rows = await service.list_distribution(document_id)
    return SuccessResponse.of(
        [DocumentDistributionResponse.model_validate(r, from_attributes=True) for r in rows]
    )


@router.post("/{document_id}/distribution",
             response_model=SuccessResponse[DocumentDistributionResponse],
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_permission(Permission.DOCUMENT_WRITE))],
             summary="Add a user to the document distribution list")
async def add_distribution_member(
    document_id: str,
    payload: AddDistributionMemberRequest,
    current_user: CurrentUser,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
) -> SuccessResponse[DocumentDistributionResponse]:
    row = await service.add_distribution_member(
        document_id=document_id,
        user_id=payload.user_id,
        added_by=current_user.sub,
    )
    return SuccessResponse.of(DocumentDistributionResponse.model_validate(row, from_attributes=True))


# ── User-scoped acknowledgment endpoints ──────────────────────────────────

@router.get("/me/acknowledgments/pending",
             response_model=SuccessResponse[list[PendingAcknowledgmentResponse]],
             dependencies=[Depends(require_permission(Permission.DOCUMENT_READ))],
             summary="Get current user's pending document acknowledgments")
async def my_pending_acknowledgments(
    current_user: CurrentUser,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
) -> SuccessResponse[list[PendingAcknowledgmentResponse]]:
    pending = await service.get_my_pending_acknowledgments(user_id=current_user.sub)
    return SuccessResponse.of(
        [PendingAcknowledgmentResponse(**p) for p in pending]
    )


# ── Document Acknowledgment (D-3) ─────────────────────────────────────────

@router.post("/{document_id}/acknowledge",
             response_model=SuccessResponse[DocumentAcknowledgmentResponse],
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_permission(Permission.DOCUMENT_WRITE))],
             summary="Acknowledge a document (ISO 17025 compliance)")
async def acknowledge_document(
    document_id: str,
    payload: AcknowledgeDocumentRequest,
    current_user: CurrentUser,
    request: Request,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
) -> SuccessResponse[DocumentAcknowledgmentResponse]:
    ip_address = payload.ip_address or request.client.host if request.client else None
    ack = await service.acknowledge_document(
        document_id=document_id,
        user_id=current_user.sub,
        signature=payload.signature,
        ip_address=ip_address,
    )
    return SuccessResponse.of(DocumentAcknowledgmentResponse.model_validate(ack, from_attributes=True))


@router.get("/{document_id}/acknowledgments",
            response_model=SuccessResponse[list[DocumentAcknowledgmentResponse]],
            dependencies=[Depends(require_permission(Permission.DOCUMENT_READ))],
            summary="List acknowledgments for a document")
async def list_acknowledgments(
    document_id: str,
    current_user: CurrentUser,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
) -> SuccessResponse[list[DocumentAcknowledgmentResponse]]:
    acks = await service.list_acknowledgments(document_id)
    return SuccessResponse.of(
        [DocumentAcknowledgmentResponse.model_validate(a, from_attributes=True) for a in acks]
    )


@router.get("/{document_id}/acknowledgments/compliance",
            response_model=SuccessResponse[ComplianceStatsResponse],
            dependencies=[Depends(require_permission(Permission.DOCUMENT_READ))],
            summary="Get acknowledgment compliance stats for a document")
async def acknowledgment_compliance(
    document_id: str,
    current_user: CurrentUser,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
) -> SuccessResponse[ComplianceStatsResponse]:
    stats = await service.get_acknowledgment_compliance_stats(document_id)
    return SuccessResponse.of(ComplianceStatsResponse(**stats))


# ── Editor content (Mode A: §4.4) ───────────────────────────────────────────

@router.get("/{document_id}/content",
            response_model=SuccessResponse[ContentResponse],
            dependencies=[Depends(require_permission(Permission.DOCUMENT_READ))],
            summary="Get document editor content")
async def get_content(
    document_id: str,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
) -> SuccessResponse[ContentResponse]:
    doc = await service.get_document(document_id)
    return SuccessResponse.of(ContentResponse(
        authoring_mode=doc.authoring_mode,
        content_ast=doc.content_ast,
        html_snapshot=doc.html_snapshot,
        editor_nonce=doc.editor_nonce,
    ))


@router.post("/{document_id}/content",
             response_model=SuccessResponse[ContentResponse],
             dependencies=[Depends(require_permission(Permission.DOCUMENT_WRITE))],
             summary="Save document editor content")
async def save_content(
    document_id: str,
    payload: SaveContentRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[DocumentDomainService, Depends(_get_service)],
) -> SuccessResponse[ContentResponse]:
    from ....infra.db.repositories import DocumentRepository

    doc = await service.get_document(document_id)
    if doc.status != "draft":
        from rainer_common.exceptions import ForbiddenError
        raise ForbiddenError("Only draft documents can be edited")

    doc_repo = DocumentRepository(db)
    update_fields: dict = {"authoring_mode": payload.authoring_mode}
    if payload.content_ast is not None:
        import secrets
        update_fields["content_ast"] = payload.content_ast
        update_fields["html_snapshot"] = payload.html_snapshot
        update_fields["editor_nonce"] = secrets.token_hex(32)
    await doc_repo.update(document_id, **update_fields)

    doc = await service.get_document(document_id)
    return SuccessResponse.of(ContentResponse(
        authoring_mode=doc.authoring_mode,
        content_ast=doc.content_ast,
        html_snapshot=doc.html_snapshot,
        editor_nonce=doc.editor_nonce,
    ))


# ── File upload (Mode B: §4.4) ──────────────────────────────────────────────

@router.post("/{document_id}/file",
             response_model=SuccessResponse[dict],
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_permission(Permission.DOCUMENT_WRITE))],
             summary="Upload a file attachment for a document")
async def upload_file(
    document_id: str,
    current_user: CurrentUser,
    request: Request,
    service: Annotated[DocumentDomainService, Depends(_get_service)],
) -> SuccessResponse[dict]:
    doc = await service.get_document(document_id)
    if doc.status != "draft":
        from rainer_common.exceptions import ForbiddenError
        raise ForbiddenError("Only draft documents can accept file uploads")

    from ....infra.db.repositories import DocumentRepository
    form = await request.form()
    file_field = form.get("file")
    if file_field is None or not hasattr(file_field, "read"):
        from rainer_common.exceptions import ValidationError
        raise ValidationError("A file upload with key 'file' is required")

    import io
    file_bytes = await file_field.read()
    filename = getattr(file_field, "filename", "upload.bin")

    # In production, upload to file-service; for now store metadata
    import hashlib
    new_file_id = hashlib.sha256(file_bytes).hexdigest()[:32]

    from sqlalchemy import update as sqla_update
    from ....infra.db.models import Document
    from ....core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        await session.execute(
            sqla_update(Document).where(Document.id == document_id).values(
                file_id=new_file_id, updated_at=datetime.now(timezone.utc),
            )
        )
        await session.commit()

    return SuccessResponse.of({
        "file_id": new_file_id,
        "filename": filename,
        "size_bytes": len(file_bytes),
    })


# ── Controlled Copies (§7.1) ────────────────────────────────────────────────

@router.get("/{document_id}/controlled-copies",
            response_model=SuccessResponse[list[ControlledCopyResponse]],
            dependencies=[Depends(require_permission(Permission.DOCUMENT_READ))],
            summary="List controlled copies for a document")
async def list_controlled_copies(
    document_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SuccessResponse[list[ControlledCopyResponse]]:
    repo = ControlledCopyRepository(db)
    rows = await repo.list_for_document(document_id)
    return SuccessResponse.of(
        [ControlledCopyResponse.model_validate(r, from_attributes=True) for r in rows]
    )


@router.post("/{document_id}/controlled-copies",
             response_model=SuccessResponse[ControlledCopyResponse],
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_permission(Permission.DOCUMENT_WRITE))],
             summary="Issue a controlled copy")
async def issue_controlled_copy(
    document_id: str,
    payload: IssueControlledCopyRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SuccessResponse[ControlledCopyResponse]:
    from ....infra.db.models import Document
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.deleted_at.is_(None))
    )
    doc = result.scalar_one_or_none()
    if not doc:
        from rainer_common.exceptions import NotFoundError
        raise NotFoundError("Document", document_id)

    repo = ControlledCopyRepository(db)
    cc = await repo.create(
        document_id=document_id,
        version=doc.current_version,
        copy_number=payload.copy_number,
        issued_to=payload.issued_to,
        issued_by=current_user.sub,
        notes=payload.notes,
    )
    await publish_controlled_copy_issued(doc, cc, current_user.sub)
    return SuccessResponse.of(ControlledCopyResponse.model_validate(cc, from_attributes=True))


@router.post("/{document_id}/controlled-copies/{copy_id}/recall",
             response_model=SuccessResponse[ControlledCopyResponse],
             dependencies=[Depends(require_permission(Permission.DOCUMENT_WRITE))],
             summary="Recall a controlled copy")
async def recall_controlled_copy(
    document_id: str,
    copy_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SuccessResponse[ControlledCopyResponse]:
    from ....infra.db.models import Document
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.deleted_at.is_(None))
    )
    doc = result.scalar_one_or_none()
    if not doc:
        from rainer_common.exceptions import NotFoundError
        raise NotFoundError("Document", document_id)

    repo = ControlledCopyRepository(db)
    cc = await repo.get_by_id(copy_id)
    if not cc:
        from rainer_common.exceptions import NotFoundError
        raise NotFoundError("ControlledCopy", copy_id)

    await repo.recall(copy_id)
    cc = await repo.get_by_id(copy_id)
    await publish_controlled_copy_recalled(doc, cc, current_user.sub)
    return SuccessResponse.of(ControlledCopyResponse.model_validate(cc, from_attributes=True))
