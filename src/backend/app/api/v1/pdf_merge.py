"""On-demand PDF merge endpoint."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import AppUser
from app.db.session import get_db_session
from app.dependencies import get_blob_service_client
from app.middleware.auth import require_permission
from app.models.enums import AuditEventType, PdfConversionStatus
from app.models.schemas import PdfMergeRequest
from app.services.audit_service import AuditService
from app.services.blob_service import BlobService
from app.services.metadata_service import MetadataService
from app.services.pdf_merge_service import PdfMergeService

logger = structlog.get_logger()
router = APIRouter()


@router.post("/investigations/{record_id}/merge-pdf")
async def merge_pdfs(
    record_id: str,
    body: PdfMergeRequest,
    app_user: Annotated[AppUser, Depends(require_permission("documents", "merge"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> StreamingResponse:
    """Merge multiple documents into a single PDF download.

    The merged PDF is NOT persisted - it's generated on-demand and streamed.
    """
    metadata_svc = MetadataService(session)
    blob_svc = BlobService(get_blob_service_client())
    audit_svc = AuditService(session)

    if len(body.file_ids) > settings.max_merge_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {settings.max_merge_files} files allowed for merge",
        )

    # Collect PDF contents
    pdf_contents: list[bytes] = []
    total_size = 0

    for file_id in body.file_ids:
        document = await metadata_svc.get_document_by_file_id(file_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {file_id}",
            )

        # Determine which path to use (PDF or original if already PDF)
        try:
            if document.pdf_conversion_status == PdfConversionStatus.NOT_REQUIRED:
                pdf_data = await blob_svc.download_blob(document.blob_path)
            elif document.pdf_conversion_status == PdfConversionStatus.COMPLETED and document.pdf_path:
                pdf_data = await blob_svc.download_blob(document.pdf_path)
            elif document.pdf_conversion_status == PdfConversionStatus.COMPLETED and not document.pdf_path:
                # PDF files marked completed without a separate pdf_path — use original
                pdf_data = await blob_svc.download_blob(document.blob_path)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"PDF not available for {file_id}. Status: {document.pdf_conversion_status}",
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error("blob_download_failed", file_id=file_id, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to download document {file_id} from storage",
            ) from e

        total_size += len(pdf_data)
        if total_size > settings.max_merge_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Combined file size exceeds {settings.max_merge_size_mb}MB limit",
            )

        pdf_contents.append(pdf_data)

    # Merge PDFs
    merged_pdf = PdfMergeService.merge_pdfs(pdf_contents)

    # Audit log
    await audit_svc.log_event(
        event_type=AuditEventType.DOCUMENT_MERGE,
        user_id=app_user.entra_oid,
        user_principal_name=app_user.email,
        action="merge",
        result="success",
        resource_type="investigation",
        resource_id=record_id,
        details={
            "file_ids": body.file_ids,
            "file_count": len(body.file_ids),
            "merged_size_bytes": len(merged_pdf),
        },
    )

    return StreamingResponse(
        iter([merged_pdf]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{record_id}-merged.pdf"',
            "Content-Length": str(len(merged_pdf)),
        },
    )
