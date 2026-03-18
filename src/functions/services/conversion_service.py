"""Routes files to the correct PDF conversion engine.

Uses the pluggable PdfConverter abstraction from pdf_engine.py.
Default engine: Aspose (production). Fallback: Gotenberg (demo).
Engine selection is configuration-driven via PDF_ENGINE env var.
"""

import logging

from services.pdf_engine import PdfConverter, get_pdf_engine

logger = logging.getLogger("conversion_service")


class ConversionService:
    """Routes file conversion to the configured PDF engine."""

    def __init__(self, engine: PdfConverter | None = None) -> None:
        self._engine = engine or get_pdf_engine()

    async def convert_to_pdf(
        self, file_data: bytes, filename: str, content_type: str
    ) -> bytes:
        """Convert a file to PDF using the configured engine."""
        if not self._engine.supports(content_type):
            logger.warning(
                "Content type not explicitly supported, attempting conversion: %s (%s)",
                filename,
                content_type,
            )

        return await self._engine.convert(file_data, filename, content_type)
