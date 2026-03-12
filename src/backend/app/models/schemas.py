"""Pydantic request/response schemas for the API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.enums import InvestigationStatus, PdfConversionStatus

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
# Document Schemas
# ============================================================================


class DocumentResponse(BaseModel):
    id: UUID
    investigation_id: UUID
    file_id: str
    original_filename: str = Field(max_length=255)
    content_type: str | None
    file_size_bytes: int
    pdf_conversion_status: PdfConversionStatus
    pdf_conversion_error: str | None
    pdf_converted_at: datetime | None
    checksum_sha256: str
    uploaded_by: str
    uploaded_by_name: str | None
    uploaded_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    id: UUID
    file_id: str
    original_filename: str
    file_size_bytes: int
    checksum_sha256: str
    pdf_conversion_status: PdfConversionStatus
    blob_path: str


class DocumentVersionResponse(BaseModel):
    version_id: str
    last_modified: datetime
    content_length: int
    is_current: bool


# ============================================================================
# PDF Merge Schemas
# ============================================================================


class PdfMergeRequest(BaseModel):
    file_ids: list[str] = Field(min_length=2, max_length=50)

    @field_validator("file_ids")
    @classmethod
    def validate_file_ids(cls, v: list[str]) -> list[str]:
        import re

        uuid_re = re.compile(r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$")
        for fid in v:
            if not uuid_re.match(fid):
                raise ValueError(f"Invalid file ID format: {fid}")
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
# Common Schemas
# ============================================================================


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


# ============================================================================
# Batch Upload Schemas
# ============================================================================


class BatchUploadResult(BaseModel):
    filename: str
    success: bool
    file_id: str | None = None
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
