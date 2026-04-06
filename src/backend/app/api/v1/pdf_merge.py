"""On-demand PDF merge endpoint — type-based ordering, latest versions only."""

import uuid
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
from app.models.enums import MERGE_ORDER_CONFIG, AuditEventType, DocumentType, PdfConversionStatus
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

    Documents are sorted by document type (rule-based ordering), not user order.
    Only the latest version of each document is used.
    The merged PDF is NOT persisted — it's generated on-demand and streamed.
    """
    metadata_svc = MetadataService(session)
    blob_svc = BlobService(get_blob_service_client())
    audit_svc = AuditService(session)

    if len(body.document_ids) > settings.max_merge_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {settings.max_merge_files} files allowed for merge",
        )

    # Load documents and their latest versions
    documents_with_versions = []
    for doc_id_str in body.document_ids:
        doc_id = uuid.UUID(doc_id_str)
        document = await metadata_svc.get_document(doc_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {doc_id_str}",
            )
        latest = document.latest_version
        if not latest:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No version available for document: {doc_id_str}",
            )
        documents_with_versions.append((document, latest))

    # Sort by document type merge order (rule-based, not user order)
    documents_with_versions.sort(key=lambda dv: MERGE_ORDER_CONFIG.get(DocumentType(dv[0].document_type), 99))

    # Collect PDF contents from sorted documents
    pdf_contents: list[bytes] = []
    total_size = 0

    for document, latest in documents_with_versions:
        try:
            if latest.pdf_conversion_status == PdfConversionStatus.NOT_REQUIRED:
                pdf_data = await blob_svc.download_blob(latest.blob_path_original)
            elif latest.pdf_conversion_status == PdfConversionStatus.COMPLETED and latest.blob_path_pdf:
                pdf_data = await blob_svc.download_blob(latest.blob_path_pdf)
            elif latest.pdf_conversion_status == PdfConversionStatus.COMPLETED and not latest.blob_path_pdf:
                pdf_data = await blob_svc.download_blob(latest.blob_path_original)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"PDF not available for document {document.id}. Status: {latest.pdf_conversion_status}",
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error("blob_download_failed", document_id=str(document.id), error=str(e))
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to download document {document.id} from storage",
            ) from e

        total_size += len(pdf_data)
        if total_size > settings.max_merge_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Combined file size exceeds {settings.max_merge_size_mb}MB limit",
            )

        pdf_contents.append(pdf_data)

    merged_pdf = PdfMergeService.merge_pdfs(pdf_contents)

    await audit_svc.log_event(
        event_type=AuditEventType.DOCUMENT_MERGE,
        user_id=app_user.entra_oid,
        user_principal_name=app_user.email,
        action="merge",
        result="success",
        resource_type="investigation",
        resource_id=record_id,
        details={
            "document_ids": body.document_ids,
            "document_count": len(body.document_ids),
            "merged_size_bytes": len(merged_pdf),
            "order": [str(dv[0].id) for dv in documents_with_versions],
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
