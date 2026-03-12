"""Routes files to the correct PDF conversion method."""

import logging

from services.gotenberg_client import GotenbergClient
from services.image_converter import ImageConverter
from services.text_converter import TextConverter

logger = logging.getLogger("conversion_service")

# Content type routing
IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/tiff", "image/bmp"}
TEXT_TYPES = {"text/plain", "text/rtf", "application/rtf"}
OFFICE_TYPES = {
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.visio",
    "application/vnd.ms-visio.drawing",
    "application/x-mspublisher",
}


class ConversionService:
    """Routes file conversion to the appropriate handler."""

    def __init__(self, gotenberg_url: str) -> None:
        self._gotenberg = GotenbergClient(gotenberg_url)
        self._image_converter = ImageConverter()
        self._text_converter = TextConverter()

    async def convert_to_pdf(
        self, file_data: bytes, filename: str, content_type: str
    ) -> bytes:
        """Convert a file to PDF using the appropriate method."""
        if content_type == "application/pdf":
            logger.info("File is already PDF, passthrough: %s", filename)
            return file_data

        if content_type in IMAGE_TYPES:
            logger.info("Using image converter for: %s (%s)", filename, content_type)
            return self._image_converter.convert(file_data, content_type)

        if content_type in TEXT_TYPES:
            logger.info("Using text converter for: %s (%s)", filename, content_type)
            return self._text_converter.convert(file_data, filename)

        if content_type in OFFICE_TYPES:
            logger.info("Using Gotenberg for: %s (%s)", filename, content_type)
            return await self._gotenberg.convert(file_data, filename)

        # Unknown type - attempt Gotenberg as fallback
        logger.warning(
            "Unknown content type, attempting Gotenberg: %s (%s)", filename, content_type
        )
        return await self._gotenberg.convert(file_data, filename)
