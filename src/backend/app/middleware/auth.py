"""Entra ID JWT validation middleware and dependencies."""

import time
from typing import Annotated

import httpx
import structlog
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings

logger = structlog.get_logger()
security = HTTPBearer()

# JWKS cache TTL in seconds (24 hours)
_JWKS_CACHE_TTL = 86400


class UserClaims(BaseModel):
    """Extracted claims from validated JWT."""

    oid: str  # Entra ID object ID
    name: str = ""
    preferred_username: str = ""
    roles: list[str] = []
    tid: str = ""  # Tenant ID


# Cache for JWKS keys with expiration
_jwks_cache: dict[str, tuple[dict, float]] = {}


async def _get_jwks() -> dict:
    """Fetch Entra ID JWKS (JSON Web Key Set) for token validation."""
    authority = settings.azure_authority
    tenant_id = settings.entra_tenant_id
    openid_config_url = f"{authority}/{tenant_id}/v2.0/.well-known/openid-configuration"

    cache_key = openid_config_url
    now = time.monotonic()

    if cache_key in _jwks_cache:
        cached_jwks, cached_at = _jwks_cache[cache_key]
        if now - cached_at < _JWKS_CACHE_TTL:
            return cached_jwks

    async with httpx.AsyncClient() as client:
        config_response = await client.get(openid_config_url)
        config_response.raise_for_status()
        jwks_uri = config_response.json()["jwks_uri"]

        jwks_response = await client.get(jwks_uri)
        jwks_response.raise_for_status()
        jwks = jwks_response.json()

    _jwks_cache[cache_key] = (jwks, now)
    return jwks


async def validate_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Security(security)],
) -> UserClaims:
    """Validate Entra ID JWT and extract user claims."""
    token = credentials.credentials

    try:
        jwks = await _get_jwks()

        # Decode header to get key ID
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        # Find matching key
        rsa_key = {}
        for key in jwks.get("keys", []):
            if key["kid"] == kid:
                rsa_key = key
                break

        if not rsa_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to find appropriate key",
            )

        # Accept both v1.0 and v2.0 tokens (Entra ID may issue either)
        valid_issuers = [
            f"{settings.azure_authority}/{settings.entra_tenant_id}/v2.0",
            f"https://sts.windows.net/{settings.entra_tenant_id}/",
        ]

        # Validate and decode token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=settings.entra_audience,
            issuer=valid_issuers,
        )

        return UserClaims(
            oid=payload.get("oid", ""),
            name=payload.get("name", ""),
            preferred_username=payload.get("preferred_username", ""),
            roles=payload.get("roles", []),
            tid=payload.get("tid", ""),
        )

    except JWTError as e:
        logger.warning("jwt_validation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from e


def require_role(*required_roles: str):
    """Dependency factory to enforce role-based access."""

    async def _check_roles(
        user: Annotated[UserClaims, Depends(validate_token)],
    ) -> UserClaims:
        if not any(role in user.roles for role in required_roles):
            logger.warning(
                "authorization_denied",
                user_id=user.oid,
                required_roles=list(required_roles),
                user_roles=user.roles,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return _check_roles


async def get_current_app_user(
    claims: Annotated[UserClaims, Depends(validate_token)],
    session: Annotated[AsyncSession, Depends(lambda: None)],
):
    """Auto-provision and return the AppUser for the current JWT.

    NOTE: This is a template - the actual session dependency is injected
    at the route level via get_db_session. Use _get_current_app_user() below.
    """
    pass


def _get_current_app_user():
    """Factory that creates the get_current_app_user dependency with DB session."""
    from app.db.session import get_db_session

    async def _inner(
        claims: Annotated[UserClaims, Depends(validate_token)],
        session: Annotated[AsyncSession, Depends(get_db_session)],
    ):
        from app.services.rbac_service import RBACService

        rbac_svc = RBACService(session)
        app_user = await rbac_svc.get_or_create_user(
            oid=claims.oid,
            name=claims.name,
            email=claims.preferred_username,
        )
        return app_user

    return _inner


# Dependency to get the current AppUser (auto-provisions on first login)
get_app_user = _get_current_app_user()


def require_permission(resource: str, action: str):
    """Dependency factory that checks DB-based permissions for the current user."""
    from app.db.models import AppUser
    from app.db.session import get_db_session

    async def _check_permission(
        claims: Annotated[UserClaims, Depends(validate_token)],
        session: Annotated[AsyncSession, Depends(get_db_session)],
    ) -> AppUser:
        from app.services.audit_service import AuditService
        from app.services.rbac_service import RBACService

        rbac_svc = RBACService(session)
        app_user = await rbac_svc.get_or_create_user(
            oid=claims.oid,
            name=claims.name,
            email=claims.preferred_username,
        )

        has_perm = await rbac_svc.user_has_permission(app_user, resource, action)
        if not has_perm:
            audit_svc = AuditService(session)
            await audit_svc.log_event(
                event_type="auth.denied",
                user_id=app_user.entra_oid,
                user_principal_name=app_user.email,
                action=action,
                result="denied",
                resource_type=resource,
                details={"required": f"{resource}.{action}"},
            )
            logger.warning(
                "permission_denied",
                user_id=app_user.entra_oid,
                required=f"{resource}.{action}",
                user_roles=[r.name for r in app_user.roles],
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {resource}.{action}",
            )
        return app_user

    return _check_permission
