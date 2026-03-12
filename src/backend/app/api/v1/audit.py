"""Audit log query endpoint (admin only)."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AppUser
from app.db.session import get_db_session
from app.middleware.auth import require_permission
from app.models.schemas import AuditLogEntry, AuditLogQuery, PaginatedResponse
from app.services.audit_service import AuditService

router = APIRouter()


@router.post("/logs", response_model=PaginatedResponse)
async def query_audit_logs(
    query: AuditLogQuery,
    app_user: Annotated[AppUser, Depends(require_permission("audit", "read"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PaginatedResponse:
    """Query audit logs with filters. Requires audit.read permission."""
    audit_svc = AuditService(session)

    entries, total = await audit_svc.query_audit_logs(
        event_type=query.event_type,
        user_id=query.user_id,
        resource_id=query.resource_id,
        start_date=query.start_date,
        end_date=query.end_date,
        page=query.page,
        page_size=query.page_size,
    )

    return PaginatedResponse(
        data=[AuditLogEntry.model_validate(e) for e in entries],
        meta={"page": query.page, "page_size": query.page_size, "total": total},
    )
