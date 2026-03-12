"""Tests for Gotenberg HTTP client."""

import pytest
from unittest.mock import AsyncMock, patch

from services.gotenberg_client import GotenbergClient


class TestGotenbergClient:
    @pytest.fixture
    def client(self):
        return GotenbergClient("http://localhost:3000")

    @pytest.mark.asyncio
    async def test_convert_success(self, client):
        """Test successful conversion via Gotenberg API."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.content = b"%PDF-1.4 test pdf content"

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            result = await client.convert(b"file content", "test.docx")
            assert result == b"%PDF-1.4 test pdf content"

    @pytest.mark.asyncio
    async def test_convert_failure(self, client):
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(RuntimeError, match="Gotenberg conversion failed"):
                await client.convert(b"file content", "test.docx")
