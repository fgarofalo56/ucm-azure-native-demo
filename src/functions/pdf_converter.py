"""Event Grid trigger handler for PDF conversion — version-aware.

Blob path structure (versioned):
    {record_id}/{document_id}/original/v{N}/{filename}
    {record_id}/{document_id}/pdf/v{N}/{base_name}.pdf
"""

import logging
import os
from datetime import datetime, timezone

import azure.functions as func
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient

from services.conversion_service import ConversionService

logger = logging.getLogger("pdf_converter")

# Environment configuration
STORAGE_ACCOUNT_NAME = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME", "")
CONTAINER_NAME = "assurancenet-documents"
CLIENT_ID = os.environ.get("AZURE_CLIENT_ID", "")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")
SQL_SERVER = os.environ.get("AZURE_SQL_SERVER", "")
SQL_DATABASE = os.environ.get("AZURE_SQL_DATABASE", "")


def _update_version_status(
    version_id: str,
    pdf_path: str | None,
    status: str,
    error_message: str | None = None,
) -> None:
    """Update document_version metadata in SQL after PDF conversion."""
    if not SQL_SERVER or not SQL_DATABASE:
        logger.warning("SQL not configured - skipping metadata update for version_id=%s", version_id)
        return

    try:
        import pyodbc

        driver = "{ODBC Driver 18 for SQL Server}"
        conn_str = (
            f"Driver={driver};"
            f"Server=tcp:{SQL_SERVER},1433;"
            f"Database={SQL_DATABASE};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
            "Authentication=ActiveDirectoryMsi;"
        )
        now = datetime.now(timezone.utc).isoformat()

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE document_versions
                SET pdf_conversion_status = ?,
                    blob_path_pdf = ?,
                    pdf_conversion_error = ?,
                    pdf_converted_at = ?,
                    uploaded_at = uploaded_at
                WHERE id = ?
                """,
                status,
                pdf_path,
                error_message,
                now if status in ("completed", "failed") else None,
                version_id,
            )
            conn.commit()
            logger.info("Version metadata updated: version_id=%s, status=%s", version_id, status)

    except Exception:
        logger.exception("Failed to update version metadata: version_id=%s", version_id)


def _find_version_id(document_id: str, version_number: int) -> str | None:
    """Look up document_version ID from document_id + version_number."""
    if not SQL_SERVER or not SQL_DATABASE:
        return None

    try:
        import pyodbc

        driver = "{ODBC Driver 18 for SQL Server}"
        conn_str = (
            f"Driver={driver};"
            f"Server=tcp:{SQL_SERVER},1433;"
            f"Database={SQL_DATABASE};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
            "Authentication=ActiveDirectoryMsi;"
        )

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT CAST(id AS NVARCHAR(36)) FROM document_versions WHERE document_id = ? AND version_number = ?",
                document_id,
                version_number,
            )
            row = cursor.fetchone()
            return row[0] if row else None
    except Exception:
        logger.exception("Failed to look up version_id for document_id=%s, v=%d", document_id, version_number)
        return None


def _get_blob_client() -> BlobServiceClient:
    if CLIENT_ID and ENVIRONMENT != "dev":
        credential = ManagedIdentityCredential(client_id=CLIENT_ID)
    else:
        credential = DefaultAzureCredential()
    return BlobServiceClient(
        account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
        credential=credential,
    )


async def handle_blob_created(event: func.EventGridEvent) -> None:
    """Process a BlobCreated event and convert the file to PDF.

    Expected blob path structure (versioned):
        {record_id}/{document_id}/original/v{N}/{filename}
    """
    event_data = event.get_json()
    subject = event.subject
    content_type = event_data.get("contentType", "")

    logger.info("Processing blob event: subject=%s, content_type=%s", subject, content_type)

    # Extract blob path from subject
    parts = subject.split("/blobs/", 1)
    if len(parts) != 2:
        logger.warning("Unexpected subject format: %s", subject)
        return

    blob_path = parts[1]

    # Skip if already in pdf/ folder
    if "/pdf/" in blob_path:
        logger.info("Skipping PDF folder blob: %s", blob_path)
        return

    # Parse versioned blob path: {record_id}/{document_id}/original/v{N}/{filename}
    path_parts = blob_path.split("/")
    if len(path_parts) < 5 or path_parts[2] != "original":
        logger.warning("Unexpected blob path structure: %s", blob_path)
        return

    record_id = path_parts[0]
    document_id = path_parts[1]
    version_dir = path_parts[3]  # "v1", "v2", etc.
    filename = "/".join(path_parts[4:])

    # Extract version number
    try:
        version_number = int(version_dir.lstrip("v"))
    except ValueError:
        logger.warning("Cannot parse version from path: %s", blob_path)
        return

    # Look up version_id in SQL
    version_id = _find_version_id(document_id, version_number)

    try:
        blob_client = _get_blob_client()
        container_client = blob_client.get_container_client(CONTAINER_NAME)

        # Download original file
        download = container_client.get_blob_client(blob_path).download_blob()
        file_data = download.readall()

        logger.info(
            "Converting file: document_id=%s, v%d, filename=%s, content_type=%s, size=%d",
            document_id, version_number, filename, content_type, len(file_data),
        )

        # Convert to PDF using pluggable engine
        conversion_service = ConversionService()
        pdf_data = await conversion_service.convert_to_pdf(
            file_data=file_data,
            filename=filename,
            content_type=content_type,
        )

        # Build versioned PDF path and upload
        base_name = filename.rsplit(".", 1)[0] if "." in filename else filename
        pdf_blob_path = f"{record_id}/{document_id}/pdf/{version_dir}/{base_name}.pdf"

        pdf_blob_client = container_client.get_blob_client(pdf_blob_path)
        pdf_blob_client.upload_blob(pdf_data, overwrite=True, content_type="application/pdf")

        logger.info(
            "PDF conversion completed: document_id=%s, v%d, pdf_path=%s, pdf_size=%d",
            document_id, version_number, pdf_blob_path, len(pdf_data),
        )

        if version_id:
            _update_version_status(version_id, pdf_blob_path, "completed")

    except Exception as exc:
        logger.exception("PDF conversion failed: document_id=%s, v%d, blob_path=%s", document_id, version_number, blob_path)
        if version_id:
            _update_version_status(version_id, None, "failed", error_message=str(exc))
        raise
