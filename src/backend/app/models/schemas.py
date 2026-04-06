"""Pydantic request/response schemas for the API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.enums import DocumentType, InvestigationStatus, PdfConversionStatus, ScanStatus

# ============================================================================
# Investigation Schemas
# ============================================================================


class InvestigationCreate(BaseModel):
    record_id: str = Field(min_length=1, max_length=50, pattern=r"^INVESTIGATION-\d+$")
    title: str = Field(min_length=1, max_length=500, pattern=r"^[^<>]*$")
    description: str | None = Field(None, max_length=5000, pattern=r"^[^<>]*$")


class InvestigationUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500, pattern=r"^[^<>]*$")
    description: str | None = Field(None, max_length=5000, pattern=r"^[^<>]*$")
    status: InvestigationStatus | None = None


class InvestigationResponse(BaseModel):
    id: UUID
    record_id: str
    title: str
    description: str | None
    status: InvestigationStatus
    created_by: str
    created_by_name: str | None
    created_at: datetime
    updated_at: datetime
    document_count: int = 0

    model_config = {"from_attributes": True}


# ============================================================================
# Document Version Schemas (physical binary metadata)
# ============================================================================


class DocumentVersionResponse(BaseModel):
    """Version details for a single physical binary."""

    id: UUID
    document_id: UUID
    version_number: int
    original_filename: str
    mime_type: str | None
    file_size_bytes: int
    checksum: str
    is_latest: bool
    pdf_conversion_status: PdfConversionStatus
    pdf_conversion_error: str | None = None
    pdf_converted_at: datetime | None = None
    scan_status: ScanStatus = ScanStatus.CLEAN
    scanned_at: datetime | None = None
    uploaded_by: str
    uploaded_by_name: str | None
    uploaded_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# Document Schemas (logical identity + latest version)
# ============================================================================


class DocumentResponse(BaseModel):
    """Logical document with latest version metadata inlined."""

    id: UUID
    investigation_id: UUID
    document_type: DocumentType
    title: str | None
    created_by: str
    created_by_name: str | None
    created_at: datetime
    updated_at: datetime

    # Latest version fields (inlined for convenience)
    current_version_id: UUID | None = None
    version_number: int | None = None
    original_filename: str | None = None
    mime_type: str | None = None
    file_size_bytes: int | None = None
    checksum: str | None = None
    pdf_conversion_status: PdfConversionStatus | None = None
    uploaded_by: str | None = None
    uploaded_by_name: str | None = None
    uploaded_at: datetime | None = None

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    """Response after uploading a document."""

    document_id: UUID
    version_id: UUID
    version_number: int
    original_filename: str
    file_size_bytes: int
    checksum: str
    document_type: DocumentType
    pdf_conversion_status: PdfConversionStatus
    blob_path: str


class DocumentCreateRequest(BaseModel):
    """Request body for creating/uploading a document."""

    document_type: DocumentType = DocumentType.OTHER
    title: str | None = Field(None, max_length=500, pattern=r"^[^<>]*$")


# ============================================================================
# Admin Document Version Schemas
# ============================================================================


class AdminDocumentDetailResponse(BaseModel):
    """Full document detail with all versions — admin only."""

    id: UUID
    investigation_id: UUID
    document_type: DocumentType
    title: str | None
    created_by: str
    created_by_name: str | None
    created_at: datetime
    updated_at: datetime
    current_version_id: UUID | None
    is_deleted: bool
    versions: list[DocumentVersionResponse] = []

    model_config = {"from_attributes": True}


class RollbackResponse(BaseModel):
    """Response after rolling back a document version."""

    document_id: UUID
    rolled_back_version: int
    promoted_version: int
    new_current_version_id: UUID


# ============================================================================
# PDF Merge Schemas
# ============================================================================


class PdfMergeRequest(BaseModel):
    document_ids: list[str] = Field(min_length=2, max_length=50)

    @field_validator("document_ids")
    @classmethod
    def validate_document_ids(cls, v: list[str]) -> list[str]:
        import re

        uuid_re = re.compile(r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$")
        for did in v:
            if not uuid_re.match(did):
                raise ValueError(f"Invalid document ID format: {did}")
        return v


# ============================================================================
# Audit Log Schemas
# ============================================================================


class AuditLogEntry(BaseModel):
    id: int
    event_type: str
    event_timestamp: datetime
    user_id: str
    user_principal_name: str | None
    ip_address: str | None
    resource_type: str | None
    resource_id: str | None
    action: str
    result: str
    details: str | None
    correlation_id: str | None

    model_config = {"from_attributes": True}


class AuditLogQuery(BaseModel):
    event_type: str | None = None
    user_id: str | None = None
    resource_id: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=200)


# ============================================================================
# RBAC Schemas
# ============================================================================


class PermissionResponse(BaseModel):
    id: int
    resource: str
    action: str
    description: str | None

    model_config = {"from_attributes": True}


class RoleResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: str | None
    is_system: bool
    permissions: list[PermissionResponse] = []

    model_config = {"from_attributes": True}


class AppUserResponse(BaseModel):
    id: str
    entra_oid: str
    display_name: str
    email: str | None
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None
    roles: list[RoleResponse] = []

    model_config = {"from_attributes": True}


class UserRoleAssignment(BaseModel):
    role_names: list[str] = Field(min_length=1)


class CurrentUserResponse(BaseModel):
    id: str
    entra_oid: str
    display_name: str
    email: str | None
    roles: list[str] = []
    permissions: list[str] = []

    model_config = {"from_attributes": True}


# ============================================================================
# Search Schemas
# ============================================================================


class SearchResultItem(BaseModel):
    type: str  # "investigation" or "document"
    id: str
    title: str
    subtitle: str | None = None
    url: str


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]
    total: int
    page: int = 1
    page_size: int = 20


# ============================================================================
# Explorer Schemas
# ============================================================================


class ExplorerItem(BaseModel):
    name: str
    type: str  # "folder" or "file"
    path: str
    size: int | None = None
    last_modified: datetime | None = None
    content_type: str | None = None


class ExplorerResponse(BaseModel):
    prefix: str
    items: list[ExplorerItem]


class AddToInvestigationRequest(BaseModel):
    investigation_id: str = Field(min_length=1)
    blob_paths: list[str] = Field(min_length=1, max_length=50)


class AddToInvestigationResult(BaseModel):
    blob_path: str
    success: bool
    document_id: str | None = None
    error: str | None = None


class AddToInvestigationResponse(BaseModel):
    investigation_id: str
    results: list[AddToInvestigationResult]
    total: int
    succeeded: int
    failed: int


class CopyDocumentsRequest(BaseModel):
    document_ids: list[str] = Field(min_length=1, max_length=50)
    investigation_id: str = Field(min_length=1)


class CopyDocumentResult(BaseModel):
    document_id: str
    success: bool
    new_document_id: str | None = None
    error: str | None = None


class CopyDocumentsResponse(BaseModel):
    investigation_id: str
    results: list[CopyDocumentResult]
    total: int
    succeeded: int
    failed: int


# ============================================================================
# Batch Upload Schemas
# ============================================================================


class BatchUploadResult(BaseModel):
    filename: str
    success: bool
    document_id: str | None = None
    version_id: str | None = None
    error: str | None = None


class BatchUploadResponse(BaseModel):
    investigation_id: str
    results: list[BatchUploadResult]
    total: int
    succeeded: int
    failed: int


# ============================================================================
# Common Schemas
# ============================================================================


class PaginatedResponse(BaseModel):
    data: list
    meta: dict


class HealthResponse(BaseModel):
    status: str
    environment: str
    version: str


class ReadinessResponse(BaseModel):
    status: str
    checks: dict[str, bool]
