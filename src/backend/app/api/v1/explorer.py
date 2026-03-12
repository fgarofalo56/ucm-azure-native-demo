"""File explorer endpoint for browsing blob storage."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Query

from app.db.models import AppUser
from app.dependencies import get_blob_service_client
from app.middleware.auth import require_permission
from app.models.schemas import ExplorerItem, ExplorerResponse
from app.services.blob_service import BlobService

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
            errors.append(f"{path}: {str(e)}")

    return {"deleted": deleted, "errors": errors}
