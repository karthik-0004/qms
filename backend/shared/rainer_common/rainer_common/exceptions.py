"""Rainer Common — Custom exception hierarchy."""

from typing import Any


class RainerException(Exception):
    """Base exception for all Rainer Platform services."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or []
        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


class NotFoundError(RainerException):
    """Resource not found."""

    def __init__(
        self,
        resource: str,
        identifier: str | None = None,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with id '{identifier}' not found"
        super().__init__(
            code="NOT_FOUND",
            message=message,
            status_code=404,
            details=details,
        )


class ForbiddenError(RainerException):
    """Insufficient permissions."""

    def __init__(
        self,
        message: str = "You do not have permission to perform this action",
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(
            code="FORBIDDEN",
            message=message,
            status_code=403,
            details=details,
        )


class UnauthorizedError(RainerException):
    """Authentication required or token invalid."""

    def __init__(
        self,
        message: str = "Authentication required",
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=401,
            details=details,
        )


class ConflictError(RainerException):
    """Resource already exists or state conflict."""

    def __init__(
        self,
        message: str,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(
            code="CONFLICT",
            message=message,
            status_code=409,
            details=details,
        )


class ValidationError(RainerException):
    """Request validation failed."""

    def __init__(
        self,
        message: str = "Request validation failed",
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=422,
            details=details,
        )


class ServiceUnavailableError(RainerException):
    """Upstream service or dependency unavailable."""

    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(
            code="SERVICE_UNAVAILABLE",
            message=message,
            status_code=503,
            details=details,
        )


class TooManyRequestsError(RainerException):
    """Rate limit exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded. Please try again later.",
        retry_after: int | None = None,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(
            code="TOO_MANY_REQUESTS",
            message=message,
            status_code=429,
            details=details,
        )
        self.retry_after = retry_after


class TenantNotFoundError(NotFoundError):
    """Tenant not found or not accessible."""

    def __init__(self, tenant_id: str | None = None) -> None:
        super().__init__(resource="Tenant", identifier=tenant_id)
        self.code = "TENANT_NOT_FOUND"


class TenantSuspendedError(ForbiddenError):
    """Tenant account is suspended."""

    def __init__(self) -> None:
        super().__init__(message="Tenant account is suspended")
        self.code = "TENANT_SUSPENDED"


class InvalidTokenError(UnauthorizedError):
    """JWT token is invalid or expired."""

    def __init__(self, message: str = "Token is invalid or expired") -> None:
        super().__init__(message=message)
        self.code = "INVALID_TOKEN"


class MFARequiredError(UnauthorizedError):
    """MFA verification required."""

    def __init__(self) -> None:
        super().__init__(message="Multi-factor authentication required")
        self.code = "MFA_REQUIRED"

