"""Synchronous PDF merge service using pypdf."""

import io

import structlog
from pypdf import PdfReader, PdfWriter

logger = structlog.get_logger()


class PdfMergeService:
    """Merges multiple PDF files into a single PDF in-memory."""

    @staticmethod
    def merge_pdfs(pdf_contents: list[bytes]) -> bytes:
        """Merge multiple PDF byte arrays into a single PDF.

        Returns the merged PDF as bytes. Does NOT persist the result.
        """
        writer = PdfWriter()

        for i, content in enumerate(pdf_contents):
            reader = PdfReader(io.BytesIO(content))
            for page in reader.pages:
                writer.add_page(page)
            logger.debug("pdf_merge_added", index=i, pages=len(reader.pages))

        output = io.BytesIO()
        writer.write(output)
        merged_bytes = output.getvalue()

        logger.info(
            "pdf_merge_completed",
            input_count=len(pdf_contents),
            output_size_bytes=len(merged_bytes),
            total_pages=len(writer.pages),
        )

        return merged_bytes
