"""HTTP client for Gotenberg PDF conversion API."""

import logging

import httpx

logger = logging.getLogger("gotenberg_client")

CONVERSION_TIMEOUT = 120  # seconds


class GotenbergClient:
    """Converts Office documents to PDF via Gotenberg's LibreOffice endpoint."""

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    async def convert(self, file_data: bytes, filename: str) -> bytes:
        """Send file to Gotenberg LibreOffice conversion endpoint."""
        url = f"{self._base_url}/forms/libreoffice/convert"

        async with httpx.AsyncClient(timeout=CONVERSION_TIMEOUT) as client:
            response = await client.post(
                url,
                files={"files": (filename, file_data)},
                data={
                    "pdfFormat": "PDF/A-2b",
                    "landscape": "false",
                },
            )

            if response.status_code != 200:
                logger.error(
                    "Gotenberg conversion failed: status=%d, body=%s",
                    response.status_code,
                    response.text[:500],
                )
                raise RuntimeError(
                    f"Gotenberg conversion failed with status {response.status_code}"
                )

            pdf_data = response.content
            logger.info(
                "Gotenberg conversion succeeded: filename=%s, output_size=%d",
                filename,
                len(pdf_data),
            )
            return pdf_data

    async def health_check(self) -> bool:
        """Check if Gotenberg is healthy."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self._base_url}/health")
                return response.status_code == 200
        except Exception:
            return False
