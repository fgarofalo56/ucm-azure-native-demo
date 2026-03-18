"""Pluggable PDF conversion engine abstraction.

Default engine: Aspose (production-grade, licensed).
Fallback engine: Gotenberg (demo/OSS).

Engine selected via PDF_ENGINE env var. No code redeployment required.

Usage:
    engine = get_pdf_engine()
    pdf_bytes = await engine.convert(file_data, filename, content_type)
"""

import io
import logging
import os
from typing import Protocol

from services.image_converter import ImageConverter
from services.text_converter import TextConverter

logger = logging.getLogger("pdf_engine")

# Content type routing (shared across all engines)
IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/tiff", "image/bmp"}
TEXT_TYPES = {"text/plain", "text/rtf", "application/rtf"}

WORD_TYPES = {
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
EXCEL_TYPES = {
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
POWERPOINT_TYPES = {
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}
VISIO_TYPES = {
    "application/vnd.visio",
    "application/vnd.ms-visio.drawing",
    "application/x-mspublisher",
}

OFFICE_TYPES = WORD_TYPES | EXCEL_TYPES | POWERPOINT_TYPES | VISIO_TYPES
ALL_SUPPORTED_TYPES = IMAGE_TYPES | TEXT_TYPES | OFFICE_TYPES | {"application/pdf"}


class PdfConverter(Protocol):
    """Protocol for pluggable PDF conversion engines."""

    def supports(self, mime_type: str) -> bool:
        """Return True if this engine can convert the given MIME type."""
        ...

    async def convert(self, input_data: bytes, filename: str, mime_type: str) -> bytes:
        """Convert input file data to PDF bytes."""
        ...


class AsposeEngine:
    """PDF conversion engine using Aspose SDKs (production-licensed).

    Uses aspose.words for Word/RTF/HTML, aspose.cells for Excel,
    and aspose.slides for PowerPoint. Images and plain text use
    the built-in converters (Pillow/fpdf2).
    """

    def __init__(self) -> None:
        self._image_converter = ImageConverter()
        self._text_converter = TextConverter()

    def supports(self, mime_type: str) -> bool:
        return mime_type in ALL_SUPPORTED_TYPES

    async def convert(self, input_data: bytes, filename: str, mime_type: str) -> bytes:
        if mime_type == "application/pdf":
            logger.info("File is already PDF, passthrough: %s", filename)
            return input_data

        if mime_type in IMAGE_TYPES:
            logger.info("Using image converter for: %s (%s)", filename, mime_type)
            return self._image_converter.convert(input_data, mime_type)

        if mime_type in TEXT_TYPES:
            logger.info("Using text converter for: %s (%s)", filename, mime_type)
            return self._text_converter.convert(input_data, filename)

        if mime_type in WORD_TYPES:
            logger.info("Using Aspose.Words for: %s (%s)", filename, mime_type)
            return self._convert_word(input_data, filename)

        if mime_type in EXCEL_TYPES:
            logger.info("Using Aspose.Cells for: %s (%s)", filename, mime_type)
            return self._convert_excel(input_data, filename)

        if mime_type in POWERPOINT_TYPES:
            logger.info("Using Aspose.Slides for: %s (%s)", filename, mime_type)
            return self._convert_slides(input_data, filename)

        if mime_type in VISIO_TYPES:
            # Visio/Publisher — fall back to Aspose.Words (handles some formats)
            logger.info("Using Aspose.Words fallback for: %s (%s)", filename, mime_type)
            return self._convert_word(input_data, filename)

        logger.warning("Unknown content type, attempting Aspose.Words: %s (%s)", filename, mime_type)
        return self._convert_word(input_data, filename)

    @staticmethod
    def _convert_word(input_data: bytes, filename: str) -> bytes:
        """Convert Word/RTF/HTML documents to PDF via aspose.words."""
        import aspose.words as aw

        doc = aw.Document(io.BytesIO(input_data))
        output = io.BytesIO()
        doc.save(output, aw.SaveFormat.PDF)
        pdf_data = output.getvalue()

        logger.info(
            "Aspose.Words conversion completed: filename=%s, output_size=%d",
            filename, len(pdf_data),
        )
        return pdf_data

    @staticmethod
    def _convert_excel(input_data: bytes, filename: str) -> bytes:
        """Convert Excel spreadsheets to PDF via aspose.cells."""
        import aspose.cells as ac

        workbook = ac.Workbook(io.BytesIO(input_data))
        output = io.BytesIO()
        workbook.save(output, ac.SaveFormat.PDF)
        pdf_data = output.getvalue()

        logger.info(
            "Aspose.Cells conversion completed: filename=%s, output_size=%d",
            filename, len(pdf_data),
        )
        return pdf_data

    @staticmethod
    def _convert_slides(input_data: bytes, filename: str) -> bytes:
        """Convert PowerPoint presentations to PDF via aspose.slides."""
        import aspose.slides as slides

        with slides.Presentation(io.BytesIO(input_data)) as pres:
            output = io.BytesIO()
            pres.save(output, slides.export.SaveFormat.PDF)
            pdf_data = output.getvalue()

        logger.info(
            "Aspose.Slides conversion completed: filename=%s, output_size=%d",
            filename, len(pdf_data),
        )
        return pdf_data


class GotenbergEngine:
    """PDF conversion engine using Gotenberg (demo/OSS fallback).

    Requires a running Gotenberg container. Use for environments
    without Aspose licenses.
    """

    def __init__(self, gotenberg_url: str) -> None:
        from services.gotenberg_client import GotenbergClient

        self._gotenberg = GotenbergClient(gotenberg_url)
        self._image_converter = ImageConverter()
        self._text_converter = TextConverter()

    def supports(self, mime_type: str) -> bool:
        return mime_type in ALL_SUPPORTED_TYPES

    async def convert(self, input_data: bytes, filename: str, mime_type: str) -> bytes:
        if mime_type == "application/pdf":
            logger.info("File is already PDF, passthrough: %s", filename)
            return input_data

        if mime_type in IMAGE_TYPES:
            logger.info("Using image converter for: %s (%s)", filename, mime_type)
            return self._image_converter.convert(input_data, mime_type)

        if mime_type in TEXT_TYPES:
            logger.info("Using text converter for: %s (%s)", filename, mime_type)
            return self._text_converter.convert(input_data, filename)

        if mime_type in OFFICE_TYPES:
            logger.info("Using Gotenberg for: %s (%s)", filename, mime_type)
            return await self._gotenberg.convert(input_data, filename)

        logger.warning("Unknown content type, attempting Gotenberg: %s (%s)", filename, mime_type)
        return await self._gotenberg.convert(input_data, filename)


def get_pdf_engine() -> PdfConverter:
    """Factory: return the configured PDF conversion engine.

    Engine selection via PDF_ENGINE env var: "aspose" (default) or "gotenberg".
    """
    engine_name = os.environ.get("PDF_ENGINE", "aspose").lower()

    if engine_name == "gotenberg":
        gotenberg_url = os.environ.get("GOTENBERG_URL", "http://ca-gotenberg-dev:3000")
        logger.info("Using Gotenberg PDF engine at %s", gotenberg_url)
        return GotenbergEngine(gotenberg_url)

    logger.info("Using Aspose PDF engine")
    return AsposeEngine()
