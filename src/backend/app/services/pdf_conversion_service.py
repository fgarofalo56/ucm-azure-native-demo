"""In-process PDF conversion service with dual engine support.

Engines:
  - "opensource" (default): Pillow for images, fpdf2 for text/CSV
  - "aspose" (licensed): Aspose.Words/Cells/Slides for Office + all of opensource

Engine selection is stored in system_settings DB table, configurable
via the admin settings UI. Aspose license keys are also stored there.

For Office formats (DOCX/XLSX/PPTX):
  - If engine=aspose and license is provided: uses Aspose SDK
  - If engine=opensource and gotenberg_url is set: uses Gotenberg HTTP API
  - Otherwise: marks as 'pending' (manual conversion needed)
"""

import io

import structlog

logger = structlog.get_logger()

# Content type sets
IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/tiff", "image/bmp"}
TEXT_TYPES = {"text/plain", "text/csv", "text/rtf", "application/rtf"}

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
OFFICE_TYPES = WORD_TYPES | EXCEL_TYPES | POWERPOINT_TYPES


def convert_to_pdf(
    file_data: bytes,
    filename: str,
    content_type: str | None,
    engine: str = "opensource",
    gotenberg_url: str = "",
    aspose_words_license: str = "",
    aspose_cells_license: str = "",
    aspose_slides_license: str = "",
) -> bytes | None:
    """Convert a file to PDF. Returns PDF bytes or None if unsupported.

    Args:
        engine: "opensource" or "aspose"
        gotenberg_url: Optional Gotenberg URL for Office fallback
        aspose_*_license: License keys for Aspose SDKs
    """
    if not content_type or content_type == "application/pdf":
        return None

    if content_type in IMAGE_TYPES:
        return _convert_image(file_data, content_type)

    if content_type in TEXT_TYPES:
        return _convert_text(file_data, filename)

    if content_type in OFFICE_TYPES:
        if engine == "aspose":
            result = _convert_office_aspose(
                file_data,
                filename,
                content_type,
                aspose_words_license,
                aspose_cells_license,
                aspose_slides_license,
            )
            if result:
                return result

        # Gotenberg fallback for Office types
        if gotenberg_url:
            result = _convert_office_gotenberg(file_data, filename, gotenberg_url)
            if result:
                return result

        logger.info("office_conversion_unavailable", filename=filename, engine=engine)
        return None

    return None


def _convert_image(file_data: bytes, content_type: str) -> bytes | None:
    try:
        from PIL import Image

        image = Image.open(io.BytesIO(file_data))
        if image.mode in ("RGBA", "P", "LA"):
            image = image.convert("RGB")  # type: ignore[assignment]

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
        pdf.cell(0, 10, filename, ln=True)  # type: ignore[arg-type]
        pdf.ln(5)

        pdf.set_font("Courier", size=8)
        w = pdf.w - pdf.l_margin - pdf.r_margin
        for line in text.split("\n")[:2000]:
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


def _convert_office_aspose(
    file_data: bytes,
    filename: str,
    content_type: str,
    words_license: str,
    cells_license: str,
    slides_license: str,
) -> bytes | None:
    """Convert Office documents using Aspose SDK with license activation."""
    try:
        if content_type in WORD_TYPES:
            import aspose.words as aw

            if words_license:
                lic = aw.License()
                lic.set_license(io.BytesIO(words_license.encode()))
            doc = aw.Document(io.BytesIO(file_data))
            output = io.BytesIO()
            doc.save(output, aw.SaveFormat.PDF)
            logger.info("aspose_words_converted", filename=filename)
            return output.getvalue()

        if content_type in EXCEL_TYPES:
            import aspose.cells as ac

            if cells_license:
                lic = ac.License()
                lic.set_license(io.BytesIO(cells_license.encode()))
            wb = ac.Workbook(io.BytesIO(file_data))
            output = io.BytesIO()
            wb.save(output, ac.SaveFormat.PDF)
            logger.info("aspose_cells_converted", filename=filename)
            return output.getvalue()

        if content_type in POWERPOINT_TYPES:
            import aspose.slides as slides

            if slides_license:
                lic = slides.License()
                lic.set_license(io.BytesIO(slides_license.encode()))
            with slides.Presentation(io.BytesIO(file_data)) as pres:
                output = io.BytesIO()
                pres.save(output, slides.export.SaveFormat.PDF)
                logger.info("aspose_slides_converted", filename=filename)
                return output.getvalue()

    except ImportError as e:
        logger.info("aspose_sdk_not_installed", error=str(e), content_type=content_type)
        return None
    except Exception as e:
        logger.error("aspose_conversion_failed", error=str(e), filename=filename)
        return None

    return None


def _convert_office_gotenberg(file_data: bytes, filename: str, gotenberg_url: str) -> bytes | None:
    """Convert Office documents via Gotenberg HTTP API (synchronous)."""
    try:
        import httpx

        url = f"{gotenberg_url.rstrip('/')}/forms/libreoffice/convert"
        response = httpx.post(
            url,
            files={"files": (filename, file_data)},
            data={"pdfFormat": "PDF/A-2b"},
            timeout=120,
        )
        if response.status_code == 200:
            logger.info("gotenberg_converted", filename=filename, size=len(response.content))
            return response.content

        logger.error("gotenberg_failed", status=response.status_code, filename=filename)
        return None
    except Exception as e:
        logger.error("gotenberg_conversion_error", error=str(e), filename=filename)
        return None
