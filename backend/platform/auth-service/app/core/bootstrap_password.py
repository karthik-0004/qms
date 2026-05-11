"""Strong temporary password generator for onboarding flows."""

import secrets
import string

from .security import is_strong_password

_ALPHABET = string.ascii_letters + string.digits + "!@#$%^&*-_=+"


def generate_temporary_password(length: int = 16) -> str:
    for _ in range(100):
        candidate = "".join(secrets.choice(_ALPHABET) for _ in range(length))
        if is_strong_password(candidate):
            return candidate
    raise RuntimeError("Could not generate a password meeting policy")
