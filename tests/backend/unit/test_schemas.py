"""Unit tests for Pydantic schemas."""

import pytest
from uuid import uuid4
from pydantic import ValidationError

from app.models.schemas import (
    InvestigationCreate,
    InvestigationUpdate,
    PdfMergeRequest,
    AuditLogQuery,
    DocumentCreateRequest,
)
from app.models.enums import DocumentType, InvestigationStatus


class TestInvestigationCreate:
    def test_valid_creation(self):
        """Should create investigation with valid data."""
        data = InvestigationCreate(
            record_id="INVESTIGATION-12345",
            title="Test Investigation",
            description="A test description",
        )
        assert data.record_id == "INVESTIGATION-12345"
        assert data.title == "Test Investigation"
        assert data.description == "A test description"

    def test_valid_record_id_patterns(self):
        """Should accept valid record ID patterns."""
        valid_patterns = [
            "INVESTIGATION-1",
            "INVESTIGATION-123",
            "INVESTIGATION-999999",
            "INVESTIGATION-0001",
        ]

        for pattern in valid_patterns:
            data = InvestigationCreate(record_id=pattern, title="Test")
            assert data.record_id == pattern

    def test_invalid_record_id_pattern(self):
        """Should reject invalid record ID patterns."""
        invalid_patterns = [
            ("INVALID-ID", "string_pattern_mismatch"),
            ("investigation-123", "string_pattern_mismatch"),  # lowercase
            ("INVESTIGATION-", "string_pattern_mismatch"),     # no number
            ("INVESTIGATION-ABC", "string_pattern_mismatch"),  # letters instead of numbers
            ("123-INVESTIGATION", "string_pattern_mismatch"),  # reversed
            ("INVESTIGATION", "string_pattern_mismatch"),      # missing dash and number
            ("", "string_too_short"),                          # empty - fails length validation first
        ]

        for pattern, expected_error_type in invalid_patterns:
            with pytest.raises(ValidationError) as exc_info:
                InvestigationCreate(record_id=pattern, title="Test")

            error = exc_info.value.errors()[0]
            assert error["type"] == expected_error_type, f"For pattern '{pattern}', expected '{expected_error_type}' but got '{error['type']}'"

    def test_title_with_html_tags(self):
        """Should reject titles containing HTML-like content."""
        invalid_titles = [
            "<script>alert('xss')</script>",
            "<div>content</div>",
            "Title with <b>bold</b> text",
            "Test < and > symbols",
        ]

        for title in invalid_titles:
            with pytest.raises(ValidationError) as exc_info:
                InvestigationCreate(record_id="INVESTIGATION-123", title=title)

            error = exc_info.value.errors()[0]
            assert error["type"] == "string_pattern_mismatch"

    def test_valid_title_patterns(self):
        """Should accept valid titles without HTML."""
        valid_titles = [
            "Simple title",
            "Title with numbers 123",
            "Title with special chars: !, @, #, $, %, &",
            "Title with 'single' and \"double\" quotes",
            "Very long title " * 10,  # Long but under limit
        ]

        for title in valid_titles:
            data = InvestigationCreate(record_id="INVESTIGATION-123", title=title)
            assert data.title == title

    def test_empty_title(self):
        """Should reject empty title."""
        with pytest.raises(ValidationError) as exc_info:
            InvestigationCreate(record_id="INVESTIGATION-123", title="")

        error = exc_info.value.errors()[0]
        assert error["type"] == "string_too_short"

    def test_title_too_long(self):
        """Should reject titles over 500 characters."""
        long_title = "x" * 501
        with pytest.raises(ValidationError) as exc_info:
            InvestigationCreate(record_id="INVESTIGATION-123", title=long_title)

        error = exc_info.value.errors()[0]
        assert error["type"] == "string_too_long"

    def test_record_id_too_long(self):
        """Should reject record IDs over 50 characters."""
        long_id = "INVESTIGATION-" + "x" * 50
        with pytest.raises(ValidationError) as exc_info:
            InvestigationCreate(record_id=long_id, title="Test")

        error = exc_info.value.errors()[0]
        assert error["type"] == "string_too_long"

    def test_description_optional(self):
        """Should allow missing description."""
        data = InvestigationCreate(record_id="INVESTIGATION-123", title="Test")
        assert data.description is None

    def test_description_with_html_rejected(self):
        """Should reject descriptions containing HTML."""
        with pytest.raises(ValidationError) as exc_info:
            InvestigationCreate(
                record_id="INVESTIGATION-123",
                title="Test",
                description="Description with <script>alert('xss')</script>"
            )

        error = exc_info.value.errors()[0]
        assert error["type"] == "string_pattern_mismatch"

    def test_description_too_long(self):
        """Should reject descriptions over 5000 characters."""
        long_description = "x" * 5001
        with pytest.raises(ValidationError) as exc_info:
            InvestigationCreate(
                record_id="INVESTIGATION-123",
                title="Test",
                description=long_description
            )

        error = exc_info.value.errors()[0]
        assert error["type"] == "string_too_long"


