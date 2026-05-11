"""Unit tests — temporary onboarding password."""

from app.core.bootstrap_password import generate_temporary_password
from app.core.security import is_strong_password


def test_generate_temporary_password_meets_policy() -> None:
    pw = generate_temporary_password()
    assert len(pw) >= 8
    assert is_strong_password(pw)
