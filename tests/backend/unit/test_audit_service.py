"""Unit tests for AuditService."""

import pytest
from unittest.mock import AsyncMock

from app.services.audit_service import AuditService


@pytest.fixture
def audit_service(mock_db_session):
    return AuditService(mock_db_session)


class TestAuditService:
    @pytest.mark.asyncio
    async def test_log_event(self, audit_service, mock_db_session):
        entry = await audit_service.log_event(
            event_type="document.upload",
            user_id="user-123",
            action="create",
            result="success",
            resource_type="document",
            resource_id="file-abc",
            details={"filename": "test.pdf", "size": 1024},
            correlation_id="corr-123",
        )
        mock_db_session.add.assert_called_once()
        mock_db_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_log_event_minimal(self, audit_service, mock_db_session):
        entry = await audit_service.log_event(
            event_type="auth.login",
            user_id="user-123",
            action="create",
            result="success",
        )
        mock_db_session.add.assert_called_once()
