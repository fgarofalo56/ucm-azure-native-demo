"""Document upload, download, list, delete endpoints — version-aware.

End users only see latest versions. Historical versions are admin-only (see admin.py).
"""

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import AppUser
from app.db.session import get_db_session
from app.dependencies import get_blob_service_client
from app.middleware.auth import require_permission
from app.models.enums import AuditEventType, DocumentType, PdfConversionStatus
from app.models.schemas import (
    BatchUploadResponse,
    BatchUploadResult,
    CopyDocumentResult,
    CopyDocumentsRequest,
    CopyDocumentsResponse,
    DocumentResponse,
    DocumentUploadResponse,
)
from app.services.audit_service import AuditService
from app.services.blob_service import BlobService
from app.services.metadata_service import MetadataService
from app.services.pdf_conversion_service import convert_to_pdf

logger = structlog.get_logger()
router = APIRouter()


def _build_document_response(doc) -> DocumentResponse:
    """Build a DocumentResponse from a Document ORM object with latest version inlined."""
    latest = doc.latest_version
    return DocumentResponse(
        id=doc.id,
        investigation_id=doc.investigation_id,
        document_type=doc.document_type,
        title=doc.title,
        created_by=doc.created_by,
        created_by_name=doc.created_by_name,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        current_version_id=latest.id if latest else None,
        version_number=latest.version_number if latest else None,
        original_filename=latest.original_filename if latest else None,
        mime_type=latest.mime_type if latest else None,
        file_size_bytes=latest.file_size_bytes if latest else None,
        checksum=latest.checksum if latest else None,
        pdf_conversion_status=latest.pdf_conversion_status if latest else None,
        uploaded_by=latest.uploaded_by if latest else None,
        uploaded_by_name=latest.uploaded_by_name if latest else None,
        uploaded_at=latest.uploaded_at if latest else None,
    )


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
    document_type: DocumentType = Form(DocumentType.OTHER),
    title: str | None = Form(None),
) -> DocumentUploadResponse:
    """Upload a document to an investigation, creating a logical document + v1."""
    metadata_svc = MetadataService(session)
    blob_svc = BlobService(get_blob_service_client())
    audit_svc = AuditService(session)

    investigation = await metadata_svc.get_investigation(investigation_id)
    if not investigation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found")

    file_data = await file.read()
    if len(file_data) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.max_upload_size_mb}MB",
        )

    checksum = BlobService.compute_checksum(file_data)
    filename = file.filename or "unnamed"
    content_type = file.content_type

    pdf_status = PdfConversionStatus.PENDING
    if content_type == "application/pdf":
        pdf_status = PdfConversionStatus.NOT_REQUIRED

    # Create logical document + v1 in metadata
    document, version = await metadata_svc.create_document_with_version(
        investigation_id=investigation_id,
        original_filename=filename,
        mime_type=content_type,
        file_size_bytes=len(file_data),
        blob_path_original="",  # placeholder, set after upload
        checksum=checksum,
        user_id=app_user.entra_oid,
        user_name=app_user.display_name,
        document_type=document_type,
        title=title,
        pdf_conversion_status=pdf_status,
    )

    # Build versioned blob path and upload
    blob_path = blob_svc.build_blob_path(
        investigation.record_id, str(document.id), version.version_number, filename
    )
    await blob_svc.upload_blob(blob_path, file_data, content_type)

    # Update version with actual blob path
    version.blob_path_original = blob_path
    await session.flush()

    # In-process PDF conversion (replaces async Event Grid pipeline)
    if pdf_status == PdfConversionStatus.PENDING:
        pdf_data = convert_to_pdf(file_data, filename, content_type)
        if pdf_data:
            pdf_blob_path = blob_svc.build_pdf_path(
                investigation.record_id, str(document.id), version.version_number, filename
            )
            await blob_svc.upload_blob(pdf_blob_path, pdf_data, "application/pdf")
            version.blob_path_pdf = pdf_blob_path
            version.pdf_conversion_status = PdfConversionStatus.COMPLETED
            pdf_status = PdfConversionStatus.COMPLETED
            await session.flush()
            logger.info("pdf_converted_inline", document_id=str(document.id), pdf_path=pdf_blob_path)

    await audit_svc.log_event(
        event_type=AuditEventType.DOCUMENT_UPLOAD,
        user_id=app_user.entra_oid,
        user_principal_name=app_user.email,
        action="create",
        result="success",
        resource_type="document",
        resource_id=str(document.id),
        details={
            "filename": filename,
            "size": len(file_data),
            "content_type": content_type,
            "version": version.version_number,
            "document_type": document_type,
        },
    )

    return DocumentUploadResponse(
        document_id=document.id,
        version_id=version.id,
        version_number=version.version_number,
        original_filename=filename,
        file_size_bytes=len(file_data),
        checksum=checksum,
        document_type=document_type,
        pdf_conversion_status=pdf_status,
        blob_path=blob_path,
    )


