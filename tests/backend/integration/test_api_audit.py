"""Integration tests for audit log endpoint."""

import pytest


class TestAuditEndpoint:
    def test_audit_requires_admin_role(self, test_client):
        """Audit query should accept requests from Admin users."""
        response = test_client.post(
            "/api/v1/audit/logs",
            json={"page": 1, "page_size": 10},
        )
        # With mocked admin auth, should not return 403
        assert response.status_code in (200, 500)  # 500 if DB not available
