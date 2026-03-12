"""Azure Blob Storage operations for document management."""

import hashlib
import re
from collections.abc import AsyncIterator

import structlog
from azure.storage.blob import BlobServiceClient, ContentSettings

from app.config import settings

logger = structlog.get_logger()

# Allowed characters in filenames: alphanumeric, dots, hyphens, underscores, spaces
_SAFE_FILENAME_RE = re.compile(r"[^a-zA-Z0-9.\-_ ]")


def _sanitize_filename(filename: str) -> str:
    """Sanitize a filename to prevent path traversal and special characters."""
    # Strip path components (handle both / and \)
    filename = filename.replace("\\", "/").split("/")[-1]
    # Remove unsafe characters
    filename = _SAFE_FILENAME_RE.sub("_", filename)
    # Remove leading/trailing dots and spaces
    filename = filename.strip(". ")
    # Fallback if empty
    return filename or "unnamed"


class BlobService:
    """Manages document storage in Azure Blob Storage."""

    def __init__(self, blob_service_client: BlobServiceClient) -> None:
        self._client = blob_service_client
        self._container_name = settings.azure_storage_container_name

    def _get_container_client(self):
        return self._client.get_container_client(self._container_name)

    def build_blob_path(self, record_id: str, file_id: str, filename: str) -> str:
        """Build hierarchical blob path: INVESTIGATION-{RecordId}/{FileId}/blob/{filename}."""
        safe_name = _sanitize_filename(filename)
        return f"{record_id}/{file_id}/blob/{safe_name}"

    def build_pdf_path(self, record_id: str, file_id: str, filename: str) -> str:
        """Build PDF blob path: INVESTIGATION-{RecordId}/{FileId}/pdf/{filename}.pdf."""
        safe_name = _sanitize_filename(filename)
        base_name = safe_name.rsplit(".", 1)[0] if "." in safe_name else safe_name
        return f"{record_id}/{file_id}/pdf/{base_name}.pdf"

    async def upload_blob(
        self,
        blob_path: str,
        data: bytes,
        content_type: str | None = None,
    ) -> tuple[str, str]:
        """Upload a blob and return (blob_url, version_id).

        Also computes SHA-256 checksum of the data.
        """
        container_client = self._get_container_client()
        blob_client = container_client.get_blob_client(blob_path)

        content_settings = ContentSettings(content_type=content_type) if content_type else None

        response = blob_client.upload_blob(
            data,
            overwrite=True,
            content_settings=content_settings,
        )

        version_id = response.get("version_id", "")
        logger.info(
            "blob_uploaded",
            blob_path=blob_path,
            size_bytes=len(data),
            version_id=version_id,
        )

        return blob_client.url, version_id

    async def download_blob(self, blob_path: str, version_id: str | None = None) -> bytes:
        """Download a blob's contents."""
        container_client = self._get_container_client()
        blob_client = container_client.get_blob_client(blob_path)

        download = blob_client.download_blob(version_id=version_id)
        data = download.readall()

        logger.info("blob_downloaded", blob_path=blob_path, size_bytes=len(data))
        return data

    async def stream_blob(self, blob_path: str, version_id: str | None = None) -> AsyncIterator[bytes]:
        """Stream a blob in chunks for large file downloads."""
        container_client = self._get_container_client()
        blob_client = container_client.get_blob_client(blob_path)

        download = blob_client.download_blob(version_id=version_id)
        for chunk in download.chunks():
            yield chunk

    async def list_blob_versions(self, blob_path: str) -> list[dict]:
        """List all versions of a blob."""
        container_client = self._get_container_client()
        versions = []

        blobs = container_client.list_blobs(
            name_starts_with=blob_path,
            include=["versions"],
        )
        for blob in blobs:
            if blob.name == blob_path:
                versions.append(
                    {
                        "version_id": blob.version_id or "",
                        "last_modified": blob.last_modified,
                        "content_length": blob.size,
                        "is_current": blob.is_current_version or False,
                    }
                )

        return sorted(versions, key=lambda v: v["last_modified"], reverse=True)

    async def delete_blob(self, blob_path: str) -> None:
        """Soft-delete a blob."""
        container_client = self._get_container_client()
        blob_client = container_client.get_blob_client(blob_path)
        blob_client.delete_blob(delete_snapshots="include")
        logger.info("blob_deleted", blob_path=blob_path)

    @staticmethod
    def compute_checksum(data: bytes) -> str:
        """Compute SHA-256 checksum of file data."""
        return hashlib.sha256(data).hexdigest()
