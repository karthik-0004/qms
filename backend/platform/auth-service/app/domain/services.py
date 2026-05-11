"""Auth Service — Core authentication domain service."""

from datetime import datetime, timedelta, timezone
import time

import pyotp
import structlog

from rainer_auth_lib.access_keys import (
    extract_key_prefix,
    generate_access_key,
    verify_access_key,
)
from rainer_auth_lib.jwt import JWTSettings, create_access_token, create_refresh_token
from rainer_common.exceptions import (
    ConflictError,
    ForbiddenError,
    InvalidTokenError,
    MFARequiredError,
    NotFoundError,
    UnauthorizedError,
)

from ..core.config import Settings
from ..core.security import hash_password, is_strong_password, verify_password
from ..infra.db.models import PlatformUser, RefreshToken, ServiceAccessKey
from ..infra.db.repositories import (
    AccessKeyRepository,
    AuditLogRepository,
    RefreshTokenRepository,
    UserRepository,
)

logger = structlog.get_logger(__name__)


class AuthDomainService:
    """Core authentication business logic."""

    def __init__(
        self,
        user_repo: UserRepository,
        token_repo: RefreshTokenRepository,
        key_repo: AccessKeyRepository,
        audit_repo: AuditLogRepository,
        settings: Settings,
    ) -> None:
        self._users = user_repo
        self._tokens = token_repo
        self._keys = key_repo
        self._audit = audit_repo
        self._settings = settings
        self._jwt_settings = JWTSettings(
            secret_key=settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
            access_token_expire_minutes=settings.jwt_access_token_expire_minutes,
            refresh_token_expire_days=settings.jwt_refresh_token_expire_days,
        )

    async def login(
        self,
        email: str,
        password: str,
        mfa_code: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict:
        """
        Authenticate user with email/password (+ optional MFA).
        Returns access_token, refresh_token, and user info.
        """
        perf_enabled = bool(self._settings.enable_perf_logs)
        t0 = time.perf_counter()
        t_db_user_start = time.perf_counter()
        user = await self._users.get_by_email(email)
        t_db_user_ms = (time.perf_counter() - t_db_user_start) * 1000

        if not user:
            logger.warning("login_user_not_found", email=email)
            raise UnauthorizedError("Invalid email or password")

        if user.status == "locked" or (
            user.locked_until and user.locked_until > datetime.now(timezone.utc)
        ):
            raise ForbiddenError("Account is locked. Please contact support.")

        if user.status != "active":
            raise ForbiddenError("Account is not active.")

        t_verify_start = time.perf_counter()
        password_ok = verify_password(password, user.password_hash)
        t_verify_ms = (time.perf_counter() - t_verify_start) * 1000
        if not password_ok:
            attempts = await self._users.increment_failed_attempts(user.id)
            logger.warning("login_failed", user_id=user.id, attempts=attempts)

            if attempts >= self._settings.max_failed_login_attempts:
                lockout_until = datetime.now(timezone.utc) + timedelta(
                    minutes=self._settings.account_lockout_minutes
                )
                await self._users.lock_account(user.id, lockout_until)
                await self._audit.create(
                    action="USER_LOCKED",
                    user_id=user.id,
                    tenant_id=user.tenant_id,
                    ip_address=ip_address,
                    severity="warning",
                )
                raise ForbiddenError("Too many failed attempts. Account locked.")

            raise UnauthorizedError("Invalid email or password")

        # MFA check
        if user.mfa_enabled:
            if not mfa_code:
                raise MFARequiredError()
            if not self._verify_totp(user.mfa_secret, mfa_code):
                raise UnauthorizedError("Invalid MFA code")

        # Issue tokens
        t_issue_tokens_start = time.perf_counter()
        access_token, access_jti = create_access_token(
            subject=user.id,
            email=user.email,
            settings=self._jwt_settings,
            tenant_id=user.tenant_id,
            role=user.role,
        )
        raw_refresh, refresh_jti = create_refresh_token(
            subject=user.id,
            settings=self._jwt_settings,
        )
        t_issue_tokens_ms = (time.perf_counter() - t_issue_tokens_start) * 1000

        expires_at = datetime.now(timezone.utc) + timedelta(
            days=self._settings.jwt_refresh_token_expire_days
        )
        t_db_writes_start = time.perf_counter()
        await self._tokens.create(
            user_id=user.id,
            raw_token=raw_refresh,
            expires_at=expires_at,
            ip_address=ip_address,
            device_info={"user_agent": user_agent} if user_agent else None,
        )
        await self._users.update_last_login(user.id, ip_address)
        await self._audit.create(
            action="USER_LOGIN",
            user_id=user.id,
            tenant_id=user.tenant_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        t_db_writes_ms = (time.perf_counter() - t_db_writes_start) * 1000

        logger.info("user_logged_in", user_id=user.id, tenant_id=user.tenant_id)
        if perf_enabled:
            total_ms = (time.perf_counter() - t0) * 1000
            logger.info(
                "login_perf",
                user_id=user.id,
                tenant_id=user.tenant_id,
                db_user_ms=round(t_db_user_ms, 2),
                verify_ms=round(t_verify_ms, 2),
                issue_tokens_ms=round(t_issue_tokens_ms, 2),
                db_writes_ms=round(t_db_writes_ms, 2),
                total_ms=round(total_ms, 2),
            )

        return {
            "access_token": access_token,
            "refresh_token": raw_refresh,
            "token_type": "bearer",
            "expires_in": self._settings.jwt_access_token_expire_minutes * 60,
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "tenant_id": user.tenant_id,
                "mfa_enabled": user.mfa_enabled,
            },
        }

    async def refresh_tokens(
        self, raw_refresh_token: str, ip_address: str | None = None
    ) -> dict:
        """Rotate refresh token and issue new access + refresh pair."""
        token = await self._tokens.get_valid_by_hash(raw_refresh_token)
        if not token:
            raise InvalidTokenError("Refresh token is invalid or expired")

        user = await self._users.get_by_id(token.user_id)
        if not user or user.status != "active":
            raise UnauthorizedError("User not found or inactive")

        # Revoke old token (rotation)
        await self._tokens.revoke(token.id)

        # Issue new pair
        access_token, _ = create_access_token(
            subject=user.id,
            email=user.email,
            settings=self._jwt_settings,
            tenant_id=user.tenant_id,
            role=user.role,
        )
        raw_new_refresh, _ = create_refresh_token(
            subject=user.id,
            settings=self._jwt_settings,
        )
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=self._settings.jwt_refresh_token_expire_days
        )
        await self._tokens.create(
            user_id=user.id,
            raw_token=raw_new_refresh,
            expires_at=expires_at,
            ip_address=ip_address,
        )

        logger.info("token_refreshed", user_id=user.id)

        return {
            "access_token": access_token,
            "refresh_token": raw_new_refresh,
            "token_type": "bearer",
            "expires_in": self._settings.jwt_access_token_expire_minutes * 60,
        }

    async def logout(self, raw_refresh_token: str) -> None:
        """Revoke the given refresh token."""
        token = await self._tokens.get_valid_by_hash(raw_refresh_token)
        if token:
            await self._tokens.revoke(token.id)
            logger.info("user_logged_out", user_id=token.user_id)

    async def logout_all(self, user_id: str) -> None:
        """Revoke all refresh tokens for a user (logout everywhere)."""
        await self._tokens.revoke_all_for_user(user_id)
        logger.info("user_logged_out_all_devices", user_id=user_id)

    async def setup_mfa(self, user_id: str) -> dict:
        """Generate a new TOTP secret and return QR provisioning URI."""
        user = await self._users.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)

        if user.mfa_enabled:
            raise ConflictError("MFA is already enabled for this user")

        totp = pyotp.TOTP(pyotp.random_base32())
        provisioning_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name=self._settings.mfa_issuer_name,
        )

        # Store secret temporarily (not yet enabled — enabled after verification)
        await self._users.update_mfa(user_id, totp.secret, enabled=False)

        return {
            "secret": totp.secret,
            "provisioning_uri": provisioning_uri,
            "qr_code_url": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={provisioning_uri}",
        }

    async def verify_and_enable_mfa(self, user_id: str, code: str) -> bool:
        """Verify TOTP code and enable MFA if valid."""
        user = await self._users.get_by_id(user_id)
        if not user or not user.mfa_secret:
            raise NotFoundError("User", user_id)

        if not self._verify_totp(user.mfa_secret, code):
            raise UnauthorizedError("Invalid MFA code")

        await self._users.update_mfa(user_id, user.mfa_secret, enabled=True)
        await self._audit.create(
            action="MFA_ENABLED",
            user_id=user_id,
            tenant_id=user.tenant_id,
        )
        logger.info("mfa_enabled", user_id=user_id)
        return True

    async def disable_mfa(self, user_id: str, password: str) -> bool:
        """Disable MFA after password confirmation."""
        user = await self._users.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)

        if not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid password")

        await self._users.update_mfa(user_id, None, enabled=False)
        await self._audit.create(
            action="MFA_DISABLED",
            user_id=user_id,
            tenant_id=user.tenant_id,
            severity="warning",
        )
        logger.info("mfa_disabled", user_id=user_id)
        return True

    async def create_access_key(
        self,
        service_name: str,
        scopes: list[str],
        expires_at: datetime | None = None,
    ) -> dict:
        """Generate a new service-to-service access key."""
        raw_key, key_hash, key_prefix = generate_access_key()
        key = await self._keys.create(
            service_name=service_name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            scopes=scopes,
            expires_at=expires_at,
        )
        logger.info("access_key_created", service_name=service_name, key_id=key.id)
        return {
            "id": key.id,
            "raw_key": raw_key,
            "key_prefix": key_prefix,
            "service_name": service_name,
            "scopes": scopes,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "warning": "Store this key securely. It will NOT be shown again.",
        }

    async def revoke_access_key(self, key_id: str) -> None:
        """Revoke a service access key."""
        key = await self._keys.get_by_id(key_id)
        if not key:
            raise NotFoundError("AccessKey", key_id)
        await self._keys.revoke(key_id)
        logger.info("access_key_revoked", key_id=key_id, service_name=key.service_name)

    async def validate_access_key(self, raw_key: str) -> ServiceAccessKey | None:
        """Validate an access key. Returns key record or None."""
        prefix = extract_key_prefix(raw_key)
        candidates = await self._keys.find_by_prefix(prefix)
        now = datetime.now(timezone.utc)

        for candidate in candidates:
            if candidate.expires_at and candidate.expires_at < now:
                continue
            if verify_access_key(raw_key, candidate.key_hash):
                return candidate
        return None

    def _verify_totp(self, secret: str | None, code: str) -> bool:
        if not secret:
            return False
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)