class TestInvestigationUpdate:
    def test_partial_update(self):
        """Should allow partial updates."""
        data = InvestigationUpdate(title="New Title")
        assert data.title == "New Title"
        assert data.status is None
        assert data.description is None

    def test_status_update(self):
        """Should accept valid status updates."""
        data = InvestigationUpdate(status=InvestigationStatus.CLOSED)
        assert data.status == InvestigationStatus.CLOSED

    def test_all_fields_update(self):
        """Should allow updating all fields."""
        data = InvestigationUpdate(
            title="Updated Title",
            description="Updated description",
            status=InvestigationStatus.ARCHIVED
        )
        assert data.title == "Updated Title"
        assert data.description == "Updated description"
        assert data.status == InvestigationStatus.ARCHIVED

    def test_empty_update(self):
        """Should allow empty update (all fields None)."""
        data = InvestigationUpdate()
        assert data.title is None
        assert data.description is None
        assert data.status is None

    def test_title_validation_same_as_create(self):
        """Should apply same title validation as InvestigationCreate."""
        with pytest.raises(ValidationError):
            InvestigationUpdate(title="<script>alert('xss')</script>")

        with pytest.raises(ValidationError):
            InvestigationUpdate(title="")

        with pytest.raises(ValidationError):
            InvestigationUpdate(title="x" * 501)


class TestPdfMergeRequest:
    def test_valid_request(self):
        """Should accept valid document IDs."""
        ids = [str(uuid4()), str(uuid4()), str(uuid4())]
        data = PdfMergeRequest(document_ids=ids)
        assert len(data.document_ids) == 3
        assert data.document_ids == ids

    def test_minimum_documents(self):
        """Should accept exactly 2 documents."""
        ids = [str(uuid4()), str(uuid4())]
        data = PdfMergeRequest(document_ids=ids)
        assert len(data.document_ids) == 2

    def test_too_few_documents(self):
        """Should reject single document."""
        with pytest.raises(ValidationError) as exc_info:
            PdfMergeRequest(document_ids=[str(uuid4())])

        error = exc_info.value.errors()[0]
        assert error["type"] == "too_short"

    def test_too_many_documents(self):
        """Should reject over 50 documents."""
        ids = [str(uuid4()) for _ in range(51)]
        with pytest.raises(ValidationError) as exc_info:
            PdfMergeRequest(document_ids=ids)

        error = exc_info.value.errors()[0]
        assert error["type"] == "too_long"

    def test_invalid_uuid_format(self):
        """Should reject invalid UUID formats."""
        invalid_uuids = [
            "not-a-uuid",
            "12345678-1234-1234-1234",  # too short
            "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",  # invalid characters
            "12345678-1234-1234-1234-12345678901g",  # invalid character at end
            "",
            "123",
            "12345678123412341234123456789012",  # no dashes
            "12345678-xxxx-xxxx-xxxx-xxxxxxxxxxxx",  # mix of valid and invalid
        ]

        for invalid_uuid in invalid_uuids:
            with pytest.raises(ValidationError) as exc_info:
                PdfMergeRequest(document_ids=[invalid_uuid, str(uuid4())])

            # Should contain a validation error about the UUID format
            errors = exc_info.value.errors()
            assert len(errors) > 0, f"Expected validation error for UUID: {invalid_uuid}"

    def test_mixed_valid_invalid_uuids(self):
        """Should reject request with mix of valid and invalid UUIDs."""
        ids = [str(uuid4()), "not-a-uuid", str(uuid4())]
        with pytest.raises(ValidationError):
            PdfMergeRequest(document_ids=ids)

    def test_empty_document_list(self):
        """Should reject empty document list."""
        with pytest.raises(ValidationError) as exc_info:
            PdfMergeRequest(document_ids=[])

        error = exc_info.value.errors()[0]
        assert error["type"] == "too_short"

    def test_uppercase_uuids_rejected(self):
        """Should reject uppercase UUIDs (validator expects lowercase)."""
        uuid_str = str(uuid4()).upper()
        with pytest.raises(ValidationError) as exc_info:
            PdfMergeRequest(document_ids=[uuid_str, str(uuid4())])

        error = exc_info.value.errors()[0]
        assert "Invalid document ID format" in str(error["ctx"]["error"])


