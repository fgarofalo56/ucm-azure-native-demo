"""Unit tests for MetadataService."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.metadata_service import MetadataService
from app.models.enums import PdfConversionStatus


@pytest.fixture
def metadata_service(mock_db_session):
    return MetadataService(mock_db_session)


class TestMetadataService:
    @pytest.mark.asyncio
    async def test_create_investigation(self, metadata_service, mock_db_session):
        investigation = await metadata_service.create_investigation(
            record_id="INVESTIGATION-12345",
            title="Test Investigation",
            description="Test description",
            user_id="user-123",
            user_name="Test User",
        )
        mock_db_session.add.assert_called_once()
        mock_db_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_document(self, metadata_service, mock_db_session):
        investigation_id = uuid4()
        document = await metadata_service.create_document(
            investigation_id=investigation_id,
            file_id="file-abc",
            original_filename="test.docx",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            file_size_bytes=1024,
            blob_path="INVESTIGATION-123/file-abc/blob/test.docx",
            blob_version_id="v1",
            checksum_sha256="abc123",
            user_id="user-123",
            user_name="Test User",
        )
        mock_db_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_pdf_status(self, metadata_service, mock_db_session):
        await metadata_service.update_pdf_status(
            file_id="file-abc",
            status=PdfConversionStatus.COMPLETED,
            pdf_path="INVESTIGATION-123/file-abc/pdf/test.pdf",
        )
        mock_db_session.execute.assert_called_once()
