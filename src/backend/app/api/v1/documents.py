"""Document upload, download, list, delete, and version endpoints."""

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import AppUser
from app.db.session import get_db_session
from app.dependencies import get_blob_service_client
from app.middleware.auth import require_permission
from app.models.enums import AuditEventType, PdfConversionStatus
from app.models.schemas import (
    BatchUploadResponse,
    BatchUploadResult,
    DocumentResponse,
    DocumentUploadResponse,
    DocumentVersionResponse,
)
from app.services.audit_service import AuditService
from app.services.blob_service import BlobService
from app.services.metadata_service import MetadataService

logger = structlog.get_logger()
router = APIRouter()


@router.post(
    "/upload/{investigation_id}",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    investigation_id: uuid.UUID,
    file: UploadFile,
    app_user: Annotated[AppUser, Depends(require_permission("documents", "create"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DocumentUploadResponse:
    """Upload a document to an investigation."""
    metadata_svc = MetadataService(session)
    blob_svc = BlobService(get_blob_service_client())
    audit_svc = AuditService(session)

    # Validate investigation exists
    investigation = await metadata_svc.get_investigation(investigation_id)
    if not investigation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found")

    # Read and validate file
    file_data = await file.read()
    if len(file_data) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.max_upload_size_mb}MB",
        )

    # Generate IDs and compute checksum
    file_id = str(uuid.uuid4())
    checksum = BlobService.compute_checksum(file_data)
    filename = file.filename or "unnamed"
    content_type = file.content_type

    # Determine if PDF conversion is needed
    pdf_status = PdfConversionStatus.PENDING
    if content_type == "application/pdf":
        pdf_status = PdfConversionStatus.NOT_REQUIRED

    # Upload to blob storage
    blob_path = blob_svc.build_blob_path(investigation.record_id, file_id, filename)
    _, version_id = await blob_svc.upload_blob(blob_path, file_data, content_type)

    # Create metadata record
    document = await metadata_svc.create_document(
        investigation_id=investigation_id,
        file_id=file_id,
        original_filename=filename,
        content_type=content_type,
        file_size_bytes=len(file_data),
        blob_path=blob_path,
        blob_version_id=version_id,
        checksum_sha256=checksum,
        user_id=app_user.entra_oid,
        user_name=app_user.display_name,
        pdf_conversion_status=pdf_status,
    )

    # Audit log
    await audit_svc.log_event(
        event_type=AuditEventType.DOCUMENT_UPLOAD,
        user_id=app_user.entra_oid,
        user_principal_name=app_user.email,
        action="create",
        result="success",
        resource_type="document",
        resource_id=file_id,
        details={"filename": filename, "size": len(file_data), "content_type": content_type},
    )

    return DocumentUploadResponse(
        id=document.id,
        file_id=file_id,
        original_filename=filename,
        file_size_bytes=len(file_data),
        checksum_sha256=checksum,
        pdf_conversion_status=pdf_status,
        blob_path=blob_path,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    app_user: Annotated[AppUser, Depends(require_permission("documents", "read"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DocumentResponse:
    """Get document metadata by ID."""
    metadata_svc = MetadataService(session)
    document = await metadata_svc.get_document(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return DocumentResponse.model_validate(document)


@router.get("/{document_id}/download")
async def download_document(
    document_id: uuid.UUID,
    app_user: Annotated[AppUser, Depends(require_permission("documents", "download"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    version: str | None = None,
) -> StreamingResponse:
    """Download original document (optionally a specific version)."""
    metadata_svc = MetadataService(session)
    blob_svc = BlobService(get_blob_service_client())
    audit_svc = AuditService(session)

    document = await metadata_svc.get_document(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Validate requested version belongs to this document's blob
    if version:
        valid_versions = await blob_svc.list_blob_versions(document.blob_path)
        valid_version_ids = {v["version_id"] for v in valid_versions}
        if version not in valid_version_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requested version not found for this document",
            )

    data = await blob_svc.download_blob(document.blob_path, version_id=version)

    await audit_svc.log_event(
        event_type=AuditEventType.DOCUMENT_DOWNLOAD,
        user_id=app_user.entra_oid,
        user_principal_name=app_user.email,
        action="read",
        result="success",
        resource_type="document",
        resource_id=document.file_id,
        details={"version": version, "format": "original"},
    )

    return StreamingResponse(
        iter([data]),
        media_type=document.content_type or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{document.original_filename}"'},
    )


@router.get("/{document_id}/pdf")
async def download_pdf(
    document_id: uuid.UUID,
    app_user: Annotated[AppUser, Depends(require_permission("documents", "download"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> StreamingResponse:
    """Download the PDF version of a document."""
    metadata_svc = MetadataService(session)
    blob_svc = BlobService(get_blob_service_client())
    audit_svc = AuditService(session)

    document = await metadata_svc.get_document(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # For PDFs, serve the original
    if document.pdf_conversion_status == PdfConversionStatus.NOT_REQUIRED:
        data = await blob_svc.download_blob(document.blob_path)
        filename = document.original_filename
    elif document.pdf_conversion_status == PdfConversionStatus.COMPLETED and document.pdf_path:
        data = await blob_svc.download_blob(document.pdf_path)
        base = document.original_filename.rsplit(".", 1)[0]
        filename = f"{base}.pdf"
    elif document.pdf_conversion_status == PdfConversionStatus.COMPLETED and not document.pdf_path:
        # PDF files marked completed without a separate pdf_path — use original
        data = await blob_svc.download_blob(document.blob_path)
        filename = document.original_filename
    else:
        # Return appropriate status codes based on conversion state
        if document.pdf_conversion_status in (
            PdfConversionStatus.PENDING,
            PdfConversionStatus.PROCESSING,
        ):
            raise HTTPException(
                status_code=status.HTTP_202_ACCEPTED,
                detail=f"PDF conversion in progress. Status: {document.pdf_conversion_status}",
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PDF not available. Conversion status: {document.pdf_conversion_status}",
        )

    await audit_svc.log_event(
        event_type=AuditEventType.DOCUMENT_DOWNLOAD,
        user_id=app_user.entra_oid,
        user_principal_name=app_user.email,
        action="read",
        result="success",
        resource_type="document",
        resource_id=document.file_id,
        details={"format": "pdf"},
    )

    return StreamingResponse(
        iter([data]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{document_id}/versions", response_model=list[DocumentVersionResponse])
async def list_document_versions(
    document_id: uuid.UUID,
    app_user: Annotated[AppUser, Depends(require_permission("documents", "read"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[DocumentVersionResponse]:
    """List all versions of a document."""
    metadata_svc = MetadataService(session)
    blob_svc = BlobService(get_blob_service_client())

    document = await metadata_svc.get_document(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    versions = await blob_svc.list_blob_versions(document.blob_path)
    return [DocumentVersionResponse(**v) for v in versions]


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    app_user: Annotated[AppUser, Depends(require_permission("documents", "delete"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    """Soft-delete a document."""
    metadata_svc = MetadataService(session)
    audit_svc = AuditService(session)

    document = await metadata_svc.get_document(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    await metadata_svc.soft_delete_document(document_id, app_user.entra_oid)

    await audit_svc.log_event(
        event_type=AuditEventType.DOCUMENT_DELETE,
        user_id=app_user.entra_oid,
        action="delete",
        result="success",
        resource_type="document",
        resource_id=document.file_id,
    )


@router.post(
    "/batch-upload/{investigation_id}",
    response_model=BatchUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def batch_upload_documents(
    investigation_id: uuid.UUID,
    files: list[UploadFile],
    app_user: Annotated[AppUser, Depends(require_permission("documents", "create"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> BatchUploadResponse:
    """Upload multiple documents to an investigation."""
    metadata_svc = MetadataService(session)
    blob_svc = BlobService(get_blob_service_client())
    audit_svc = AuditService(session)

    investigation = await metadata_svc.get_investigation(investigation_id)
    if not investigation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found")

    results: list[BatchUploadResult] = []
    for file in files:
        try:
            file_data = await file.read()
            if len(file_data) > settings.max_upload_size_bytes:
                results.append(
                    BatchUploadResult(
                        filename=file.filename or "unnamed",
                        success=False,
                        error=f"Exceeds {settings.max_upload_size_mb}MB limit",
                    )
                )
                continue

            file_id = str(uuid.uuid4())
            checksum = BlobService.compute_checksum(file_data)
            filename = file.filename or "unnamed"
            content_type = file.content_type

            pdf_status = PdfConversionStatus.PENDING
            if content_type == "application/pdf":
                pdf_status = PdfConversionStatus.NOT_REQUIRED

            blob_path = blob_svc.build_blob_path(investigation.record_id, file_id, filename)
            _, version_id = await blob_svc.upload_blob(blob_path, file_data, content_type)

            await metadata_svc.create_document(
                investigation_id=investigation_id,
                file_id=file_id,
                original_filename=filename,
                content_type=content_type,
                file_size_bytes=len(file_data),
                blob_path=blob_path,
                blob_version_id=version_id,
                checksum_sha256=checksum,
                user_id=app_user.entra_oid,
                user_name=app_user.display_name,
                pdf_conversion_status=pdf_status,
            )

            results.append(
                BatchUploadResult(
                    filename=filename,
                    success=True,
                    file_id=file_id,
                )
            )
        except Exception as e:
            results.append(
                BatchUploadResult(
                    filename=file.filename or "unnamed",
                    success=False,
                    error=str(e),
                )
            )

    succeeded = sum(1 for r in results if r.success)
    await audit_svc.log_event(
        event_type=AuditEventType.BATCH_UPLOAD,
        user_id=app_user.entra_oid,
        user_principal_name=app_user.email,
        action="create",
        result="success" if succeeded > 0 else "failure",
        resource_type="investigation",
        resource_id=str(investigation_id),
        details={"total": len(results), "succeeded": succeeded, "failed": len(results) - succeeded},
    )

    return BatchUploadResponse(
        investigation_id=str(investigation_id),
        results=results,
        total=len(results),
        succeeded=succeeded,
        failed=len(results) - succeeded,
    )
