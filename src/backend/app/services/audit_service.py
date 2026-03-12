"""Audit log recording and querying service (NIST 800-53 AU-2/AU-3)."""

import json
from datetime import datetime

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AuditLog

logger = structlog.get_logger()


class AuditService:
    """Records and queries audit log entries for compliance."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def log_event(
        self,
        event_type: str,
        user_id: str,
        action: str,
        result: str,
        user_principal_name: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        details: dict | None = None,
        correlation_id: str | None = None,
        session_id: str | None = None,
    ) -> AuditLog:
        """Record an audit event to the database."""
        entry = AuditLog(
            event_type=event_type,
            event_timestamp=datetime.utcnow(),
            user_id=user_id,
            user_principal_name=user_principal_name,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            result=result,
            details=json.dumps(details) if details else None,
            correlation_id=correlation_id,
            session_id=session_id,
        )
        self._session.add(entry)
        await self._session.flush()

        logger.info(
            "audit_event_recorded",
            event_type=event_type,
            user_id=user_id,
            action=action,
            result=result,
            resource_id=resource_id,
        )
        return entry

    async def query_audit_logs(
        self,
        event_type: str | None = None,
        user_id: str | None = None,
        resource_id: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[AuditLog], int]:
        """Query audit logs with optional filters."""
        query = select(AuditLog)
        count_query = select(func.count()).select_from(AuditLog)

        if event_type:
            query = query.where(AuditLog.event_type == event_type)
            count_query = count_query.where(AuditLog.event_type == event_type)
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
            count_query = count_query.where(AuditLog.user_id == user_id)
        if resource_id:
            query = query.where(AuditLog.resource_id == resource_id)
            count_query = count_query.where(AuditLog.resource_id == resource_id)
        if start_date:
            query = query.where(AuditLog.event_timestamp >= start_date)
            count_query = count_query.where(AuditLog.event_timestamp >= start_date)
        if end_date:
            query = query.where(AuditLog.event_timestamp <= end_date)
            count_query = count_query.where(AuditLog.event_timestamp <= end_date)

        total = (await self._session.execute(count_query)).scalar() or 0
        result = await self._session.execute(
            query.order_by(AuditLog.event_timestamp.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total
