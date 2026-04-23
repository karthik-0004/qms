"""Rainer Auth Lib — Service access key generation and verification."""

import hashlib
import hmac
import secrets
import string

_KEY_ALPHABET = string.ascii_letters + string.digits
_KEY_PREFIX = "rsk"  # rainer service key
_KEY_BODY_LENGTH = 40


def generate_access_key() -> tuple[str, str, str]:
    """
    Generate a new service access key.

    Returns:
        (raw_key, key_hash, key_prefix) tuple
        - raw_key: full key shown to user ONCE (e.g. rsk_abc123...)
        - key_hash: SHA-256 hash stored in DB
        - key_prefix: first 8 chars for fast DB lookup
    """
    body = "".join(secrets.choice(_KEY_ALPHABET) for _ in range(_KEY_BODY_LENGTH))
    raw_key = f"{_KEY_PREFIX}_{body}"
    key_hash = hash_access_key(raw_key)
    key_prefix = raw_key[:8]
    return raw_key, key_hash, key_prefix


def hash_access_key(raw_key: str) -> str:
    """Hash an access key using SHA-256. Result stored in DB."""
    return hashlib.sha256(raw_key.encode()).hexdigest()


def verify_access_key(raw_key: str, stored_hash: str) -> bool:
    """
    Securely compare the hash of raw_key against stored_hash.
    Uses constant-time comparison to prevent timing attacks.
    """
    computed = hash_access_key(raw_key)
    return hmac.compare_digest(computed.encode(), stored_hash.encode())


def extract_key_prefix(raw_key: str) -> str:
    """Extract the first 8 characters of the key for DB lookup."""
    return raw_key[:8]

