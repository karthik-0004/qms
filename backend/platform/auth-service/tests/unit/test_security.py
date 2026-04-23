"""Unit tests — security helpers (password hashing, strength check)."""

import pytest

from app.core.security import hash_password, is_strong_password, verify_password


class TestPasswordHashing:
    def test_hash_password_returns_bcrypt_string(self):
        result = hash_password("MyPassword123!")
        assert result.startswith("$2b$")

    def test_hash_is_not_plain_text(self):
        plain = "MyPassword123!"
        hashed = hash_password(plain)
        assert hashed != plain

    def test_verify_correct_password(self):
        plain = "MyPassword123!"
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("MyPassword123!")
        assert verify_password("WrongPassword!", hashed) is False

    def test_different_hashes_for_same_password(self):
        plain = "MyPassword123!"
        hash1 = hash_password(plain)
        hash2 = hash_password(plain)
        assert hash1 != hash2
        assert verify_password(plain, hash1)
        assert verify_password(plain, hash2)


class TestPasswordStrength:
    def test_strong_password_passes(self):
        assert is_strong_password("StrongPass123!") is True

    def test_too_short_fails(self):
        assert is_strong_password("Ab1!") is False

    def test_no_uppercase_fails(self):
        assert is_strong_password("weakpass123!") is False

    def test_no_lowercase_fails(self):
        assert is_strong_password("WEAKPASS123!") is False

    def test_no_digit_fails(self):
        assert is_strong_password("NoDigitPass!") is False

    def test_no_special_fails(self):
        assert is_strong_password("NoSpecialPass1") is False

    def test_exactly_8_chars_passes(self):
        assert is_strong_password("Aa1!Bb2@") is True
