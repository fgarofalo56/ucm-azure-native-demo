"""Tests for image to PDF converter."""

import io
import pytest
from PIL import Image

from services.image_converter import ImageConverter


class TestImageConverter:
    @pytest.fixture
    def converter(self):
        return ImageConverter()

    def _create_test_image(self, format: str = "PNG") -> bytes:
        """Create a minimal test image."""
        img = Image.new("RGB", (100, 100), color="red")
        output = io.BytesIO()
        img.save(output, format=format)
        return output.getvalue()

    def test_convert_png(self, converter):
        image_data = self._create_test_image("PNG")
        pdf_data = converter.convert(image_data, "image/png")
        assert len(pdf_data) > 0
        assert pdf_data[:4] == b"%PDF"

    def test_convert_jpeg(self, converter):
        image_data = self._create_test_image("JPEG")
        pdf_data = converter.convert(image_data, "image/jpeg")
        assert len(pdf_data) > 0

    def test_convert_bmp(self, converter):
        image_data = self._create_test_image("BMP")
        pdf_data = converter.convert(image_data, "image/bmp")
        assert len(pdf_data) > 0
