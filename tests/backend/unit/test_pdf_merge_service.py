"""Unit tests for PdfMergeService."""

import io

import pytest
from pypdf import PdfWriter

from app.services.pdf_merge_service import PdfMergeService


def _create_test_pdf(num_pages: int = 1) -> bytes:
    """Create a minimal valid PDF for testing."""
    writer = PdfWriter()
    for _ in range(num_pages):
        writer.add_blank_page(width=612, height=792)
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


class TestPdfMergeService:
    def test_merge_two_pdfs(self):
        pdf1 = _create_test_pdf(2)
        pdf2 = _create_test_pdf(3)

        result = PdfMergeService.merge_pdfs([pdf1, pdf2])

        assert len(result) > 0
        # Verify it's a valid PDF
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(result))
        assert len(reader.pages) == 5

    def test_merge_single_pdf(self):
        pdf = _create_test_pdf(1)
        result = PdfMergeService.merge_pdfs([pdf])
        assert len(result) > 0

    def test_merge_empty_list(self):
        result = PdfMergeService.merge_pdfs([])
        # Should produce a valid but empty PDF
        assert len(result) > 0
