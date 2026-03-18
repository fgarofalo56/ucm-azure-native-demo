"""Status enums and action types for the document management system."""

from enum import StrEnum


class PdfConversionStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    NOT_REQUIRED = "not_required"


class InvestigationStatus(StrEnum):
    ACTIVE = "active"
    CLOSED = "closed"
    ARCHIVED = "archived"


class MigrationStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class DocumentType(StrEnum):
    """FSIS document type taxonomy for rule-based merge ordering."""

    INVESTIGATION_REPORT = "investigation_report"
    INSPECTION_FORM = "inspection_form"
    LABORATORY_RESULT = "laboratory_result"
    CORRESPONDENCE = "correspondence"
    SUPPORTING_EVIDENCE = "supporting_evidence"
    LEGAL_DOCUMENT = "legal_document"
    OTHER = "other"


# Merge order: lower number = earlier in merged PDF
MERGE_ORDER_CONFIG: dict[DocumentType, int] = {
    DocumentType.INVESTIGATION_REPORT: 10,
    DocumentType.INSPECTION_FORM: 20,
    DocumentType.LABORATORY_RESULT: 30,
    DocumentType.LEGAL_DOCUMENT: 40,
    DocumentType.CORRESPONDENCE: 50,
    DocumentType.SUPPORTING_EVIDENCE: 60,
    DocumentType.OTHER: 99,
}


class ScanStatus(StrEnum):
    """Malware scan status for two-phase upload pipeline."""

    PENDING = "pending"
    SCANNING = "scanning"
    CLEAN = "clean"
    INFECTED = "infected"
    ERROR = "error"


class AuditAction(StrEnum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    MERGE = "merge"
    ROLLBACK = "rollback"


class AuditResult(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"
    DENIED = "denied"


class AuditEventType(StrEnum):
    DOCUMENT_UPLOAD = "document.upload"
    DOCUMENT_DOWNLOAD = "document.download"
    DOCUMENT_DELETE = "document.delete"
    DOCUMENT_PDF_CONVERTED = "document.pdf_converted"
    DOCUMENT_MERGE = "document.merge"
    DOCUMENT_VERSION_ACCESS = "document.version_access"
    DOCUMENT_ROLLBACK = "document.rollback"
    DOCUMENT_SCAN_RESULT = "document.scan_result"
    INVESTIGATION_CREATE = "investigation.create"
    INVESTIGATION_UPDATE = "investigation.update"
    AUTH_LOGIN = "auth.login"
    AUTH_LOGOUT = "auth.logout"
    AUTH_DENIED = "auth.denied"
    USER_ROLE_CHANGED = "user.role_changed"
    EXPLORER_BROWSE = "explorer.browse"
    EXPLORER_DELETE = "explorer.delete"
    SEARCH_QUERY = "search.query"
    BATCH_UPLOAD = "document.batch_upload"
