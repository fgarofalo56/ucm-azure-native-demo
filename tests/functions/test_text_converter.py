"""Tests for text to PDF converter."""

import pytest

from services.text_converter import TextConverter


class TestTextConverter:
    @pytest.fixture
    def converter(self):
        return TextConverter()

    def test_convert_plain_text(self, converter):
        text = b"Hello, this is a test document.\nLine 2.\nLine 3."
        pdf_data = converter.convert(text, "test.txt")
        assert len(pdf_data) > 0
        assert pdf_data[:4] == b"%PDF"

    def test_convert_utf8_text(self, converter):
        text = "Unicode text: Hello World".encode("utf-8")
        pdf_data = converter.convert(text, "unicode.txt")
        assert len(pdf_data) > 0

    def test_strip_rtf_basic(self, converter):
        rtf = r"{\rtf1\ansi Hello \b World}"
        result = converter._strip_rtf(rtf)
        assert "Hello" in result
        assert "World" in result
        assert "\\rtf" not in result
