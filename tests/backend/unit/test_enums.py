"""Unit tests for model enums."""

from app.models.enums import (
    PdfConversionStatus,
    InvestigationStatus,
    DocumentType,
    ScanStatus,
    MigrationStatus,
    AuditAction,
    AuditResult,
    AuditEventType,
    MERGE_ORDER_CONFIG,
)


class TestPdfConversionStatus:
    def test_status_values(self):
        """Should have expected status values."""
        assert PdfConversionStatus.PENDING == "pending"
        assert PdfConversionStatus.PROCESSING == "processing"
        assert PdfConversionStatus.COMPLETED == "completed"
        assert PdfConversionStatus.FAILED == "failed"
        assert PdfConversionStatus.NOT_REQUIRED == "not_required"

    def test_all_statuses_present(self):
        """Should have all expected statuses."""
        expected_statuses = {
            "pending", "processing", "completed", "failed", "not_required"
        }
        actual_statuses = {status.value for status in PdfConversionStatus}
        assert actual_statuses == expected_statuses

    def test_enum_membership(self):
        """Should be able to check membership."""
        assert PdfConversionStatus.PENDING in PdfConversionStatus
        assert "invalid" not in [status.value for status in PdfConversionStatus]


class TestInvestigationStatus:
    def test_status_values(self):
        """Should have expected status values."""
        assert InvestigationStatus.ACTIVE == "active"
        assert InvestigationStatus.CLOSED == "closed"
        assert InvestigationStatus.ARCHIVED == "archived"

    def test_all_statuses_present(self):
        """Should have all expected statuses."""
        expected_statuses = {"active", "closed", "archived"}
        actual_statuses = {status.value for status in InvestigationStatus}
        assert actual_statuses == expected_statuses

    def test_string_comparison(self):
        """Should be comparable with strings."""
        assert InvestigationStatus.ACTIVE == "active"
        assert str(InvestigationStatus.ACTIVE) == "active"


class TestMigrationStatus:
    def test_status_values(self):
        """Should have expected migration status values."""
        assert MigrationStatus.PENDING == "pending"
        assert MigrationStatus.IN_PROGRESS == "in_progress"
        assert MigrationStatus.COMPLETED == "completed"
        assert MigrationStatus.FAILED == "failed"
        assert MigrationStatus.SKIPPED == "skipped"

    def test_all_statuses_present(self):
        """Should have all expected migration statuses."""
        expected_statuses = {
            "pending", "in_progress", "completed", "failed", "skipped"
        }
        actual_statuses = {status.value for status in MigrationStatus}
        assert actual_statuses == expected_statuses


class TestDocumentType:
    def test_document_type_values(self):
        """Should have expected document type values."""
        assert DocumentType.INVESTIGATION_REPORT == "investigation_report"
        assert DocumentType.INSPECTION_FORM == "inspection_form"
        assert DocumentType.LABORATORY_RESULT == "laboratory_result"
        assert DocumentType.CORRESPONDENCE == "correspondence"
        assert DocumentType.SUPPORTING_EVIDENCE == "supporting_evidence"
        assert DocumentType.LEGAL_DOCUMENT == "legal_document"
        assert DocumentType.OTHER == "other"

    def test_all_document_types_present(self):
        """Should have all expected document types."""
        expected_types = {
            "investigation_report", "inspection_form", "laboratory_result",
            "correspondence", "supporting_evidence", "legal_document", "other"
        }
        actual_types = {doc_type.value for doc_type in DocumentType}
        assert actual_types == expected_types

    def test_document_types_in_merge_config(self):
        """Should have all document types in merge order config."""
        for doc_type in DocumentType:
            assert doc_type in MERGE_ORDER_CONFIG, f"{doc_type} missing from MERGE_ORDER_CONFIG"


class TestScanStatus:
    def test_scan_status_values(self):
        """Should have expected scan status values."""
        assert ScanStatus.PENDING == "pending"
        assert ScanStatus.SCANNING == "scanning"
        assert ScanStatus.CLEAN == "clean"
        assert ScanStatus.INFECTED == "infected"
        assert ScanStatus.ERROR == "error"

    def test_all_scan_statuses_present(self):
        """Should have all expected scan statuses."""
        expected_statuses = {
            "pending", "scanning", "clean", "infected", "error"
        }
        actual_statuses = {status.value for status in ScanStatus}
        assert actual_statuses == expected_statuses


class TestAuditAction:
    def test_audit_action_values(self):
        """Should have expected audit action values."""
        assert AuditAction.CREATE == "create"
        assert AuditAction.READ == "read"
        assert AuditAction.UPDATE == "update"
        assert AuditAction.DELETE == "delete"
        assert AuditAction.MERGE == "merge"
        assert AuditAction.ROLLBACK == "rollback"

    def test_all_audit_actions_present(self):
        """Should have all expected audit actions."""
        expected_actions = {
            "create", "read", "update", "delete", "merge", "rollback"
        }
        actual_actions = {action.value for action in AuditAction}
        assert actual_actions == expected_actions


class TestAuditResult:
    def test_audit_result_values(self):
        """Should have expected audit result values."""
        assert AuditResult.SUCCESS == "success"
        assert AuditResult.FAILURE == "failure"
        assert AuditResult.DENIED == "denied"

    def test_all_audit_results_present(self):
        """Should have all expected audit results."""
        expected_results = {"success", "failure", "denied"}
        actual_results = {result.value for result in AuditResult}
        assert actual_results == expected_results


