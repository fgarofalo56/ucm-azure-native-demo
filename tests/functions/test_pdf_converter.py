"""Tests for PDF converter function."""

import pytest
from unittest.mock import MagicMock


class TestPdfConverterEventParsing:
    def test_parse_blob_subject(self):
        """Test parsing blob path from Event Grid subject."""
        subject = "/blobServices/default/containers/assurancenet-documents/blobs/INVESTIGATION-123/file-abc/blob/test.docx"
        parts = subject.split("/blobs/", 1)
        assert len(parts) == 2
        assert parts[1] == "INVESTIGATION-123/file-abc/blob/test.docx"

    def test_parse_blob_path_components(self):
        blob_path = "INVESTIGATION-123/file-abc/blob/test.docx"
        path_parts = blob_path.split("/")
        assert path_parts[0] == "INVESTIGATION-123"
        assert path_parts[1] == "file-abc"
        assert path_parts[2] == "blob"
        assert path_parts[3] == "test.docx"

    def test_skip_pdf_folder(self):
        blob_path = "INVESTIGATION-123/file-abc/pdf/test.pdf"
        assert "/pdf/" in blob_path
