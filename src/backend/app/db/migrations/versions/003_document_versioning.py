"""Add document versioning: document_versions table, refactor documents table.

Revision ID: 003_versioning
Revises: 002_rbac
Create Date: 2026-03-17

This migration:
1. Creates the document_versions table for immutable physical versions
2. Adds document_type, title, current_version_id to documents
3. Removes version-specific columns from documents (moved to document_versions)
4. Adds new permissions for admin version management
5. Grants reviewer role download permission
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "003_versioning"
down_revision: str | None = "002_rbac"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create document_versions table
    op.create_table(
        "document_versions",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("NEWID()")),
        sa.Column("document_id", sa.Uuid(), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("original_filename", sa.String(500), nullable=False),
        sa.Column("mime_type", sa.String(255), nullable=True),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("blob_path_original", sa.String(1000), nullable=False),
        sa.Column("blob_path_pdf", sa.String(1000), nullable=True),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("is_latest", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("pdf_conversion_status", sa.String(50), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("pdf_conversion_error", sa.Text(), nullable=True),
        sa.Column("pdf_converted_at", sa.DateTime(), nullable=True),
        sa.Column("scan_status", sa.String(50), nullable=False, server_default=sa.text("'clean'")),
        sa.Column("scanned_at", sa.DateTime(), nullable=True),
        sa.Column("uploaded_by", sa.String(255), nullable=False),
        sa.Column("uploaded_by_name", sa.String(255), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_docver_document_id", "document_versions", ["document_id"])
    op.create_index("ix_docver_is_latest", "document_versions", ["document_id", "is_latest"])
    op.create_index("ix_docver_version", "document_versions", ["document_id", "version_number"], unique=True)

    # 2. Add new columns to documents table
    op.add_column("documents", sa.Column("document_type", sa.String(50), nullable=True))
    op.add_column("documents", sa.Column("title", sa.String(500), nullable=True))
    op.add_column("documents", sa.Column("current_version_id", sa.Uuid(), nullable=True))
    op.add_column("documents", sa.Column("created_by", sa.String(255), nullable=True))
    op.add_column("documents", sa.Column("created_by_name", sa.String(255), nullable=True))

    # 3. Migrate existing document data into document_versions
    # For each existing document, create a v1 DocumentVersion
    op.execute("""
        INSERT INTO document_versions (
            id, document_id, version_number, original_filename, mime_type,
            file_size_bytes, blob_path_original, blob_path_pdf, checksum,
            is_latest, pdf_conversion_status, pdf_conversion_error, pdf_converted_at,
            scan_status, uploaded_by, uploaded_by_name, uploaded_at
        )
        SELECT
            NEWID(), id, 1, original_filename, content_type,
            file_size_bytes, blob_path, pdf_path, checksum_sha256,
            1, pdf_conversion_status, pdf_conversion_error, pdf_converted_at,
            'clean', uploaded_by, uploaded_by_name, uploaded_at
        FROM documents
    """)

    # 4. Set current_version_id, created_by, document_type on documents from migrated versions
    op.execute("""
        UPDATE documents
        SET current_version_id = dv.id,
            created_by = documents.uploaded_by,
            created_by_name = documents.uploaded_by_name,
            document_type = 'other',
            title = documents.original_filename
        FROM document_versions dv
        WHERE documents.id = dv.document_id AND dv.is_latest = 1
    """)

    # 5. Now make created_by NOT NULL and document_type NOT NULL
    op.alter_column("documents", "created_by", nullable=False, existing_type=sa.String(255))
    op.alter_column("documents", "document_type", nullable=False, existing_type=sa.String(50),
                     server_default=sa.text("'other'"))

    # 6. Drop old columns from documents (now in document_versions)
    op.drop_index("ix_documents_file_id", table_name="documents")
    op.drop_index("ix_documents_pdf_status", table_name="documents")
    op.drop_index("ix_documents_uploaded_at", table_name="documents")
    op.drop_column("documents", "file_id")
    op.drop_column("documents", "original_filename")
    op.drop_column("documents", "content_type")
    op.drop_column("documents", "file_size_bytes")
    op.drop_column("documents", "blob_path")
    op.drop_column("documents", "pdf_path")
    op.drop_column("documents", "pdf_conversion_status")
    op.drop_column("documents", "pdf_conversion_error")
    op.drop_column("documents", "pdf_converted_at")
    op.drop_column("documents", "blob_version_id")
    op.drop_column("documents", "checksum_sha256")
    op.drop_column("documents", "uploaded_by")
    op.drop_column("documents", "uploaded_by_name")
    op.drop_column("documents", "uploaded_at")

    # 7. Add FK constraint for current_version_id (deferred because of circular ref)
    op.create_foreign_key(
        "fk_documents_current_version",
        "documents",
        "document_versions",
        ["current_version_id"],
        ["id"],
    )

    # 8. Add new indexes on documents
    op.create_index("ix_documents_type", "documents", ["document_type"])
    op.create_index("ix_documents_deleted", "documents", ["is_deleted"])

    # 9. Add new permissions for admin version management + document rollback
    permissions_table = sa.table(
        "permissions",
        sa.column("id", sa.Integer),
        sa.column("resource", sa.String),
        sa.column("action", sa.String),
        sa.column("description", sa.String),
    )
    op.bulk_insert(
        permissions_table,
        [
            {"id": 14, "resource": "documents", "action": "rollback", "description": "Roll back document versions"},
            {"id": 15, "resource": "documents", "action": "versions", "description": "View all document versions (admin)"},
        ],
    )

    # Grant rollback + versions permissions to admin role
    rp_table = sa.table(
        "role_permissions",
        sa.column("role_id", sa.Integer),
        sa.column("permission_id", sa.Integer),
    )
    op.bulk_insert(
        rp_table,
        [
            {"role_id": 1, "permission_id": 14},  # admin -> rollback
            {"role_id": 1, "permission_id": 15},  # admin -> versions
            {"role_id": 4, "permission_id": 7},   # reviewer -> download
        ],
    )


def downgrade() -> None:
    # Remove new permissions
    op.execute("DELETE FROM role_permissions WHERE permission_id IN (14, 15)")
    op.execute("DELETE FROM role_permissions WHERE role_id = 4 AND permission_id = 7")
    op.execute("DELETE FROM permissions WHERE id IN (14, 15)")

    # Drop new indexes
    op.drop_index("ix_documents_deleted", table_name="documents")
    op.drop_index("ix_documents_type", table_name="documents")

    # Drop FK
    op.drop_constraint("fk_documents_current_version", "documents", type_="foreignkey")

    # Re-add columns to documents
    op.add_column("documents", sa.Column("file_id", sa.String(100), nullable=True))
    op.add_column("documents", sa.Column("original_filename", sa.String(500), nullable=True))
    op.add_column("documents", sa.Column("content_type", sa.String(255), nullable=True))
    op.add_column("documents", sa.Column("file_size_bytes", sa.BigInteger(), nullable=True))
    op.add_column("documents", sa.Column("blob_path", sa.String(1000), nullable=True))
    op.add_column("documents", sa.Column("pdf_path", sa.String(1000), nullable=True))
    op.add_column("documents", sa.Column("pdf_conversion_status", sa.String(50), nullable=True))
    op.add_column("documents", sa.Column("pdf_conversion_error", sa.Text(), nullable=True))
    op.add_column("documents", sa.Column("pdf_converted_at", sa.DateTime(), nullable=True))
    op.add_column("documents", sa.Column("blob_version_id", sa.String(255), nullable=True))
    op.add_column("documents", sa.Column("checksum_sha256", sa.String(64), nullable=True))
    op.add_column("documents", sa.Column("uploaded_by", sa.String(255), nullable=True))
    op.add_column("documents", sa.Column("uploaded_by_name", sa.String(255), nullable=True))
    op.add_column("documents", sa.Column("uploaded_at", sa.DateTime(), nullable=True))

    # Drop new columns
    op.drop_column("documents", "current_version_id")
    op.drop_column("documents", "title")
    op.drop_column("documents", "document_type")
    op.drop_column("documents", "created_by")
    op.drop_column("documents", "created_by_name")

    # Drop document_versions
    op.drop_index("ix_docver_version", table_name="document_versions")
    op.drop_index("ix_docver_is_latest", table_name="document_versions")
    op.drop_index("ix_docver_document_id", table_name="document_versions")
    op.drop_table("document_versions")
