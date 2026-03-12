"""Azure SQL metadata CRUD operations via SQLAlchemy."""

from datetime import datetime
from uuid import UUID

import structlog
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document, Investigation
from app.models.enums import InvestigationStatus, PdfConversionStatus

logger = structlog.get_logger()


class MetadataService:
    """Manages document and investigation metadata in Azure SQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ========================================================================
    # Investigation operations
    # ========================================================================

    async def create_investigation(
        self,
        record_id: str,
        title: str,
        description: str | None,
        user_id: str,
        user_name: str | None,
    ) -> Investigation:
        investigation = Investigation(
            record_id=record_id,
            title=title,
            description=description,
            created_by=user_id,
            created_by_name=user_name,
        )
        self._session.add(investigation)
        await self._session.flush()
        logger.info("investigation_created", record_id=record_id, id=str(investigation.id))
        return investigation

    async def get_investigation(self, investigation_id: UUID) -> Investigation | None:
        result = await self._session.execute(
            select(Investigation).where(Investigation.id == investigation_id)
        )
        return result.scalar_one_or_none()

    async def get_investigation_by_record_id(self, record_id: str) -> Investigation | None:
        result = await self._session.execute(
            select(Investigation).where(Investigation.record_id == record_id)
        )
        return result.scalar_one_or_none()

    async def list_investigations(
        self,
        status: InvestigationStatus | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Investigation], int]:
        # Use a COUNT subquery instead of loading all documents via selectin
        doc_count_subq = (
            select(func.count())
            .where(
                Document.investigation_id == Investigation.id,
                Document.is_deleted == False,  # noqa: E712
            )
            .correlate(Investigation)
            .scalar_subquery()
            .label("document_count")
        )

        query = select(Investigation, doc_count_subq)
        count_query = select(func.count()).select_from(Investigation)

        if status:
            query = query.where(Investigation.status == status)
            count_query = count_query.where(Investigation.status == status)

        total = (await self._session.execute(count_query)).scalar() or 0
        result = await self._session.execute(
            query.order_by(Investigation.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        investigations = []
        for row in result.all():
            inv = row[0]
            inv.document_count = row[1]  # type: ignore[attr-defined]
            investigations.append(inv)
        return investigations, total

    async def update_investigation(
        self,
        investigation_id: UUID,
        title: str | None = None,
        description: str | None = None,
        status: InvestigationStatus | None = None,
    ) -> Investigation | None:
        values: dict = {"updated_at": datetime.utcnow()}
        if title is not None:
            values["title"] = title
        if description is not None:
            values["description"] = description
        if status is not None:
            values["status"] = status

        await self._session.execute(
            update(Investigation).where(Investigation.id == investigation_id).values(**values)
        )
        return await self.get_investigation(investigation_id)

    # ========================================================================
    # Document operations
    # ========================================================================

    async def create_document(
        self,
        investigation_id: UUID,
        file_id: str,
        original_filename: str,
        content_type: str | None,
        file_size_bytes: int,
        blob_path: str,
        blob_version_id: str,
        checksum_sha256: str,
        user_id: str,
        user_name: str | None,
        pdf_conversion_status: PdfConversionStatus = PdfConversionStatus.PENDING,
    ) -> Document:
        document = Document(
            investigation_id=investigation_id,
            file_id=file_id,
            original_filename=original_filename,
            content_type=content_type,
            file_size_bytes=file_size_bytes,
            blob_path=blob_path,
            blob_version_id=blob_version_id,
            checksum_sha256=checksum_sha256,
            uploaded_by=user_id,
            uploaded_by_name=user_name,
            pdf_conversion_status=pdf_conversion_status,
        )
        self._session.add(document)
        await self._session.flush()
        logger.info("document_created", file_id=file_id, investigation_id=str(investigation_id))
        return document

    async def get_document(self, document_id: UUID) -> Document | None:
        result = await self._session.execute(
            select(Document).where(Document.id == document_id, Document.is_deleted == False)  # noqa: E712
        )
        return result.scalar_one_or_none()

    async def get_document_by_file_id(self, file_id: str) -> Document | None:
        result = await self._session.execute(
            select(Document).where(Document.file_id == file_id, Document.is_deleted == False)  # noqa: E712
        )
        return result.scalar_one_or_none()

    async def list_documents_for_investigation(
        self,
        investigation_id: UUID,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Document], int]:
        base = select(Document).where(
            Document.investigation_id == investigation_id,
            Document.is_deleted == False,  # noqa: E712
        )
        count_query = select(func.count()).select_from(Document).where(
            Document.investigation_id == investigation_id,
            Document.is_deleted == False,  # noqa: E712
        )

        total = (await self._session.execute(count_query)).scalar() or 0
        result = await self._session.execute(
            base.order_by(Document.uploaded_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def update_pdf_status(
        self,
        file_id: str,
        status: PdfConversionStatus,
        pdf_path: str | None = None,
        error: str | None = None,
    ) -> None:
        values: dict = {
            "pdf_conversion_status": status,
            "updated_at": datetime.utcnow(),
        }
        if pdf_path:
            values["pdf_path"] = pdf_path
            values["pdf_converted_at"] = datetime.utcnow()
        if error:
            values["pdf_conversion_error"] = error

        await self._session.execute(
            update(Document).where(Document.file_id == file_id).values(**values)
        )

    async def soft_delete_document(self, document_id: UUID, user_id: str) -> None:
        await self._session.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(
                is_deleted=True,
                deleted_at=datetime.utcnow(),
                deleted_by=user_id,
                updated_at=datetime.utcnow(),
            )
        )
        logger.info("document_soft_deleted", document_id=str(document_id), user_id=user_id)
