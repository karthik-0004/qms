"""Gateway Service — Token validation and routing API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, status
from pydantic import BaseModel

from rainer_auth_lib.jwt import JWTSettings
from rainer_common.responses import SuccessResponse

from ....core.config import Settings, get_settings
from ....domain.services import GatewayDomainService

router = APIRouter(prefix="/gateway", tags=["Gateway"])


def _get_service(settings: Annotated[Settings, Depends(get_settings)]) -> GatewayDomainService:
    return GatewayDomainService(
        jwt_settings=JWTSettings(
            secret_key=settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )
    )


class ValidateTokenResponse(BaseModel):
    valid: bool
    user_id: str | None = None
    tenant_id: str | None = None
    role: str | None = None
    permissions: list[str] = []


@router.post(
    "/validate-token",
    response_model=SuccessResponse[ValidateTokenResponse],
    summary="Validate JWT token and extract tenant context (internal)",
)
async def validate_token(
    service: Annotated[GatewayDomainService, Depends(_get_service)],
    authorization: str | None = Header(default=None),
) -> SuccessResponse[ValidateTokenResponse]:
    raw_token = service.extract_bearer_token(authorization)
    if not raw_token:
        return SuccessResponse.of(ValidateTokenResponse(valid=False))

    try:
        payload = service.validate_token(raw_token)
        return SuccessResponse.of(
            ValidateTokenResponse(
                valid=True,
                user_id=payload["user_id"],
                tenant_id=payload.get("tenant_id"),
                role=payload.get("role"),
                permissions=payload.get("permissions", []),
            )
        )
    except Exception:
        return SuccessResponse.of(ValidateTokenResponse(valid=False))
