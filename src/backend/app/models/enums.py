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


class AuditAction(StrEnum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    MERGE = "merge"


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
