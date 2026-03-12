"""Unit tests for BlobService."""

import pytest
from unittest.mock import MagicMock

from app.services.blob_service import BlobService


@pytest.fixture
def blob_service(mock_blob_service_client):
    return BlobService(mock_blob_service_client)


class TestBlobService:
    def test_build_blob_path(self, blob_service):
        path = blob_service.build_blob_path("INVESTIGATION-123", "file-abc", "report.docx")
        assert path == "INVESTIGATION-123/file-abc/blob/report.docx"

    def test_build_pdf_path(self, blob_service):
        path = blob_service.build_pdf_path("INVESTIGATION-123", "file-abc", "report.docx")
        assert path == "INVESTIGATION-123/file-abc/pdf/report.pdf"

    def test_build_pdf_path_no_extension(self, blob_service):
        path = blob_service.build_pdf_path("INVESTIGATION-123", "file-abc", "report")
        assert path == "INVESTIGATION-123/file-abc/pdf/report.pdf"

    def test_compute_checksum(self):
        data = b"hello world"
        checksum = BlobService.compute_checksum(data)
        assert len(checksum) == 64
        assert checksum == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

    @pytest.mark.asyncio
    async def test_upload_blob(self, blob_service, mock_blob_service_client):
        url, version_id = await blob_service.upload_blob(
            "test/path/file.txt", b"content", "text/plain"
        )
        assert version_id == "v1"

    @pytest.mark.asyncio
    async def test_download_blob(self, blob_service):
        data = await blob_service.download_blob("test/path/file.txt")
        assert data == b"test file content"

    @pytest.mark.asyncio
    async def test_delete_blob(self, blob_service, mock_blob_service_client):
        await blob_service.delete_blob("test/path/file.txt")
        container = mock_blob_service_client.get_container_client.return_value
        blob = container.get_blob_client.return_value
        blob.delete_blob.assert_called_once()
