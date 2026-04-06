"""Seed FSIS demo data with versioned document model.

Revision ID: 004_seed_data
Revises: 003_versioning
Create Date: 2026-03-17

Seeds 8 FSIS investigations with 15 documents (each with v1 DocumentVersion).
Uses real USDA/FSIS document references from https://www.fsis.usda.gov/science-data.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "004_seed_data"
down_revision: str | None = "003_versioning"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SYSTEM_USER = "system-seed"
SYSTEM_USER_NAME = "FSIS Data Seed"


def _inv(record_id, title, description, status="active"):
    return {
        "record_id": record_id,
        "title": title,
        "description": description,
        "status": status,
        "created_by": SYSTEM_USER,
        "created_by_name": SYSTEM_USER_NAME,
    }


INVESTIGATIONS = [
    _inv(
        "INVESTIGATION-10001",
        "FY2025 Annual Sampling Program",
        "FSIS Annual Sampling Program Plan and results for Fiscal Year 2025. Covers domestic microbiological and chemical sampling for beef, pork, poultry, Siluriformes, and egg products.",
    ),
    _inv(
        "INVESTIGATION-10002",
        "National Residue Program - Chemical Testing",
        "National Residue Program quarterly reports summarizing chemical residue results for meat, poultry, and egg products covering domestic and import sampling programs.",
    ),
    _inv(
        "INVESTIGATION-10003",
        "Microbiology Baseline Data Collection - Poultry",
        "Baseline microbiology data collection for estimating national prevalence and levels of bacteria of public health concern in poultry products.",
    ),
    _inv(
        "INVESTIGATION-10004",
        "Humane Handling Verification - District 50",
        "Livestock humane handling and poultry good commercial practices inspection task verification for District 50 establishments.",
    ),
    _inv(
        "INVESTIGATION-10005",
        "MPI Directory Establishment Audit",
        "Meat, Poultry, and Egg Products Inspection (MPI) Directory audit covering all FSIS-inspected establishments.",
    ),
    _inv(
        "INVESTIGATION-10006",
        "Quarterly Enforcement Review FY2024",
        "Quarterly enforcement reports covering administrative actions, suspensions, and regulatory citations for FSIS-inspected establishments.",
    ),
    _inv(
        "INVESTIGATION-10007",
        "STEC Sampling Results Analysis",
        "Shiga toxin-producing Escherichia coli (STEC) sampling program results including E. coli O157:H7 and non-O157 STEC testing in raw beef products.",
    ),
    _inv(
        "INVESTIGATION-10008",
        "Import Sampling Program Compliance",
        "Import sampling program compliance review for foreign establishment reinspection at ports of entry.",
        status="closed",
    ),
]

# (investigation_index, document_type, title, filename, mime_type, size_bytes)
DOCUMENTS = [
    # INVESTIGATION-10001
    (
        0,
        "investigation_report",
        "FSIS Annual Sampling Plan FY2025",
        "FSIS-Annual-Sampling-Plan-FY2025.pdf",
        "application/pdf",
        2457600,
    ),
    (
        0,
        "investigation_report",
        "FSIS Annual Sampling Plan FY2024",
        "FSIS-Annual-Sampling-Plan-FY2024.pdf",
        "application/pdf",
        2150400,
    ),
    # INVESTIGATION-10002
    (
        1,
        "laboratory_result",
        "National Residue Program FY2019 Results (Red Book)",
        "fy2019-red-book.pdf",
        "application/pdf",
        3276800,
    ),
    (
        1,
        "inspection_form",
        "National Residue Program FY2019 Sampling Plan (Blue Book)",
        "2019-blue-book.pdf",
        "application/pdf",
        1843200,
    ),
    (
        1,
        "laboratory_result",
        "Residue Quarterly Report FY23 Q2",
        "Dataset_QSR_Residue_Tolerances_SummaryReport_FY23Q2.pdf",
        "application/pdf",
        1024000,
    ),
    # INVESTIGATION-10003
    (
        2,
        "investigation_report",
        "FY2024 Sampling Summary Report",
        "FY2024A_Sampling-Summary-Report.pdf",
        "application/pdf",
        1740800,
    ),
    (
        2,
        "investigation_report",
        "FY2021 Sampling Summary Report",
        "FY2021-Sampling-Summary-Report.pdf",
        "application/pdf",
        1536000,
    ),
    # INVESTIGATION-10004
    (
        3,
        "inspection_form",
        "Directive 6900.2 - Humane Handling Procedures",
        "humane-handling-verification-procedures.pdf",
        "application/pdf",
        921600,
    ),
    # INVESTIGATION-10005
    (
        4,
        "supporting_evidence",
        "MPI Directory by Establishment Number",
        "MPI_Directory_by_Establishment_Number.csv",
        "text/csv",
        5242880,
    ),
    (
        4,
        "supporting_evidence",
        "MPI Directory by Establishment Name",
        "MPI_Directory_by_Establishment_Name.csv",
        "text/csv",
        5242880,
    ),
    (4, "correspondence", "CSV File Opening Guide", "CSV_Guide.pdf", "application/pdf", 204800),
    # INVESTIGATION-10006
    (
        5,
        "legal_document",
        "Quarterly Enforcement Report FY2024 Q1",
        "quarterly-enforcement-report-fy2024-q1.pdf",
        "application/pdf",
        1433600,
    ),
    # INVESTIGATION-10007
    (
        6,
        "laboratory_result",
        "STEC Testing Results FY2024",
        "FSIS-STEC-Testing-Results-FY2024.pdf",
        "application/pdf",
        1228800,
    ),
    (
        6,
        "inspection_form",
        "STEC Sampling Methodology (MLG 5C)",
        "STEC-Sampling-Methodology.pdf",
        "application/pdf",
        819200,
    ),
    # INVESTIGATION-10008
    (
        7,
        "legal_document",
        "Directive 9900.1 - Import Reinspection",
        "import-reinspection-procedures-9900.1.pdf",
        "application/pdf",
        1126400,
    ),
    (
        7,
        "investigation_report",
        "Foreign Audit Report 2024",
        "foreign-audit-report-2024.pdf",
        "application/pdf",
        2048000,
    ),
]


def upgrade() -> None:
    # Delete existing seed data (fresh re-seed)
    op.execute("DELETE FROM document_versions")
    op.execute("DELETE FROM documents")
    op.execute("DELETE FROM investigations")

    inv_table = sa.table(
        "investigations",
        sa.column("id", sa.Uuid),
        sa.column("record_id", sa.String),
        sa.column("title", sa.String),
        sa.column("description", sa.Text),
        sa.column("status", sa.String),
        sa.column("created_by", sa.String),
        sa.column("created_by_name", sa.String),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )

    doc_table = sa.table(
        "documents",
        sa.column("id", sa.Uuid),
        sa.column("investigation_id", sa.Uuid),
        sa.column("document_type", sa.String),
        sa.column("title", sa.String),
        sa.column("created_by", sa.String),
        sa.column("created_by_name", sa.String),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
        sa.column("is_deleted", sa.Boolean),
        sa.column("current_version_id", sa.Uuid),
    )

    ver_table = sa.table(
        "document_versions",
        sa.column("id", sa.Uuid),
        sa.column("document_id", sa.Uuid),
        sa.column("version_number", sa.Integer),
        sa.column("original_filename", sa.String),
        sa.column("mime_type", sa.String),
        sa.column("file_size_bytes", sa.BigInteger),
        sa.column("blob_path_original", sa.String),
        sa.column("blob_path_pdf", sa.String),
        sa.column("checksum", sa.String),
        sa.column("is_latest", sa.Boolean),
        sa.column("pdf_conversion_status", sa.String),
        sa.column("scan_status", sa.String),
        sa.column("uploaded_by", sa.String),
        sa.column("uploaded_by_name", sa.String),
        sa.column("uploaded_at", sa.DateTime),
    )

    # Insert investigations using NEWID() for each
    inv_ids = []
    for inv in INVESTIGATIONS:
        # Use raw SQL to leverage NEWID()
        result = op.get_bind().execute(
            sa.text("""
                INSERT INTO investigations (id, record_id, title, description, status,
                    created_by, created_by_name, created_at, updated_at)
                OUTPUT INSERTED.id
                VALUES (NEWID(), :record_id, :title, :description, :status,
                    :created_by, :created_by_name, GETUTCDATE(), GETUTCDATE())
            """),
            inv,
        )
        inv_id = result.fetchone()[0]  # type: ignore[index]
        inv_ids.append(inv_id)

    # Insert documents + versions
    for inv_idx, doc_type, title, filename, mime_type, size_bytes in DOCUMENTS:
        inv_id = inv_ids[inv_idx]
        record_id = INVESTIGATIONS[inv_idx]["record_id"]

        pdf_status = "not_required" if mime_type == "application/pdf" else "pending"
        # Dummy checksum (SHA-256 of filename for determinism)
        import hashlib

        checksum = hashlib.sha256(filename.encode()).hexdigest()

        # Insert document, get ID
        doc_result = op.get_bind().execute(
            sa.text("""
                INSERT INTO documents (id, investigation_id, document_type, title,
                    created_by, created_by_name, created_at, updated_at, is_deleted)
                OUTPUT INSERTED.id
                VALUES (NEWID(), :inv_id, :doc_type, :title,
                    :created_by, :created_by_name, GETUTCDATE(), GETUTCDATE(), 0)
            """),
            {
                "inv_id": inv_id,
                "doc_type": doc_type,
                "title": title,
                "created_by": SYSTEM_USER,
                "created_by_name": SYSTEM_USER_NAME,
            },
        )
        doc_id = doc_result.fetchone()[0]  # type: ignore[index]

        # Build versioned blob path
        blob_path = f"{record_id}/{doc_id}/original/v1/{filename}"

        # Insert version
        ver_result = op.get_bind().execute(
            sa.text("""
                INSERT INTO document_versions (id, document_id, version_number,
                    original_filename, mime_type, file_size_bytes, blob_path_original,
                    checksum, is_latest, pdf_conversion_status, scan_status,
                    uploaded_by, uploaded_by_name, uploaded_at)
                OUTPUT INSERTED.id
                VALUES (NEWID(), :doc_id, 1,
                    :filename, :mime_type, :size_bytes, :blob_path,
                    :checksum, 1, :pdf_status, 'clean',
                    :uploaded_by, :uploaded_by_name, GETUTCDATE())
            """),
            {
                "doc_id": doc_id,
                "filename": filename,
                "mime_type": mime_type,
                "size_bytes": size_bytes,
                "blob_path": blob_path,
                "checksum": checksum,
                "pdf_status": pdf_status,
                "uploaded_by": SYSTEM_USER,
                "uploaded_by_name": SYSTEM_USER_NAME,
            },
        )
        ver_id = ver_result.fetchone()[0]  # type: ignore[index]

        # Update document's current_version_id
        op.get_bind().execute(
            sa.text("UPDATE documents SET current_version_id = :ver_id WHERE id = :doc_id"),
            {"ver_id": ver_id, "doc_id": doc_id},
        )


def downgrade() -> None:
    op.execute("DELETE FROM document_versions")
    op.execute("DELETE FROM documents")
    op.execute("DELETE FROM investigations")
