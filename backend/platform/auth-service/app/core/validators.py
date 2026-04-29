from __future__ import annotations

from email_validator import EmailNotValidError, validate_email

from .config import get_settings


def _is_basic_email_shape(value: str) -> bool:
    candidate = value.strip()
    if " " in candidate:
        return False
    if candidate.count("@") != 1:
        return False
    local_part, domain = candidate.split("@", 1)
    if not local_part or not domain:
        return False
    if domain.startswith(".") or domain.endswith("."):
        return False
    if ".." in domain:
        return False
    return True


def validate_request_email(value: str) -> str:
    settings = get_settings()
    test_environment = (not settings.is_production) and settings.allow_reserved_email_domains

    try:
        result = validate_email(
            value,
            allow_smtputf8=True,
            check_deliverability=False,
            test_environment=test_environment,
        )
    except EmailNotValidError as e:
        if test_environment and "special-use or reserved name" in str(e) and _is_basic_email_shape(value):
            return value.strip().lower()
        raise ValueError(str(e)) from e

    return result.normalized

