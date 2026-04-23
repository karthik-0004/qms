"""Config Service — Feature flags and per-tenant configuration domain service."""

from typing import Any

import structlog

from rainer_common.exceptions import NotFoundError

logger = structlog.get_logger(__name__)

# Platform-wide default feature flags
DEFAULT_FEATURE_FLAGS: dict[str, bool] = {
    "qms.documents": True,
    "qms.quality_events": True,
    "qms.capa": True,
    "qms.training": True,
    "qms.equipment": True,
    "qms.audits": True,
    "qms.risk": False,
    "qms.complaints": False,
    "qms.supplier": False,
    "em.plates": True,
    "em.ai_analysis": True,
    "em.qa_review": True,
    "ccv.crm": True,
    "ccv.contracts": True,
    "ccv.workorders": True,
    "ccv.certificates": True,
    "ccv.billing": False,
    "ccv.portal": False,
    "platform.mfa": True,
    "platform.audit_export": True,
    "platform.advanced_reporting": False,
}

# Platform enums (read-only configuration)
PLATFORM_ENUMS: dict[str, list[dict[str, str]]] = {
    "document_status": [
        {"value": "draft", "label": "Draft"},
        {"value": "under_review", "label": "Under Review"},
        {"value": "approved", "label": "Approved"},
        {"value": "obsolete", "label": "Obsolete"},
    ],
    "quality_event_type": [
        {"value": "deviation", "label": "Deviation"},
        {"value": "non_conformance", "label": "Non-Conformance"},
        {"value": "complaint", "label": "Complaint"},
        {"value": "observation", "label": "Observation"},
    ],
    "capa_status": [
        {"value": "open", "label": "Open"},
        {"value": "in_progress", "label": "In Progress"},
        {"value": "under_review", "label": "Under Review"},
        {"value": "closed", "label": "Closed"},
        {"value": "cancelled", "label": "Cancelled"},
    ],
    "severity": [
        {"value": "critical", "label": "Critical"},
        {"value": "major", "label": "Major"},
        {"value": "minor", "label": "Minor"},
        {"value": "informational", "label": "Informational"},
    ],
    "workorder_status": [
        {"value": "scheduled", "label": "Scheduled"},
        {"value": "in_progress", "label": "In Progress"},
        {"value": "completed", "label": "Completed"},
        {"value": "cancelled", "label": "Cancelled"},
    ],
    "regulatory_frameworks": [
        {"value": "iso_9001", "label": "ISO 9001:2015"},
        {"value": "iso_17025", "label": "ISO/IEC 17025:2017"},
        {"value": "gmp", "label": "GMP (Good Manufacturing Practice)"},
        {"value": "fda_21_cfr_820", "label": "FDA 21 CFR Part 820"},
        {"value": "eu_ivdr", "label": "EU IVDR 2017/746"},
    ],
}


class ConfigDomainService:
    """Platform-wide configuration and feature flag management."""

    async def get_feature_flags(
        self,
        tenant_id: str | None = None,
        tenant_overrides: dict | None = None,
    ) -> dict[str, bool]:
        """Get feature flags, merging defaults with tenant overrides."""
        flags = dict(DEFAULT_FEATURE_FLAGS)
        if tenant_overrides:
            flags.update({k: v for k, v in tenant_overrides.items() if k in flags})
        return flags

    async def get_feature_flag(self, flag_key: str, tenant_overrides: dict | None = None) -> bool:
        flags = await self.get_feature_flags(tenant_overrides=tenant_overrides)
        if flag_key not in flags:
            raise NotFoundError("FeatureFlag", flag_key)
        return flags[flag_key]

    async def get_enums(self, enum_type: str) -> list[dict[str, str]]:
        """Get enum values by type."""
        enums = PLATFORM_ENUMS.get(enum_type)
        if enums is None:
            raise NotFoundError("Enum", enum_type)
        return enums

    async def list_enum_types(self) -> list[str]:
        return list(PLATFORM_ENUMS.keys())

    async def get_platform_config(self) -> dict[str, Any]:
        """Get complete platform configuration."""
        return {
            "feature_flags": DEFAULT_FEATURE_FLAGS,
            "enum_types": list(PLATFORM_ENUMS.keys()),
            "supported_products": ["qms", "em", "ccv"],
            "supported_tiers": ["starter", "professional", "enterprise"],
            "supported_regions": ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
        }
