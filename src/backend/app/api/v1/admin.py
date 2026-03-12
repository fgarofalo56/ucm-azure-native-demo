"""Admin endpoints: user management, role assignment, current user info."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AppUser
from app.db.session import get_db_session
from app.middleware.auth import get_app_user, require_permission
from app.models.enums import AuditEventType
from app.models.schemas import (
    AppUserResponse,
    CurrentUserResponse,
    PaginatedResponse,
    RoleResponse,
    UserRoleAssignment,
)
from app.services.audit_service import AuditService
from app.services.rbac_service import RBACService

logger = structlog.get_logger()
router = APIRouter()


@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user(
    app_user: Annotated[AppUser, Depends(get_app_user)],
) -> CurrentUserResponse:
    """Get the current user's profile, roles, and permissions."""
    permissions: list[str] = []
    role_names: list[str] = []
    for role in app_user.roles:
        role_names.append(role.name)
        for perm in role.permissions:
            perm_str = f"{perm.resource}.{perm.action}"
            if perm_str not in permissions:
                permissions.append(perm_str)

    return CurrentUserResponse(
        id=app_user.id,
        entra_oid=app_user.entra_oid,
        display_name=app_user.display_name,
        email=app_user.email,
        roles=role_names,
        permissions=permissions,
    )


@router.get("/users", response_model=PaginatedResponse)
async def list_users(
    app_user: Annotated[AppUser, Depends(require_permission("users", "read"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse:
    """List all application users. Requires users.read permission."""
    rbac_svc = RBACService(session)
    users, total = await rbac_svc.list_users(page=page, page_size=page_size)

    return PaginatedResponse(
        data=[AppUserResponse.model_validate(u) for u in users],
        meta={"page": page, "page_size": page_size, "total": total},
    )


@router.get("/roles", response_model=list[RoleResponse])
async def list_roles(
    app_user: Annotated[AppUser, Depends(require_permission("roles", "manage"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[RoleResponse]:
    """List all available roles. Requires roles.manage permission."""
    rbac_svc = RBACService(session)
    roles = await rbac_svc.list_roles()
    return [RoleResponse.model_validate(r) for r in roles]


@router.put("/users/{user_id}/roles", response_model=AppUserResponse)
async def assign_user_roles(
    user_id: str,
    body: UserRoleAssignment,
    app_user: Annotated[AppUser, Depends(require_permission("roles", "manage"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AppUserResponse:
    """Assign roles to a user. Requires roles.manage permission."""
    rbac_svc = RBACService(session)
    audit_svc = AuditService(session)

    updated_user = await rbac_svc.assign_roles(user_id, body.role_names)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await audit_svc.log_event(
        event_type=AuditEventType.USER_ROLE_CHANGED,
        user_id=app_user.entra_oid,
        user_principal_name=app_user.email,
        action="update",
        result="success",
        resource_type="user",
        resource_id=user_id,
        details={
            "assigned_roles": body.role_names,
            "target_user": updated_user.display_name,
        },
    )

    return AppUserResponse.model_validate(updated_user)