class TestAuditEventType:
    def test_document_event_types(self):
        """Should have expected document-related event types."""
        document_events = [
            AuditEventType.DOCUMENT_UPLOAD,
            AuditEventType.DOCUMENT_DOWNLOAD,
            AuditEventType.DOCUMENT_DELETE,
            AuditEventType.DOCUMENT_PDF_CONVERTED,
            AuditEventType.DOCUMENT_MERGE,
            AuditEventType.DOCUMENT_VERSION_ACCESS,
            AuditEventType.DOCUMENT_ROLLBACK,
            AuditEventType.DOCUMENT_SCAN_RESULT,
            AuditEventType.BATCH_UPLOAD,
        ]

        expected_values = [
            "document.upload", "document.download", "document.delete",
            "document.pdf_converted", "document.merge", "document.version_access",
            "document.rollback", "document.scan_result", "document.batch_upload"
        ]

        for event, expected in zip(document_events, expected_values):
            assert event.value == expected

    def test_investigation_event_types(self):
        """Should have expected investigation-related event types."""
        assert AuditEventType.INVESTIGATION_CREATE == "investigation.create"
        assert AuditEventType.INVESTIGATION_UPDATE == "investigation.update"

    def test_auth_event_types(self):
        """Should have expected authentication-related event types."""
        assert AuditEventType.AUTH_LOGIN == "auth.login"
        assert AuditEventType.AUTH_LOGOUT == "auth.logout"
        assert AuditEventType.AUTH_DENIED == "auth.denied"

    def test_user_event_types(self):
        """Should have expected user-related event types."""
        assert AuditEventType.USER_ROLE_CHANGED == "user.role_changed"

    def test_explorer_event_types(self):
        """Should have expected explorer-related event types."""
        assert AuditEventType.EXPLORER_BROWSE == "explorer.browse"
        assert AuditEventType.EXPLORER_DELETE == "explorer.delete"

    def test_search_event_types(self):
        """Should have expected search-related event types."""
        assert AuditEventType.SEARCH_QUERY == "search.query"

    def test_all_event_types_present(self):
        """Should have all expected event types."""
        expected_events = {
            "document.upload", "document.download", "document.delete",
            "document.pdf_converted", "document.merge", "document.version_access",
            "document.rollback", "document.scan_result", "investigation.create",
            "investigation.update", "auth.login", "auth.logout", "auth.denied",
            "user.role_changed", "explorer.browse", "explorer.delete",
            "search.query", "document.batch_upload"
        }
        actual_events = {event.value for event in AuditEventType}
        assert actual_events == expected_events


class TestMergeOrderConfig:
    def test_merge_order_config_structure(self):
        """Should be a dictionary mapping DocumentType to int."""
        assert isinstance(MERGE_ORDER_CONFIG, dict)
        for key, value in MERGE_ORDER_CONFIG.items():
            assert isinstance(key, DocumentType)
            assert isinstance(value, int)

    def test_all_document_types_have_merge_order(self):
        """Should have merge order for all document types."""
        for doc_type in DocumentType:
            assert doc_type in MERGE_ORDER_CONFIG
            assert isinstance(MERGE_ORDER_CONFIG[doc_type], int)

    def test_merge_order_values(self):
        """Should have expected merge order values."""
        expected_orders = {
            DocumentType.INVESTIGATION_REPORT: 10,
            DocumentType.INSPECTION_FORM: 20,
            DocumentType.LABORATORY_RESULT: 30,
            DocumentType.LEGAL_DOCUMENT: 40,
            DocumentType.CORRESPONDENCE: 50,
            DocumentType.SUPPORTING_EVIDENCE: 60,
            DocumentType.OTHER: 99,
        }

        for doc_type, expected_order in expected_orders.items():
            assert MERGE_ORDER_CONFIG[doc_type] == expected_order

    def test_merge_order_ascending(self):
        """Should have investigation reports first (lowest order)."""
        investigation_order = MERGE_ORDER_CONFIG[DocumentType.INVESTIGATION_REPORT]
        other_order = MERGE_ORDER_CONFIG[DocumentType.OTHER]

        assert investigation_order < other_order
        assert investigation_order == 10  # Should be first
        assert other_order == 99  # Should be last

    def test_merge_order_uniqueness(self):
        """Should have unique merge order values (no ties except if intended)."""
        orders = list(MERGE_ORDER_CONFIG.values())
        # Check that most orders are unique (some might be intentionally the same)
        unique_orders = set(orders)
        assert len(unique_orders) >= 5  # At least 5 different ordering levels

    def test_merge_order_logical_sequence(self):
        """Should have logical sequence for FSIS workflow."""
        # Investigation reports should come first
        assert MERGE_ORDER_CONFIG[DocumentType.INVESTIGATION_REPORT] < MERGE_ORDER_CONFIG[DocumentType.INSPECTION_FORM]
        # Inspection forms should come before lab results
        assert MERGE_ORDER_CONFIG[DocumentType.INSPECTION_FORM] < MERGE_ORDER_CONFIG[DocumentType.LABORATORY_RESULT]
        # Legal documents should come before correspondence
        assert MERGE_ORDER_CONFIG[DocumentType.LEGAL_DOCUMENT] < MERGE_ORDER_CONFIG[DocumentType.CORRESPONDENCE]
        # Supporting evidence should come before OTHER
        assert MERGE_ORDER_CONFIG[DocumentType.SUPPORTING_EVIDENCE] < MERGE_ORDER_CONFIG[DocumentType.OTHER]