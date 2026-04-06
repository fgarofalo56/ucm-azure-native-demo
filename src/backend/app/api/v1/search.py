"""Global search endpoint across investigations and documents — metadata-first."""

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AppUser, Document, DocumentVersion, Investigation
from app.db.session import get_db_session
from app.middleware.auth import get_app_user
from app.models.schemas import SearchResponse, SearchResultItem

logger = structlog.get_logger()
router = APIRouter()


@router.get("", response_model=SearchResponse)
async def search_all(
    q: str = Query(min_length=2, max_length=200),
    type: str | None = Query(None, pattern="^(investigation|document)$"),
    app_user: AppUser = Depends(get_app_user),
    session: AsyncSession = Depends(get_db_session),
) -> SearchResponse:
    """Search investigations and documents using SQL LIKE.

    Documents are searched by title and latest version filename.
    No blob listing — all retrieval is metadata-driven.
    """
    pattern = f"%{q}%"
    results: list[SearchResultItem] = []

    if type is None or type == "investigation":
        inv_query = (
            select(Investigation)
            .where(
                or_(
                    Investigation.title.ilike(pattern),
                    Investigation.description.ilike(pattern),
                    Investigation.record_id.ilike(pattern),
                )
            )
            .limit(20)
        )
        inv_result = await session.execute(inv_query)
        for inv in inv_result.scalars().all():
            results.append(
                SearchResultItem(
                    type="investigation",
                    id=str(inv.id),
                    title=inv.title or inv.record_id,
                    subtitle=inv.record_id,
                    url=f"/investigations/{inv.id}",
                )
            )

    if type is None or type == "document":
        # Search by document title or latest version filename (via join)
        doc_query = (
            select(Document)
            .join(DocumentVersion, DocumentVersion.document_id == Document.id)
            .where(
                Document.is_deleted == False,  # noqa: E712
                DocumentVersion.is_latest == True,  # noqa: E712
                or_(
                    Document.title.ilike(pattern),
                    DocumentVersion.original_filename.ilike(pattern),
                ),
            )
            .limit(20)
        )
        doc_result = await session.execute(doc_query)
        for doc in doc_result.scalars().unique().all():
            latest = doc.latest_version
            display_name = doc.title or (latest.original_filename if latest else "Untitled")
            results.append(
                SearchResultItem(
                    type="document",
                    id=str(doc.id),
                    title=display_name,
                    subtitle=f"Investigation: {doc.investigation_id}",
                    url=f"/investigations/{doc.investigation_id}",
                )
            )

    return SearchResponse(
        query=q,
        results=results,
        total=len(results),
    )
