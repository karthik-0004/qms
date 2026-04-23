"""Rainer Auth Lib — Permission and role definitions."""

from enum import StrEnum


class UserRole(StrEnum):
    SUPER_ADMIN = "super_admin"
    TENANT_ADMIN = "tenant_admin"
    TENANT_USER = "tenant_user"


class Permission(StrEnum):
    # Platform
    TENANT_READ = "tenant:read"
    TENANT_WRITE = "tenant:write"
    TENANT_DELETE = "tenant:delete"
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    ROLE_READ = "role:read"
    ROLE_WRITE = "role:write"
    AUDIT_READ = "audit:read"
    AUDIT_EXPORT = "audit:export"
    CONFIG_READ = "config:read"
    CONFIG_WRITE = "config:write"

    # QMS
    DOCUMENT_READ = "document:read"
    DOCUMENT_WRITE = "document:write"
    DOCUMENT_APPROVE = "document:approve"
    DOCUMENT_DELETE = "document:delete"
    QUALITY_EVENT_READ = "quality_event:read"
    QUALITY_EVENT_WRITE = "quality_event:write"
    CAPA_READ = "capa:read"
    CAPA_WRITE = "capa:write"
    CAPA_APPROVE = "capa:approve"
    TRAINING_READ = "training:read"
    TRAINING_WRITE = "training:write"
    TRAINING_ASSIGN = "training:assign"
    EQUIPMENT_READ = "equipment:read"
    EQUIPMENT_WRITE = "equipment:write"

    # EM
    PLATE_READ = "plate:read"
    PLATE_WRITE = "plate:write"
    JOB_READ = "job:read"
    JOB_WRITE = "job:write"
    QA_REVIEW_READ = "qa_review:read"
    QA_REVIEW_WRITE = "qa_review:write"
    QA_REVIEW_APPROVE = "qa_review:approve"

    # CCV
    CRM_READ = "crm:read"
    CRM_WRITE = "crm:write"
    CONTRACT_READ = "contract:read"
    CONTRACT_WRITE = "contract:write"
    WORKORDER_READ = "workorder:read"
    WORKORDER_WRITE = "workorder:write"
    WORKORDER_EXECUTE = "workorder:execute"
    CERTIFICATE_READ = "certificate:read"
    CERTIFICATE_WRITE = "certificate:write"
    CERTIFICATE_ISSUE = "certificate:issue"
    BILLING_READ = "billing:read"
    BILLING_WRITE = "billing:write"

    # Reporting
    REPORT_READ = "report:read"
    REPORT_GENERATE = "report:generate"
    ANALYTICS_READ = "analytics:read"


# Default permissions per role
ROLE_PERMISSIONS: dict[UserRole, list[Permission]] = {
    UserRole.SUPER_ADMIN: list(Permission),  # All permissions
    UserRole.TENANT_ADMIN: [
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.USER_DELETE,
        Permission.ROLE_READ,
        Permission.ROLE_WRITE,
        Permission.AUDIT_READ,
        Permission.AUDIT_EXPORT,
        Permission.CONFIG_READ,
        Permission.CONFIG_WRITE,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_WRITE,
        Permission.DOCUMENT_APPROVE,
        Permission.DOCUMENT_DELETE,
        Permission.QUALITY_EVENT_READ,
        Permission.QUALITY_EVENT_WRITE,
        Permission.CAPA_READ,
        Permission.CAPA_WRITE,
        Permission.CAPA_APPROVE,
        Permission.TRAINING_READ,
        Permission.TRAINING_WRITE,
        Permission.TRAINING_ASSIGN,
        Permission.EQUIPMENT_READ,
        Permission.EQUIPMENT_WRITE,
        Permission.PLATE_READ,
        Permission.PLATE_WRITE,
        Permission.JOB_READ,
        Permission.JOB_WRITE,
        Permission.QA_REVIEW_READ,
        Permission.QA_REVIEW_WRITE,
        Permission.QA_REVIEW_APPROVE,
        Permission.CRM_READ,
        Permission.CRM_WRITE,
        Permission.CONTRACT_READ,
        Permission.CONTRACT_WRITE,
        Permission.WORKORDER_READ,
        Permission.WORKORDER_WRITE,
        Permission.CERTIFICATE_READ,
        Permission.CERTIFICATE_WRITE,
        Permission.CERTIFICATE_ISSUE,
        Permission.BILLING_READ,
        Permission.BILLING_WRITE,
        Permission.REPORT_READ,
        Permission.REPORT_GENERATE,
        Permission.ANALYTICS_READ,
    ],
    UserRole.TENANT_USER: [
        Permission.DOCUMENT_READ,
        Permission.QUALITY_EVENT_READ,
        Permission.CAPA_READ,
        Permission.TRAINING_READ,
        Permission.EQUIPMENT_READ,
        Permission.PLATE_READ,
        Permission.JOB_READ,
        Permission.QA_REVIEW_READ,
        Permission.CRM_READ,
        Permission.CONTRACT_READ,
        Permission.WORKORDER_READ,
        Permission.CERTIFICATE_READ,
        Permission.REPORT_READ,
        Permission.ANALYTICS_READ,
    ],
}


def has_permission(
    role: str,
    permission: Permission,
    extra_permissions: list[str] | None = None,
) -> bool:
    """Check if a role (plus any extra permissions) includes the given permission."""
    try:
        role_enum = UserRole(role)
        role_perms = ROLE_PERMISSIONS.get(role_enum, [])
    except ValueError:
        role_perms = []

    if permission in role_perms:
        return True

    if extra_permissions and permission.value in extra_permissions:
        return True

    return False
