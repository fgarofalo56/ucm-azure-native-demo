"""Image to PDF conversion using Pillow + img2pdf."""

import io
import logging

from PIL import Image
import img2pdf

logger = logging.getLogger("image_converter")


class ImageConverter:
    """Converts image files (JPEG, PNG, TIFF, BMP, GIF) to PDF."""

    def convert(self, file_data: bytes, content_type: str) -> bytes:
        """Convert an image to PDF preserving original resolution."""
        # For JPEG, PNG - img2pdf handles them losslessly
        if content_type in ("image/jpeg", "image/png"):
            try:
                pdf_data = img2pdf.convert(file_data)
                logger.info("img2pdf conversion completed, size=%d", len(pdf_data))
                return pdf_data
            except Exception as e:
                logger.warning("img2pdf failed, falling back to Pillow: %s", e, exc_info=True)

        # For TIFF, BMP, GIF or img2pdf fallback - use Pillow
        return self._convert_with_pillow(file_data)

    @staticmethod
    def _convert_with_pillow(file_data: bytes) -> bytes:
        """Convert image to PDF using Pillow."""
        image = Image.open(io.BytesIO(file_data))

        # Convert to RGB if necessary (RGBA, P modes can't save directly to PDF)
        if image.mode in ("RGBA", "P", "LA"):
            image = image.convert("RGB")

        output = io.BytesIO()
        image.save(output, format="PDF", resolution=image.info.get("dpi", (300, 300))[0])
        pdf_data = output.getvalue()

        logger.info("Pillow conversion completed, size=%d", len(pdf_data))
        return pdf_data
