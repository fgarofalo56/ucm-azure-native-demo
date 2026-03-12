"""Initial schema - investigations, documents, audit_log, migration_status.

Revision ID: 001_initial
Revises: None
Create Date: 2026-03-10

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # investigations
    op.create_table(
        "investigations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("record_id", sa.String(50), nullable=False, unique=True),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("created_by", sa.String(255), nullable=False),
        sa.Column("created_by_name", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_investigations_record_id", "investigations", ["record_id"])
    op.create_index("ix_investigations_status", "investigations", ["status"])
    op.create_index("ix_investigations_created_at", "investigations", ["created_at"])

    # documents
    op.create_table(
        "documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "investigation_id",
            sa.String(36),
            sa.ForeignKey("investigations.id"),
            nullable=False,
        ),
        sa.Column("file_id", sa.String(100), nullable=False, unique=True),
        sa.Column("original_filename", sa.String(500), nullable=False),
        sa.Column("content_type", sa.String(255), nullable=True),
        sa.Column("file_size_bytes", sa.BigInteger, nullable=False),
        sa.Column("blob_path", sa.String(1000), nullable=False),
        sa.Column("pdf_path", sa.String(1000), nullable=True),
        sa.Column(
            "pdf_conversion_status",
            sa.String(50),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("pdf_conversion_error", sa.Text, nullable=True),
        sa.Column("pdf_converted_at", sa.DateTime, nullable=True),
        sa.Column("blob_version_id", sa.String(255), nullable=True),
        sa.Column("checksum_sha256", sa.String(64), nullable=False),
        sa.Column("uploaded_by", sa.String(255), nullable=False),
        sa.Column("uploaded_by_name", sa.String(255), nullable=True),
        sa.Column("uploaded_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default=sa.text("0")),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("deleted_by", sa.String(255), nullable=True),
    )
    op.create_index("ix_documents_investigation_id", "documents", ["investigation_id"])
    op.create_index("ix_documents_file_id", "documents", ["file_id"])
    op.create_index("ix_documents_pdf_status", "documents", ["pdf_conversion_status"])
    op.create_index("ix_documents_uploaded_at", "documents", ["uploaded_at"])

    # audit_log
    op.create_table(
        "audit_log",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("event_timestamp", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("user_principal_name", sa.String(255), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("resource_type", sa.String(100), nullable=True),
        sa.Column("resource_id", sa.String(255), nullable=True),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("result", sa.String(50), nullable=False),
        sa.Column("details", sa.Text, nullable=True),
        sa.Column("correlation_id", sa.String(255), nullable=True),
        sa.Column("session_id", sa.String(255), nullable=True),
    )
    op.create_index("ix_audit_timestamp", "audit_log", ["event_timestamp"])
    op.create_index("ix_audit_user_id", "audit_log", ["user_id"])
    op.create_index("ix_audit_resource_id", "audit_log", ["resource_id"])
    op.create_index("ix_audit_event_type", "audit_log", ["event_type"])
    op.create_index("ix_audit_correlation_id", "audit_log", ["correlation_id"])

    # migration_status
    op.create_table(
        "migration_status",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("ucm_document_id", sa.String(255), nullable=False),
        sa.Column("ucm_path", sa.String(1000), nullable=True),
        sa.Column("azure_blob_path", sa.String(1000), nullable=True),
        sa.Column(
            "azure_document_id",
            sa.String(36),
            sa.ForeignKey("documents.id"),
            nullable=True,
        ),
        sa.Column(
            "migration_status",
            sa.String(50),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("source_checksum", sa.String(64), nullable=True),
        sa.Column("target_checksum", sa.String(64), nullable=True),
        sa.Column("checksum_match", sa.Boolean, nullable=True),
        sa.Column("file_size_bytes", sa.BigInteger, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("migrated_at", sa.DateTime, nullable=True),
        sa.Column("retry_count", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("batch_id", sa.String(100), nullable=True),
    )
    op.create_index("ix_migration_status", "migration_status", ["migration_status"])
    op.create_index("ix_migration_ucm_id", "migration_status", ["ucm_document_id"])
    op.create_index("ix_migration_batch", "migration_status", ["batch_id"])


def downgrade() -> None:
    op.drop_table("migration_status")
    op.drop_table("audit_log")
    op.drop_table("documents")
    op.drop_table("investigations")
