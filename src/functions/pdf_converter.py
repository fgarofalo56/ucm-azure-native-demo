"""Event Grid trigger handler for PDF conversion."""

import json
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
GOTENBERG_URL = os.environ.get("GOTENBERG_URL", "http://ca-gotenberg-dev:3000")
SQL_SERVER = os.environ.get("AZURE_SQL_SERVER", "")
SQL_DATABASE = os.environ.get("AZURE_SQL_DATABASE", "")


def _update_document_status(
    file_id: str,
    pdf_path: str | None,
    status: str,
    error_message: str | None = None,
) -> None:
    """Update document metadata in SQL after PDF conversion."""
    if not SQL_SERVER or not SQL_DATABASE:
        logger.warning("SQL not configured - skipping metadata update for file_id=%s", file_id)
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
                UPDATE documents
                SET pdf_conversion_status = ?,
                    pdf_path = ?,
                    pdf_conversion_error = ?,
                    pdf_converted_at = ?,
                    updated_at = ?
                WHERE file_id = ?
                """,
                status,
                pdf_path,
                error_message,
                now if status in ("completed", "failed") else None,
                now,
                file_id,
            )
            conn.commit()
            logger.info("Document metadata updated: file_id=%s, status=%s", file_id, status)

    except Exception:
        logger.exception("Failed to update document metadata: file_id=%s", file_id)


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
    """Process a BlobCreated event and convert the file to PDF."""
    event_data = event.get_json()
    subject = event.subject
    blob_url = event_data.get("url", "")
    content_type = event_data.get("contentType", "")

    logger.info("Processing blob event: subject=%s, content_type=%s", subject, content_type)

    # Extract blob path from subject
    # Subject format: /blobServices/default/containers/{container}/blobs/{blob_path}
    parts = subject.split("/blobs/", 1)
    if len(parts) != 2:
        logger.warning("Unexpected subject format: %s", subject)
        return

    blob_path = parts[1]

    # Skip if already in pdf/ folder
    if "/pdf/" in blob_path:
        logger.info("Skipping PDF folder blob: %s", blob_path)
        return

    # Parse blob path: {record_id}/{file_id}/blob/{filename}
    path_parts = blob_path.split("/")
    if len(path_parts) < 4 or path_parts[2] != "blob":
        logger.warning("Unexpected blob path structure: %s", blob_path)
        return

    record_id = path_parts[0]
    file_id = path_parts[1]
    filename = "/".join(path_parts[3:])

    try:
        blob_client = _get_blob_client()
        container_client = blob_client.get_container_client(CONTAINER_NAME)

        # Download original file
        download = container_client.get_blob_client(blob_path).download_blob()
        file_data = download.readall()

        logger.info(
            "Converting file: file_id=%s, filename=%s, content_type=%s, size=%d",
            file_id, filename, content_type, len(file_data),
        )

        # Convert to PDF
        conversion_service = ConversionService(gotenberg_url=GOTENBERG_URL)
        pdf_data = await conversion_service.convert_to_pdf(
            file_data=file_data,
            filename=filename,
            content_type=content_type,
        )

        # Build PDF path and upload
        base_name = filename.rsplit(".", 1)[0] if "." in filename else filename
        pdf_blob_path = f"{record_id}/{file_id}/pdf/{base_name}.pdf"

        pdf_blob_client = container_client.get_blob_client(pdf_blob_path)
        pdf_blob_client.upload_blob(pdf_data, overwrite=True, content_type="application/pdf")

        logger.info(
            "PDF conversion completed: file_id=%s, pdf_path=%s, pdf_size=%d",
            file_id, pdf_blob_path, len(pdf_data),
        )

        _update_document_status(file_id, pdf_blob_path, "completed")

    except Exception as exc:
        logger.exception("PDF conversion failed: file_id=%s, blob_path=%s", file_id, blob_path)
        _update_document_status(file_id, None, "failed", error_message=str(exc))
        raise
