"""Notification Service — API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from rainer_auth_lib.dependencies import CurrentUser, require_role
from rainer_common.responses import MessageResponse, SuccessResponse

from ....core.config import Settings, get_settings
from ....core.database import get_db
from ....domain.services import NotificationDomainService
from ....infra.db.repositories import NotificationLogRepository, NotificationTemplateRepository

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def _get_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> NotificationDomainService:
    return NotificationDomainService(
        template_repo=NotificationTemplateRepository(db),
        log_repo=NotificationLogRepository(db),
        settings=settings,
    )


class SendEmailRequest(BaseModel):
    recipient_email: EmailStr
    subject: str
    body_html: str
    body_text: str | None = None
    tenant_id: str | None = None
    user_id: str | None = None
    template_name: str | None = None


class SendFromTemplateRequest(BaseModel):
    template_name: str
    recipient_email: EmailStr
    variables: dict = {}
    tenant_id: str | None = None
    user_id: str | None = None


class CreateTemplateRequest(BaseModel):
    name: str
    subject: str
    body_html: str
    body_text: str | None = None
    channel: str = "email"
    variables: list[str] = []


@router.post("/send-email", response_model=MessageResponse, status_code=200,
             summary="Send email notification (internal)")
async def send_email(
    payload: SendEmailRequest,
    current_user: CurrentUser,
    service: Annotated[NotificationDomainService, Depends(_get_service)],
) -> MessageResponse:
    await service.send_email(
        recipient_email=payload.recipient_email,
        subject=payload.subject,
        body_html=payload.body_html,
        body_text=payload.body_text,
        tenant_id=payload.tenant_id,
        user_id=payload.user_id,
        template_name=payload.template_name,
    )
    return MessageResponse(message="Email queued for delivery")


@router.post("/send-from-template", response_model=MessageResponse, status_code=200,
             summary="Send notification using template")
async def send_from_template(
    payload: SendFromTemplateRequest,
    current_user: CurrentUser,
    service: Annotated[NotificationDomainService, Depends(_get_service)],
) -> MessageResponse:
    await service.send_from_template(
        template_name=payload.template_name,
        recipient_email=payload.recipient_email,
        variables=payload.variables,
        tenant_id=payload.tenant_id,
        user_id=payload.user_id,
    )
    return MessageResponse(message="Notification sent via template")


@router.get("/templates", response_model=SuccessResponse[list[dict]],
            summary="List notification templates")
async def list_templates(
    current_user: CurrentUser,
    service: Annotated[NotificationDomainService, Depends(_get_service)],
) -> SuccessResponse[list[dict]]:
    templates = await service._templates.list_all()
    return SuccessResponse.of([
        {"id": t.id, "name": t.name, "channel": t.channel, "subject": t.subject}
        for t in templates
    ])


@router.post("/templates", response_model=SuccessResponse[dict], status_code=201,
             summary="Create notification template (admin)")
async def create_template(
    payload: CreateTemplateRequest,
    _: Annotated[CurrentUser, Depends(require_role("super_admin", "tenant_admin"))],
    service: Annotated[NotificationDomainService, Depends(_get_service)],
) -> SuccessResponse[dict]:
    template = await service._templates.create(
        name=payload.name,
        subject=payload.subject,
        body_html=payload.body_html,
        body_text=payload.body_text,
        channel=payload.channel,
        variables=payload.variables,
    )
    return SuccessResponse.of({"id": template.id, "name": template.name})
