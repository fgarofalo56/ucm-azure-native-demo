"""Shared test fixtures with mock Azure clients."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.config import Settings


@pytest.fixture
def mock_settings():
    return Settings(
        environment="test",
        azure_storage_account_name="teststorage",
        azure_storage_container_name="test-container",
        azure_sql_server="localhost",
        azure_sql_database="testdb",
        entra_tenant_id="test-tenant",
        entra_client_id="test-client",
        entra_audience="api://test",
    )


@pytest.fixture
def mock_blob_service_client():
    client = MagicMock()
    container = MagicMock()
    blob = MagicMock()

    client.get_container_client.return_value = container
    container.get_blob_client.return_value = blob
    blob.upload_blob.return_value = {"version_id": "v1"}
    blob.url = "https://teststorage.blob.core.windows.net/test/path"

    download = MagicMock()
    download.readall.return_value = b"test file content"
    blob.download_blob.return_value = download

    return client


@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def mock_user_claims():
    from app.middleware.auth import UserClaims
    return UserClaims(
        oid=str(uuid4()),
        name="Test User",
        preferred_username="test@example.com",
        roles=["Documents.Contributor", "Investigations.Manager"],
        tid="test-tenant",
    )


@pytest.fixture
def test_client():
    """Create a FastAPI test client with mocked dependencies."""
    from app.main import app
    from app.middleware.auth import validate_token, UserClaims

    async def mock_validate_token():
        return UserClaims(
            oid="test-user-id",
            name="Test User",
            preferred_username="test@example.com",
            roles=["Documents.Contributor", "Investigations.Manager", "Admin"],
            tid="test-tenant",
        )

    app.dependency_overrides[validate_token] = mock_validate_token
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
