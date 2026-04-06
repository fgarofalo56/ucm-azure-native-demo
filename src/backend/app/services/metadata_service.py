"""Azure SQL metadata CRUD operations via SQLAlchemy — version-aware."""

from datetime import datetime
from uuid import UUID

import structlog
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document, DocumentVersion, Investigation
from app.models.enums import DocumentType, InvestigationStatus, PdfConversionStatus

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
        result = await self._session.execute(select(Investigation).where(Investigation.id == investigation_id))
        return result.scalar_one_or_none()

    async def get_investigation_by_record_id(self, record_id: str) -> Investigation | None:
        result = await self._session.execute(select(Investigation).where(Investigation.record_id == record_id))
        return result.scalar_one_or_none()

    async def list_investigations(
        self,
        status: InvestigationStatus | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Investigation], int, dict[str, int]]:
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

        if search:
            from sqlalchemy import or_

            pattern = f"%{search}%"
            search_filter = or_(
                Investigation.title.ilike(pattern),
                Investigation.record_id.ilike(pattern),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        if status:
            query = query.where(Investigation.status == status)
            count_query = count_query.where(Investigation.status == status)

        total = (await self._session.execute(count_query)).scalar() or 0

        # Get global status counts (ignoring current status filter, but respecting search)
        status_counts_query = select(Investigation.status, func.count()).group_by(Investigation.status)
        if search:
            from sqlalchemy import or_

            pattern = f"%{search}%"
            status_counts_query = status_counts_query.where(
                or_(
                    Investigation.title.ilike(pattern),
                    Investigation.record_id.ilike(pattern),
                )
            )
        status_counts_result = await self._session.execute(status_counts_query)
        status_counts: dict[str, int] = {}
        for row in status_counts_result.all():
            status_counts[row[0].value if hasattr(row[0], "value") else str(row[0])] = row[1]

        result = await self._session.execute(
            query.order_by(Investigation.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        )

        investigations = []
        for row in result.all():
            inv = row[0]
            inv.document_count = row[1]  # type: ignore[attr-defined]
            investigations.append(inv)
        return investigations, total, status_counts

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

        await self._session.execute(update(Investigation).where(Investigation.id == investigation_id).values(**values))
        return await self.get_investigation(investigation_id)

    async def soft_delete_investigation(self, investigation_id: UUID, user_id: str) -> None:
        """Soft-delete an investigation and all its documents."""
        investigation = await self.get_investigation(investigation_id)
        if not investigation:
            return

        now = datetime.utcnow()
        investigation.status = InvestigationStatus.ARCHIVED
        investigation.updated_at = now

        # Soft-delete all documents
        for doc in investigation.documents:
            if not doc.is_deleted:
                doc.is_deleted = True
                doc.deleted_at = now
                doc.deleted_by = user_id

        await self._session.flush()

    # ========================================================================
    # Document operations (logical)
    # ========================================================================

    async def create_document_with_version(
        self,
        investigation_id: UUID,
        original_filename: str,
        mime_type: str | None,
        file_size_bytes: int,
        blob_path_original: str,
        checksum: str,
        user_id: str,
        user_name: str | None,
        document_type: DocumentType = DocumentType.OTHER,
        title: str | None = None,
        pdf_conversion_status: PdfConversionStatus = PdfConversionStatus.PENDING,
    ) -> tuple[Document, DocumentVersion]:
        """Create a new logical document with its first version (v1)."""
        document = Document(
            investigation_id=investigation_id,
            document_type=document_type,
            title=title or original_filename,
            created_by=user_id,
            created_by_name=user_name,
        )
        self._session.add(document)
        await self._session.flush()

        version = DocumentVersion(
            document_id=document.id,
            version_number=1,
            original_filename=original_filename,
            mime_type=mime_type,
            file_size_bytes=file_size_bytes,
            blob_path_original=blob_path_original,
            checksum=checksum,
            is_latest=True,
            pdf_conversion_status=pdf_conversion_status,
            uploaded_by=user_id,
            uploaded_by_name=user_name,
        )
        self._session.add(version)
        await self._session.flush()

        document.current_version_id = version.id
        await self._session.flush()

        logger.info(
            "document_created",
            document_id=str(document.id),
            version_id=str(version.id),
            investigation_id=str(investigation_id),
        )
        return document, version

    async def add_version(
        self,
        document_id: UUID,
        original_filename: str,
        mime_type: str | None,
        file_size_bytes: int,
        blob_path_original: str,
        checksum: str,
        user_id: str,
        user_name: str | None,
        pdf_conversion_status: PdfConversionStatus = PdfConversionStatus.PENDING,
    ) -> DocumentVersion:
        """Add a new version to an existing document. Demotes previous latest."""
        # Demote current latest
        await self._session.execute(
            update(DocumentVersion)
            .where(DocumentVersion.document_id == document_id, DocumentVersion.is_latest == True)  # noqa: E712
            .values(is_latest=False)
        )

        # Get next version number
        max_ver_result = await self._session.execute(
            select(func.max(DocumentVersion.version_number)).where(DocumentVersion.document_id == document_id)
        )
        max_ver = max_ver_result.scalar() or 0

        version = DocumentVersion(
            document_id=document_id,
            version_number=max_ver + 1,
            original_filename=original_filename,
            mime_type=mime_type,
            file_size_bytes=file_size_bytes,
            blob_path_original=blob_path_original,
            checksum=checksum,
            is_latest=True,
            pdf_conversion_status=pdf_conversion_status,
            uploaded_by=user_id,
            uploaded_by_name=user_name,
        )
        self._session.add(version)
        await self._session.flush()

        # Update document pointer
        await self._session.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(current_version_id=version.id, updated_at=datetime.utcnow())
        )

        logger.info(
            "version_added",
            document_id=str(document_id),
            version_id=str(version.id),
            version_number=version.version_number,
        )
        return version

    async def get_document(self, document_id: UUID) -> Document | None:
        result = await self._session.execute(
            select(Document).where(Document.id == document_id, Document.is_deleted == False)  # noqa: E712
        )
        return result.scalar_one_or_none()

    async def get_document_with_latest_version(self, document_id: UUID) -> Document | None:
        """Get document with versions eagerly loaded (latest first via relationship ordering)."""
        return await self.get_document(document_id)

    async def list_documents_for_investigation(
        self,
        investigation_id: UUID,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Document], int]:
        """List logical documents for an investigation. Versions loaded via selectin."""
        base = select(Document).where(
            Document.investigation_id == investigation_id,
            Document.is_deleted == False,  # noqa: E712
        )
        count_query = (
            select(func.count())
            .select_from(Document)
            .where(
                Document.investigation_id == investigation_id,
                Document.is_deleted == False,  # noqa: E712
            )
        )

        total = (await self._session.execute(count_query)).scalar() or 0
        result = await self._session.execute(
            base.order_by(Document.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        )
        return list(result.scalars().all()), total

    async def get_version(self, version_id: UUID) -> DocumentVersion | None:
        result = await self._session.execute(select(DocumentVersion).where(DocumentVersion.id == version_id))
        return result.scalar_one_or_none()

    async def list_versions_for_document(self, document_id: UUID) -> list[DocumentVersion]:
        """List all versions for a document (admin only), ordered by version_number desc."""
        result = await self._session.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number.desc())
        )
        return list(result.scalars().all())

    async def rollback_version(self, document_id: UUID) -> tuple[DocumentVersion, DocumentVersion]:
        """Roll back to the previous version. Returns (demoted_version, promoted_version).

        Raises ValueError if only one version exists.
        """
        versions = await self.list_versions_for_document(document_id)
        if len(versions) < 2:
            raise ValueError("Cannot rollback: only one version exists")

        latest = versions[0]
        previous = versions[1]

        # Demote latest
        latest.is_latest = False
        # Promote previous
        previous.is_latest = True

        # Update document pointer
        await self._session.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(current_version_id=previous.id, updated_at=datetime.utcnow())
        )
        await self._session.flush()

        logger.info(
            "version_rolled_back",
            document_id=str(document_id),
            from_version=latest.version_number,
            to_version=previous.version_number,
        )
        return latest, previous

    async def update_version_pdf_status(
        self,
        version_id: UUID,
        status: PdfConversionStatus,
        pdf_path: str | None = None,
        error: str | None = None,
    ) -> None:
        values: dict = {"pdf_conversion_status": status}
        if pdf_path:
            values["blob_path_pdf"] = pdf_path
            values["pdf_converted_at"] = datetime.utcnow()
        if error:
            values["pdf_conversion_error"] = error

        await self._session.execute(update(DocumentVersion).where(DocumentVersion.id == version_id).values(**values))

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
