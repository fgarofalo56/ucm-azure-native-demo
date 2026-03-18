"""In-process PDF conversion service for the backend API.

Converts uploaded documents to PDF synchronously during upload.
Uses lightweight converters (Pillow for images, fpdf2 for text).
Office format conversion requires Aspose SDK — falls back to marking
as 'pending' if Aspose is not installed.

This replaces the Azure Functions pipeline for environments without
separate compute (e.g., Container Apps with no Functions quota).
"""

import io
import logging

import structlog

logger = structlog.get_logger()

# Content type sets
IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/tiff", "image/bmp"}
TEXT_TYPES = {"text/plain", "text/csv", "text/rtf", "application/rtf"}
OFFICE_TYPES = {
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}


def convert_to_pdf(file_data: bytes, filename: str, content_type: str | None) -> bytes | None:
    """Convert a file to PDF in-process. Returns PDF bytes or None if unsupported.

    Supports: images (Pillow + img2pdf), text/CSV (fpdf2), Office (Aspose if installed).
    Returns None for unsupported types (caller should mark as 'pending' for async pipeline).
    """
    if not content_type:
        return None

    if content_type == "application/pdf":
        return None  # Already PDF

    if content_type in IMAGE_TYPES:
        return _convert_image(file_data, content_type)

    if content_type in TEXT_TYPES:
        return _convert_text(file_data, filename)

    if content_type in OFFICE_TYPES:
        return _convert_office(file_data, filename, content_type)

    logger.info("pdf_conversion_unsupported", content_type=content_type, filename=filename)
    return None


def _convert_image(file_data: bytes, content_type: str) -> bytes | None:
    """Convert image to PDF using Pillow."""
    try:
        from PIL import Image

        image = Image.open(io.BytesIO(file_data))
        if image.mode in ("RGBA", "P", "LA"):
            image = image.convert("RGB")

        output = io.BytesIO()
        image.save(output, format="PDF", resolution=image.info.get("dpi", (300, 300))[0])
        pdf_data = output.getvalue()
        logger.info("pdf_image_converted", size=len(pdf_data))
        return pdf_data
    except ImportError:
        logger.warning("pillow_not_installed")
        return None
    except Exception as e:
        logger.error("pdf_image_conversion_failed", error=str(e))
        return None


def _convert_text(file_data: bytes, filename: str) -> bytes | None:
    """Convert text/CSV to PDF using fpdf2."""
    try:
        from fpdf import FPDF

        try:
            text = file_data.decode("utf-8")
        except UnicodeDecodeError:
            text = file_data.decode("latin-1")

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_font("Helvetica", "B", size=12)
        pdf.cell(0, 10, filename, ln=True)
        pdf.ln(5)

        pdf.set_font("Courier", size=8)
        w = pdf.w - pdf.l_margin - pdf.r_margin
        for line in text.split("\n")[:2000]:  # Cap at 2000 lines for demo
            if line.strip():
                pdf.multi_cell(w, 4, line)
            else:
                pdf.ln(4)

        output = pdf.output()
        pdf_data = bytes(output)
        logger.info("pdf_text_converted", filename=filename, size=len(pdf_data))
        return pdf_data
    except ImportError:
        logger.warning("fpdf2_not_installed")
        return None
    except Exception as e:
        logger.error("pdf_text_conversion_failed", error=str(e))
        return None


def _convert_office(file_data: bytes, filename: str, content_type: str) -> bytes | None:
    """Convert Office documents to PDF using Aspose (if installed)."""
    try:
        if content_type in {
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }:
            import aspose.words as aw
            doc = aw.Document(io.BytesIO(file_data))
            output = io.BytesIO()
            doc.save(output, aw.SaveFormat.PDF)
            return output.getvalue()

        if content_type in {
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }:
            import aspose.cells as ac
            wb = ac.Workbook(io.BytesIO(file_data))
            output = io.BytesIO()
            wb.save(output, ac.SaveFormat.PDF)
            return output.getvalue()

        if content_type in {
            "application/vnd.ms-powerpoint",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        }:
            import aspose.slides as slides
            with slides.Presentation(io.BytesIO(file_data)) as pres:
                output = io.BytesIO()
                pres.save(output, slides.export.SaveFormat.PDF)
                return output.getvalue()

    except ImportError:
        logger.info("aspose_not_installed", content_type=content_type)
        return None
    except Exception as e:
        logger.error("pdf_office_conversion_failed", error=str(e), content_type=content_type)
        return None

    return None
