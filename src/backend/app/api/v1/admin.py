"""Admin endpoints: user management, role assignment, document version management, rollback, system settings."""

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AppUser
from app.db.session import get_db_session
from app.dependencies import get_blob_service_client
from app.middleware.auth import get_app_user, require_permission
from app.models.enums import AuditEventType, DocumentType
from app.models.schemas import (
    AdminDocumentDetailResponse,
    AppUserResponse,
    CurrentUserResponse,
    DocumentVersionResponse,
    PaginatedResponse,
    RoleResponse,
    RollbackResponse,
    UserRoleAssignment,
)
from app.services.audit_service import AuditService
from app.services.blob_service import BlobService
from app.services.metadata_service import MetadataService
from app.services.rbac_service import RBACService
from app.services.settings_service import SettingsService

logger = structlog.get_logger()
router = APIRouter()


# ============================================================================
# Current User
# ============================================================================


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


# ============================================================================
# User Management
# ============================================================================


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


# ============================================================================
# Document Version Management (Admin Only)
# ============================================================================


@router.get("/documents/{document_id}", response_model=AdminDocumentDetailResponse)
async def get_document_detail(
    document_id: uuid.UUID,
    app_user: Annotated[AppUser, Depends(require_permission("documents", "versions"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AdminDocumentDetailResponse:
    """Get full document detail with all versions. Admin only."""
    metadata_svc = MetadataService(session)
    document = await metadata_svc.get_document(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    versions = await metadata_svc.list_versions_for_document(document_id)

    return AdminDocumentDetailResponse(
        id=document.id,
        investigation_id=document.investigation_id,
        document_type=DocumentType(document.document_type),
        title=document.title,
        created_by=document.created_by,
        created_by_name=document.created_by_name,
        created_at=document.created_at,
        updated_at=document.updated_at,
        current_version_id=document.current_version_id,
        is_deleted=document.is_deleted,
        versions=[DocumentVersionResponse.model_validate(v) for v in versions],
    )


@router.get("/documents/{document_id}/versions", response_model=list[DocumentVersionResponse])
async def list_document_versions(
    document_id: uuid.UUID,
    app_user: Annotated[AppUser, Depends(require_permission("documents", "versions"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[DocumentVersionResponse]:
    """List all versions of a document. Admin only."""
    metadata_svc = MetadataService(session)

    document = await metadata_svc.get_document(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    versions = await metadata_svc.list_versions_for_document(document_id)
    return [DocumentVersionResponse.model_validate(v) for v in versions]


@router.get("/documents/{document_id}/versions/{version_id}/download")
async def download_specific_version(
    document_id: uuid.UUID,
    version_id: uuid.UUID,
    app_user: Annotated[AppUser, Depends(require_permission("documents", "versions"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> StreamingResponse:
    """Download a specific version of a document. Admin only."""
    metadata_svc = MetadataService(session)
    blob_svc = BlobService(get_blob_service_client())
    audit_svc = AuditService(session)

    document = await metadata_svc.get_document(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    version = await metadata_svc.get_version(version_id)
    if not version or version.document_id != document_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")

    data = await blob_svc.download_blob(version.blob_path_original)

    await audit_svc.log_event(
        event_type=AuditEventType.DOCUMENT_VERSION_ACCESS,
        user_id=app_user.entra_oid,
        user_principal_name=app_user.email,
        action="read",
        result="success",
        resource_type="document_version",
        resource_id=str(version_id),
        details={
            "document_id": str(document_id),
            "version_number": version.version_number,
        },
    )

    return StreamingResponse(
        iter([data]),
        media_type=version.mime_type or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{version.original_filename}"'},
    )


@router.post("/documents/{document_id}/rollback", response_model=RollbackResponse)
async def rollback_document(
    document_id: uuid.UUID,
    app_user: Annotated[AppUser, Depends(require_permission("documents", "rollback"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> RollbackResponse:
    """Roll back a document to its previous version. Admin only.

    Demotes the current latest version and promotes the prior version.
    No binary mutation occurs — only metadata pointer changes.
    """
    metadata_svc = MetadataService(session)
    audit_svc = AuditService(session)

    document = await metadata_svc.get_document(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    try:
        demoted, promoted = await metadata_svc.rollback_version(document_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    await audit_svc.log_event(
        event_type=AuditEventType.DOCUMENT_ROLLBACK,
        user_id=app_user.entra_oid,
        user_principal_name=app_user.email,
        action="rollback",
        result="success",
        resource_type="document",
        resource_id=str(document_id),
        details={
            "rolled_back_version": demoted.version_number,
            "promoted_version": promoted.version_number,
        },
    )

    return RollbackResponse(
        document_id=document_id,
        rolled_back_version=demoted.version_number,
        promoted_version=promoted.version_number,
        new_current_version_id=promoted.id,
    )


# ============================================================================
# System Settings (Admin Only)
# ============================================================================


@router.get("/settings")
async def get_system_settings(
    app_user: Annotated[AppUser, Depends(require_permission("roles", "manage"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict:
    """Get all system settings. Admin only. Sensitive values are masked."""
    svc = SettingsService(session)
    return await svc.get_all()


@router.put("/settings")
async def update_system_settings(
    updates: Annotated[dict[str, str], Body(embed=False)],
    app_user: Annotated[AppUser, Depends(require_permission("roles", "manage"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict:
    """Update system settings. Admin only.

    Accepts a JSON object of {key: value} pairs to update.
    Valid keys: pdf_engine, aspose_words_license, aspose_cells_license,
    aspose_slides_license, malware_scanning_enabled, gotenberg_url
    """
    audit_svc = AuditService(session)
    svc = SettingsService(session)

    valid_keys = {
        "pdf_engine",
        "aspose_words_license",
        "aspose_cells_license",
        "aspose_slides_license",
        "malware_scanning_enabled",
        "gotenberg_url",
    }
    invalid = set(updates.keys()) - valid_keys
    if invalid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid setting keys: {', '.join(invalid)}",
        )

    # Validate pdf_engine value
    if "pdf_engine" in updates and updates["pdf_engine"] not in ("opensource", "aspose"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="pdf_engine must be 'opensource' or 'aspose'",
        )

    await svc.set_many(updates, user_id=app_user.entra_oid)

    await audit_svc.log_event(
        event_type=AuditEventType.USER_ROLE_CHANGED,
        user_id=app_user.entra_oid,
        user_principal_name=app_user.email,
        action="update",
        result="success",
        resource_type="system_settings",
        details={"updated_keys": list(updates.keys())},
    )

    return await svc.get_all()