@router.post(
    "/{document_id}/versions",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_new_version(
    document_id: uuid.UUID,
    file: UploadFile,
    app_user: Annotated[AppUser, Depends(require_permission("documents", "create"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DocumentUploadResponse:
    """Upload a new version of an existing document. Previous version demoted."""
    metadata_svc = MetadataService(session)
    blob_svc = BlobService(get_blob_service_client())
    audit_svc = AuditService(session)

    document = await metadata_svc.get_document(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    investigation = await metadata_svc.get_investigation(document.investigation_id)
    if not investigation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found")

    file_data = await file.read()
    if len(file_data) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.max_upload_size_mb}MB",
        )

    checksum = BlobService.compute_checksum(file_data)
    filename = file.filename or "unnamed"
    content_type = file.content_type

    pdf_status = PdfConversionStatus.PENDING
    if content_type == "application/pdf":
        pdf_status = PdfConversionStatus.NOT_REQUIRED

    version = await metadata_svc.add_version(
        document_id=document_id,
        original_filename=filename,
        mime_type=content_type,
        file_size_bytes=len(file_data),
        blob_path_original="",
        checksum=checksum,
        user_id=app_user.entra_oid,
        user_name=app_user.display_name,
        pdf_conversion_status=pdf_status,
    )

    blob_path = blob_svc.build_blob_path(
        investigation.record_id, str(document.id), version.version_number, filename
    )
    await blob_svc.upload_blob(blob_path, file_data, content_type)

    version.blob_path_original = blob_path
    await session.flush()

    # In-process PDF conversion
    if pdf_status == PdfConversionStatus.PENDING:
        pdf_data = convert_to_pdf(file_data, filename, content_type)
        if pdf_data:
            pdf_blob_path = blob_svc.build_pdf_path(
                investigation.record_id, str(document.id), version.version_number, filename
            )
            await blob_svc.upload_blob(pdf_blob_path, pdf_data, "application/pdf")
            version.blob_path_pdf = pdf_blob_path
            version.pdf_conversion_status = PdfConversionStatus.COMPLETED
            pdf_status = PdfConversionStatus.COMPLETED
            await session.flush()

    await audit_svc.log_event(
        event_type=AuditEventType.DOCUMENT_UPLOAD,
        user_id=app_user.entra_oid,
        user_principal_name=app_user.email,
        action="create",
        result="success",
        resource_type="document_version",
        resource_id=str(version.id),
        details={
            "document_id": str(document_id),
            "filename": filename,
            "version": version.version_number,
        },
    )

    return DocumentUploadResponse(
        document_id=document.id,
        version_id=version.id,
        version_number=version.version_number,
        original_filename=filename,
        file_size_bytes=len(file_data),
        checksum=checksum,
        document_type=document.document_type,
        pdf_conversion_status=pdf_status,
        blob_path=blob_path,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    app_user: Annotated[AppUser, Depends(require_permission("documents", "read"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DocumentResponse:
    """Get document metadata — latest version only."""
    metadata_svc = MetadataService(session)
    document = await metadata_svc.get_document(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return _build_document_response(document)


@router.get("/{document_id}/download")
async def download_document(
    document_id: uuid.UUID,
    app_user: Annotated[AppUser, Depends(require_permission("documents", "download"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> StreamingResponse:
    """Download the latest version's original file."""
    metadata_svc = MetadataService(session)
    blob_svc = BlobService(get_blob_service_client())
    audit_svc = AuditService(session)

    document = await metadata_svc.get_document(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    latest = document.latest_version
    if not latest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No version available")

    data = await blob_svc.download_blob(latest.blob_path_original)

    await audit_svc.log_event(
        event_type=AuditEventType.DOCUMENT_DOWNLOAD,
        user_id=app_user.entra_oid,
        user_principal_name=app_user.email,
        action="read",
        result="success",
        resource_type="document",
        resource_id=str(document.id),
        details={"version": latest.version_number, "format": "original"},
    )

    return StreamingResponse(
        iter([data]),
        media_type=latest.mime_type or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{latest.original_filename}"'},
    )


@router.get("/{document_id}/pdf")
async def download_pdf(
    document_id: uuid.UUID,
    app_user: Annotated[AppUser, Depends(require_permission("documents", "download"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> StreamingResponse:
    """Download the PDF version of the latest document version."""
    metadata_svc = MetadataService(session)
    blob_svc = BlobService(get_blob_service_client())
    audit_svc = AuditService(session)

    document = await metadata_svc.get_document(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    latest = document.latest_version
    if not latest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No version available")

    if latest.pdf_conversion_status == PdfConversionStatus.NOT_REQUIRED:
        data = await blob_svc.download_blob(latest.blob_path_original)
        filename = latest.original_filename
    elif latest.pdf_conversion_status == PdfConversionStatus.COMPLETED and latest.blob_path_pdf:
        data = await blob_svc.download_blob(latest.blob_path_pdf)
        base = latest.original_filename.rsplit(".", 1)[0]
        filename = f"{base}.pdf"
    elif latest.pdf_conversion_status == PdfConversionStatus.COMPLETED and not latest.blob_path_pdf:
        data = await blob_svc.download_blob(latest.blob_path_original)
        filename = latest.original_filename
    else:
        if latest.pdf_conversion_status in (PdfConversionStatus.PENDING, PdfConversionStatus.PROCESSING):
            raise HTTPException(
                status_code=status.HTTP_202_ACCEPTED,
                detail=f"PDF conversion in progress. Status: {latest.pdf_conversion_status}",
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PDF not available. Conversion status: {latest.pdf_conversion_status}",
        )

    await audit_svc.log_event(
        event_type=AuditEventType.DOCUMENT_DOWNLOAD,
        user_id=app_user.entra_oid,
        user_principal_name=app_user.email,
        action="read",
        result="success",
        resource_type="document",
        resource_id=str(document.id),
        details={"version": latest.version_number, "format": "pdf"},
    )

    return StreamingResponse(
        iter([data]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    app_user: Annotated[AppUser, Depends(require_permission("documents", "delete"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    """Soft-delete a document (all versions)."""
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
        resource_id=str(document.id),
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
    document_type: DocumentType = Form(DocumentType.OTHER),
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

            checksum = BlobService.compute_checksum(file_data)
            filename = file.filename or "unnamed"
            content_type = file.content_type

            pdf_status = PdfConversionStatus.PENDING
            if content_type == "application/pdf":
                pdf_status = PdfConversionStatus.NOT_REQUIRED

            document, version = await metadata_svc.create_document_with_version(
                investigation_id=investigation_id,
                original_filename=filename,
                mime_type=content_type,
                file_size_bytes=len(file_data),
                blob_path_original="",
                checksum=checksum,
                user_id=app_user.entra_oid,
                user_name=app_user.display_name,
                document_type=document_type,
                pdf_conversion_status=pdf_status,
            )

            blob_path = blob_svc.build_blob_path(
                investigation.record_id, str(document.id), version.version_number, filename
            )
            await blob_svc.upload_blob(blob_path, file_data, content_type)
            version.blob_path_original = blob_path
            await session.flush()

            # In-process PDF conversion
            if pdf_status == PdfConversionStatus.PENDING:
                pdf_data = convert_to_pdf(file_data, filename, content_type)
                if pdf_data:
                    pdf_blob_path = blob_svc.build_pdf_path(
                        investigation.record_id, str(document.id), version.version_number, filename
                    )
                    await blob_svc.upload_blob(pdf_blob_path, pdf_data, "application/pdf")
                    version.blob_path_pdf = pdf_blob_path
                    version.pdf_conversion_status = PdfConversionStatus.COMPLETED
                    await session.flush()

            results.append(
                BatchUploadResult(
                    filename=filename,
                    success=True,
                    document_id=str(document.id),
                    version_id=str(version.id),
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


@router.post("/copy-to-investigation", response_model=CopyDocumentsResponse)
async def copy_documents_to_investigation(
    body: CopyDocumentsRequest,
    app_user: Annotated[AppUser, Depends(require_permission("documents", "create"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CopyDocumentsResponse:
    """Copy existing documents (latest versions) to a different investigation."""
    metadata_svc = MetadataService(session)
    blob_svc = BlobService(get_blob_service_client())
    audit_svc = AuditService(session)

    investigation = await metadata_svc.get_investigation(uuid.UUID(body.investigation_id))
    if not investigation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found")

    results: list[CopyDocumentResult] = []
    for doc_id in body.document_ids:
        try:
            source_doc = await metadata_svc.get_document(uuid.UUID(doc_id))
            if not source_doc:
                results.append(CopyDocumentResult(document_id=doc_id, success=False, error="Document not found"))
                continue

            latest = source_doc.latest_version
            if not latest:
                results.append(CopyDocumentResult(document_id=doc_id, success=False, error="No version available"))
                continue

            data = await blob_svc.download_blob(latest.blob_path_original)

            new_doc, new_ver = await metadata_svc.create_document_with_version(
                investigation_id=uuid.UUID(body.investigation_id),
                original_filename=latest.original_filename,
                mime_type=latest.mime_type,
                file_size_bytes=len(data),
                blob_path_original="",
                checksum=BlobService.compute_checksum(data),
                user_id=app_user.entra_oid,
                user_name=app_user.display_name,
                document_type=source_doc.document_type,
                title=source_doc.title,
                pdf_conversion_status=latest.pdf_conversion_status,
            )

            new_blob_path = blob_svc.build_blob_path(
                investigation.record_id, str(new_doc.id), new_ver.version_number, latest.original_filename
            )
            await blob_svc.upload_blob(new_blob_path, data, latest.mime_type)
            new_ver.blob_path_original = new_blob_path
            await session.flush()

            results.append(CopyDocumentResult(document_id=doc_id, success=True, new_document_id=str(new_doc.id)))
        except Exception as e:
            logger.error("copy_document_failed", document_id=doc_id, error=str(e))
            results.append(CopyDocumentResult(document_id=doc_id, success=False, error=str(e)))

    succeeded = sum(1 for r in results if r.success)
    await audit_svc.log_event(
        event_type=AuditEventType.BATCH_UPLOAD,
        user_id=app_user.entra_oid,
        user_principal_name=app_user.email,
        action="create",
        result="success" if succeeded > 0 else "failure",
        resource_type="investigation",
        resource_id=body.investigation_id,
        details={"source": "copy", "total": len(results), "succeeded": succeeded},
    )

    return CopyDocumentsResponse(
        investigation_id=body.investigation_id,
        results=results,
        total=len(results),
        succeeded=succeeded,
        failed=len(results) - succeeded,
    )