class TestAuditLogQuery:
    def test_defaults(self):
        """Should have correct default values."""
        query = AuditLogQuery()
        assert query.page == 1
        assert query.page_size == 50
        assert query.event_type is None
        assert query.user_id is None
        assert query.resource_id is None
        assert query.start_date is None
        assert query.end_date is None

    def test_page_size_limit(self):
        """Should reject page sizes over 200."""
        with pytest.raises(ValidationError) as exc_info:
            AuditLogQuery(page_size=300)

        error = exc_info.value.errors()[0]
        assert error["type"] == "less_than_equal"

    def test_page_size_minimum(self):
        """Should reject page sizes under 1."""
        with pytest.raises(ValidationError) as exc_info:
            AuditLogQuery(page_size=0)

        error = exc_info.value.errors()[0]
        assert error["type"] == "greater_than_equal"

    def test_page_minimum(self):
        """Should reject page numbers under 1."""
        with pytest.raises(ValidationError) as exc_info:
            AuditLogQuery(page=0)

        error = exc_info.value.errors()[0]
        assert error["type"] == "greater_than_equal"

    def test_valid_page_size_range(self):
        """Should accept valid page sizes."""
        valid_sizes = [1, 10, 50, 100, 200]
        for size in valid_sizes:
            query = AuditLogQuery(page_size=size)
            assert query.page_size == size

    def test_valid_page_range(self):
        """Should accept valid page numbers."""
        valid_pages = [1, 10, 100, 1000]
        for page in valid_pages:
            query = AuditLogQuery(page=page)
            assert query.page == page

    def test_optional_filters(self):
        """Should accept optional filter parameters."""
        query = AuditLogQuery(
            event_type="document.upload",
            user_id="user-123",
            resource_id="doc-456"
        )
        assert query.event_type == "document.upload"
        assert query.user_id == "user-123"
        assert query.resource_id == "doc-456"


class TestDocumentCreateRequest:
    def test_default_type(self):
        """Should default to OTHER document type."""
        data = DocumentCreateRequest()
        assert data.document_type == DocumentType.OTHER
        assert data.title is None

    def test_with_title(self):
        """Should accept title and document type."""
        data = DocumentCreateRequest(
            title="Test Document",
            document_type=DocumentType.INSPECTION_FORM
        )
        assert data.title == "Test Document"
        assert data.document_type == DocumentType.INSPECTION_FORM

    def test_all_document_types(self):
        """Should accept all valid document types."""
        for doc_type in DocumentType:
            data = DocumentCreateRequest(document_type=doc_type)
            assert data.document_type == doc_type

    def test_title_with_html_rejected(self):
        """Should reject titles with HTML content."""
        with pytest.raises(ValidationError) as exc_info:
            DocumentCreateRequest(title="<script>alert('xss')</script>")

        error = exc_info.value.errors()[0]
        assert error["type"] == "string_pattern_mismatch"

    def test_title_too_long(self):
        """Should reject titles over 500 characters."""
        long_title = "x" * 501
        with pytest.raises(ValidationError) as exc_info:
            DocumentCreateRequest(title=long_title)

        error = exc_info.value.errors()[0]
        assert error["type"] == "string_too_long"

    def test_empty_title_allowed(self):
        """Should allow None title (optional field)."""
        data = DocumentCreateRequest(title=None)
        assert data.title is None

    def test_valid_titles(self):
        """Should accept valid titles."""
        valid_titles = [
            "Simple title",
            "Title with numbers 123",
            "Title with punctuation!",
            "Title with 'quotes'",
        ]

        for title in valid_titles:
            data = DocumentCreateRequest(title=title)
            assert data.title == title