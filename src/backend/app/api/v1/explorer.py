"""File explorer endpoint for browsing blob storage."""

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AppUser
from app.db.session import get_db_session
from app.dependencies import get_blob_service_client
from app.middleware.auth import require_permission
from app.models.enums import AuditEventType, PdfConversionStatus
from app.models.schemas import (
    AddToInvestigationRequest,
    AddToInvestigationResponse,
    AddToInvestigationResult,
    ExplorerItem,
    ExplorerResponse,
)
from app.services.audit_service import AuditService
from app.services.blob_service import BlobService
from app.services.metadata_service import MetadataService

logger = structlog.get_logger()
router = APIRouter()


@router.get("/browse", response_model=ExplorerResponse)
async def browse_explorer(
    app_user: Annotated[AppUser, Depends(require_permission("documents", "read"))],
    prefix: str = Query("", max_length=500),
) -> ExplorerResponse:
    """Browse blob storage with folder/file structure.

    Uses delimiter-based listing to show investigation folders and document files.
    """
    blob_svc = BlobService(get_blob_service_client())
    container_client = blob_svc._get_container_client()

    items: list[ExplorerItem] = []
    seen_prefixes: set[str] = set()

    # Use walk_blobs to get hierarchical listing
    blobs = container_client.walk_blobs(name_starts_with=prefix or None, delimiter="/")
    for item in blobs:
        if hasattr(item, "prefix"):
            # It's a virtual folder
            folder_path = item.prefix
            folder_name = folder_path.rstrip("/").rsplit("/", 1)[-1]
            if folder_path not in seen_prefixes:
                seen_prefixes.add(folder_path)
                items.append(
                    ExplorerItem(
                        name=folder_name,
                        type="folder",
                        path=folder_path,
                    )
                )
        else:
            # It's a file
            file_name = item.name.rsplit("/", 1)[-1]
            items.append(
                ExplorerItem(
                    name=file_name,
                    type="file",
                    path=item.name,
                    size=item.size,
                    last_modified=item.last_modified,
                    content_type=item.content_settings.content_type if item.content_settings else None,
                )
            )

    return ExplorerResponse(prefix=prefix, items=items)


@router.get("/download")
async def download_explorer_file(
    app_user: Annotated[AppUser, Depends(require_permission("documents", "download"))],
    path: str = Query(min_length=1, max_length=1000),
) -> StreamingResponse:
    """Download a single file from blob storage by path."""
    blob_svc = BlobService(get_blob_service_client())

    try:
        data = await blob_svc.download_blob(path)
    except Exception as e:
        logger.error("explorer_download_failed", path=path, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {path}",
        ) from e

    filename = path.rsplit("/", 1)[-1]
    return StreamingResponse(
        iter([data]),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/files")
async def delete_explorer_files(
    paths: list[str],
    app_user: Annotated[AppUser, Depends(require_permission("documents", "delete"))],
) -> dict:
    """Batch delete blobs by path. Requires documents.delete permission."""
    blob_svc = BlobService(get_blob_service_client())
    deleted = 0
    errors: list[str] = []

    for path in paths:
        try:
            await blob_svc.delete_blob(path)
            deleted += 1
        except Exception as e:
            errors.append(f"{path}: {e}")

    return {"deleted": deleted, "errors": errors}


@router.post("/add-to-investigation", response_model=AddToInvestigationResponse)
async def add_files_to_investigation(
    body: AddToInvestigationRequest,
    app_user: Annotated[AppUser, Depends(require_permission("documents", "create"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AddToInvestigationResponse:
    """Copy explorer files into an investigation as tracked documents."""
    blob_svc = BlobService(get_blob_service_client())
    metadata_svc = MetadataService(session)
    audit_svc = AuditService(session)

    investigation = await metadata_svc.get_investigation(uuid.UUID(body.investigation_id))
    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )

    results: list[AddToInvestigationResult] = []
    for blob_path in body.blob_paths:
        try:
            # Download the source blob
            data = await blob_svc.download_blob(blob_path)
            filename = blob_path.rsplit("/", 1)[-1]
            file_id = str(uuid.uuid4())

            # Determine content type from extension
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
            content_type_map = {
                "pdf": "application/pdf",
                "doc": "application/msword",
                "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "xls": "application/vnd.ms-excel",
                "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "png": "image/png",
                "jpg": "image/jpeg",
                "jpeg": "image/jpeg",
                "txt": "text/plain",
                "csv": "text/csv",
            }
            content_type = content_type_map.get(ext, "application/octet-stream")
            pdf_status = PdfConversionStatus.NOT_REQUIRED if ext == "pdf" else PdfConversionStatus.PENDING

            # Copy to investigation folder
            new_blob_path = blob_svc.build_blob_path(investigation.record_id, file_id, filename)
            _, version_id = await blob_svc.upload_blob(new_blob_path, data, content_type)
            checksum = BlobService.compute_checksum(data)

            # Create document record
            await metadata_svc.create_document(
                investigation_id=uuid.UUID(body.investigation_id),
                file_id=file_id,
                original_filename=filename,
                content_type=content_type,
                file_size_bytes=len(data),
                blob_path=new_blob_path,
                blob_version_id=version_id,
                checksum_sha256=checksum,
                user_id=app_user.entra_oid,
                user_name=app_user.display_name,
                pdf_conversion_status=pdf_status,
            )

            results.append(AddToInvestigationResult(blob_path=blob_path, success=True, file_id=file_id))
        except Exception as e:
            logger.error("add_to_investigation_failed", blob_path=blob_path, error=str(e))
            results.append(AddToInvestigationResult(blob_path=blob_path, success=False, error=str(e)))

    succeeded = sum(1 for r in results if r.success)
    await audit_svc.log_event(
        event_type=AuditEventType.BATCH_UPLOAD,
        user_id=app_user.entra_oid,
        user_principal_name=app_user.email,
        action="create",
        result="success" if succeeded > 0 else "failure",
        resource_type="investigation",
        resource_id=body.investigation_id,
        details={"source": "explorer", "total": len(results), "succeeded": succeeded},
    )

    return AddToInvestigationResponse(
        investigation_id=body.investigation_id,
        results=results,
        total=len(results),
        succeeded=succeeded,
        failed=len(results) - succeeded,
    )
