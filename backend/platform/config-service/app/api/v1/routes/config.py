"""Config Service — Feature flags and enum configuration API routes."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path

from rainer_auth_lib.dependencies import CurrentUser
from rainer_common.responses import SuccessResponse

from ....domain.services import ConfigDomainService

router = APIRouter(prefix="/config", tags=["Configuration"])


def _get_service() -> ConfigDomainService:
    return ConfigDomainService()


@router.get("/features", response_model=SuccessResponse[dict[str, bool]],
            summary="Get feature flags for current tenant")
async def get_features(
    current_user: CurrentUser,
    service: Annotated[ConfigDomainService, Depends(_get_service)],
) -> SuccessResponse[dict[str, bool]]:
    flags = await service.get_feature_flags()
    return SuccessResponse.of(flags)


@router.get("/features/{flag_key}", response_model=SuccessResponse[dict[str, Any]],
            summary="Get specific feature flag value")
async def get_feature(
    flag_key: str,
    current_user: CurrentUser,
    service: Annotated[ConfigDomainService, Depends(_get_service)],
) -> SuccessResponse[dict[str, Any]]:
    value = await service.get_feature_flag(flag_key)
    return SuccessResponse.of({"key": flag_key, "enabled": value})


@router.get("/enums", response_model=SuccessResponse[list[str]],
            summary="List all available enum types")
async def list_enum_types(
    current_user: CurrentUser,
    service: Annotated[ConfigDomainService, Depends(_get_service)],
) -> SuccessResponse[list[str]]:
    types = await service.list_enum_types()
    return SuccessResponse.of(types)


@router.get("/enums/{enum_type}", response_model=SuccessResponse[list[dict[str, str]]],
            summary="Get enum values by type")
async def get_enums(
    enum_type: str,
    current_user: CurrentUser,
    service: Annotated[ConfigDomainService, Depends(_get_service)],
) -> SuccessResponse[list[dict[str, str]]]:
    enums = await service.get_enums(enum_type)
    return SuccessResponse.of(enums)


@router.get("/platform", response_model=SuccessResponse[dict],
            summary="Get complete platform configuration")
async def get_platform_config(
    current_user: CurrentUser,
    service: Annotated[ConfigDomainService, Depends(_get_service)],
) -> SuccessResponse[dict]:
    config = await service.get_platform_config()
    return SuccessResponse.of(config)
