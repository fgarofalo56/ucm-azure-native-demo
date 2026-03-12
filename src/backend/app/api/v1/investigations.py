"""Investigation CRUD and document listing endpoints."""

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AppUser
from app.db.session import get_db_session
from app.middleware.auth import require_permission
from app.models.enums import InvestigationStatus
from app.models.schemas import (
    DocumentResponse,
    InvestigationCreate,
    InvestigationResponse,
    InvestigationUpdate,
    PaginatedResponse,
)
from app.services.metadata_service import MetadataService

logger = structlog.get_logger()
router = APIRouter()


@router.post("/", response_model=InvestigationResponse, status_code=status.HTTP_201_CREATED)
async def create_investigation(
    body: InvestigationCreate,
    app_user: Annotated[AppUser, Depends(require_permission("investigations", "create"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> InvestigationResponse:
    """Create a new investigation."""
    metadata_svc = MetadataService(session)

    # Check for duplicate record_id
    existing = await metadata_svc.get_investigation_by_record_id(body.record_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Investigation with record_id {body.record_id} already exists",
        )

    investigation = await metadata_svc.create_investigation(
        record_id=body.record_id,
        title=body.title,
        description=body.description,
        user_id=app_user.entra_oid,
        user_name=app_user.display_name,
    )

    return InvestigationResponse.model_validate(investigation)


@router.get("/", response_model=PaginatedResponse)
async def list_investigations(
    app_user: Annotated[AppUser, Depends(require_permission("investigations", "read"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    status_filter: InvestigationStatus | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse:
    """List all investigations with optional status filter."""
    metadata_svc = MetadataService(session)
    investigations, total = await metadata_svc.list_investigations(
        status=status_filter,
        page=page,
        page_size=page_size,
    )

    data = [InvestigationResponse.model_validate(inv) for inv in investigations]

    return PaginatedResponse(
        data=data,
        meta={"page": page, "page_size": page_size, "total": total},
    )


@router.get("/{investigation_id}", response_model=InvestigationResponse)
async def get_investigation(
    investigation_id: uuid.UUID,
    app_user: Annotated[AppUser, Depends(require_permission("investigations", "read"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> InvestigationResponse:
    """Get investigation details by ID."""
    metadata_svc = MetadataService(session)
    investigation = await metadata_svc.get_investigation(investigation_id)
    if not investigation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found")

    response = InvestigationResponse.model_validate(investigation)
    response.document_count = len(investigation.documents)
    return response


@router.patch("/{investigation_id}", response_model=InvestigationResponse)
async def update_investigation(
    investigation_id: uuid.UUID,
    body: InvestigationUpdate,
    app_user: Annotated[AppUser, Depends(require_permission("investigations", "update"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> InvestigationResponse:
    """Update investigation metadata."""
    metadata_svc = MetadataService(session)

    investigation = await metadata_svc.update_investigation(
        investigation_id=investigation_id,
        title=body.title,
        description=body.description,
        status=body.status,
    )
    if not investigation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found")

    return InvestigationResponse.model_validate(investigation)


@router.get("/{investigation_id}/documents", response_model=PaginatedResponse)
async def list_investigation_documents(
    investigation_id: uuid.UUID,
    app_user: Annotated[AppUser, Depends(require_permission("documents", "read"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
) -> PaginatedResponse:
    """List all documents for a specific investigation."""
    metadata_svc = MetadataService(session)

    # Verify investigation exists
    investigation = await metadata_svc.get_investigation(investigation_id)
    if not investigation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found")

    documents, total = await metadata_svc.list_documents_for_investigation(
        investigation_id=investigation_id,
        page=page,
        page_size=page_size,
    )

    return PaginatedResponse(
        data=[DocumentResponse.model_validate(doc) for doc in documents],
        meta={"page": page, "page_size": page_size, "total": total},
    )
