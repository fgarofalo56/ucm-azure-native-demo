"""Unit tests for MetadataService."""

import pytest
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
        mock_db_session.add.assert_called()
        mock_db_session.flush.assert_called()

    @pytest.mark.asyncio
    async def test_create_document_with_version(self, metadata_service, mock_db_session):
        investigation_id = uuid4()
        document, version = await metadata_service.create_document_with_version(
            investigation_id=investigation_id,
            original_filename="test.docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            file_size_bytes=1024,
            blob_path_original="INVESTIGATION-123/file-abc/original/v1/test.docx",
            checksum="abc123",
            user_id="user-123",
            user_name="Test User",
        )
        assert mock_db_session.add.call_count >= 2  # document + version

    @pytest.mark.asyncio
    async def test_update_version_pdf_status(self, metadata_service, mock_db_session):
        version_id = uuid4()
        await metadata_service.update_version_pdf_status(
            version_id=version_id,
            status=PdfConversionStatus.COMPLETED,
            pdf_path="INVESTIGATION-123/file-abc/pdf/v1/test.pdf",
        )
        mock_db_session.execute.assert_called_once()
