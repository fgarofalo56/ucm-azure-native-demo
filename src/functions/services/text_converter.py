"""Plain text and RTF to PDF conversion using fpdf2."""

import logging

from fpdf import FPDF

logger = logging.getLogger("text_converter")


class TextConverter:
    """Converts plain text and RTF files to PDF."""

    def convert(self, file_data: bytes, filename: str) -> bytes:
        """Convert text content to PDF."""
        # Decode text content
        try:
            text = file_data.decode("utf-8")
        except UnicodeDecodeError:
            text = file_data.decode("latin-1")

        # Strip RTF markup if RTF file
        if filename.lower().endswith(".rtf"):
            text = self._strip_rtf(text)

        return self._text_to_pdf(text, filename)

    @staticmethod
    def _text_to_pdf(text: str, filename: str) -> bytes:
        """Render plain text as a PDF document."""
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Courier", size=10)

        # Add title
        pdf.set_font("Helvetica", "B", size=12)
        pdf.cell(0, 10, filename, ln=True)
        pdf.ln(5)

        # Add text content line by line
        pdf.set_font("Courier", size=10)
        w = pdf.w - pdf.l_margin - pdf.r_margin
        for line in text.split("\n"):
            if line.strip():
                pdf.multi_cell(w, 5, line)
            else:
                pdf.ln(5)

        output = pdf.output()
        logger.info("Text conversion completed: filename=%s, pdf_size=%d", filename, len(output))
        return bytes(output)

    @staticmethod
    def _strip_rtf(text: str) -> str:
        """Basic RTF markup stripping (extracts plain text content)."""
        result = []
        in_group = 0
        i = 0
        while i < len(text):
            char = text[i]
            if char == "{":
                in_group += 1
            elif char == "}":
                in_group -= 1
            elif char == "\\" and i + 1 < len(text):
                next_char = text[i + 1]
                if next_char == "\n":
                    result.append("\n")
                    i += 1
                elif next_char in ("\\", "{", "}"):
                    result.append(next_char)
                    i += 1
                else:
                    # Skip control word
                    j = i + 1
                    while j < len(text) and text[j].isalpha():
                        j += 1
                    if j < len(text) and text[j] == " ":
                        j += 1
                    i = j - 1
            elif in_group <= 1:
                result.append(char)
            i += 1
        return "".join(result)
