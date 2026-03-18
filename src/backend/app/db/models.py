"""SQLAlchemy ORM models matching the Azure SQL schema."""

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    Uuid,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# RBAC association tables
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", String(36), ForeignKey("app_users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class AppUser(Base):
    __tablename__ = "app_users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entra_oid: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime)

    roles: Mapped[list["Role"]] = relationship(secondary=user_roles, lazy="selectin")

    __table_args__ = (Index("ix_app_users_entra_oid", "entra_oid"),)


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    permissions: Mapped[list["Permission"]] = relationship(secondary=role_permissions, lazy="selectin")


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    resource: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))

    __table_args__ = (Index("ix_permissions_resource_action", "resource", "action", unique=True),)


class Investigation(Base):
    __tablename__ = "investigations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    record_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    title: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    created_by_name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    documents: Mapped[list["Document"]] = relationship(
        back_populates="investigation", lazy="selectin", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_investigations_record_id", "record_id"),
        Index("ix_investigations_status", "status"),
        Index("ix_investigations_created_at", "created_at"),
    )


class Document(Base):
    """Logical document entity — stable identity across versions.

    Physical binaries live in DocumentVersion. Only the latest version
    is visible to end users; historical versions are admin-only.
    """

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    investigation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False
    )
    document_type: Mapped[str] = mapped_column(String(50), nullable=False, default="other")
    title: Mapped[str | None] = mapped_column(String(500))
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    created_by_name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)
    deleted_by: Mapped[str | None] = mapped_column(String(255))

    # Pointer to the current (latest) version
    current_version_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("document_versions.id", use_alter=True), nullable=True
    )

    investigation: Mapped["Investigation"] = relationship(back_populates="documents")
    versions: Mapped[list["DocumentVersion"]] = relationship(
        back_populates="document",
        foreign_keys="DocumentVersion.document_id",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="DocumentVersion.version_number.desc()",
    )

    __table_args__ = (
        Index("ix_documents_investigation_id", "investigation_id"),
        Index("ix_documents_type", "document_type"),
        Index("ix_documents_deleted", "is_deleted"),
    )

    @property
    def latest_version(self) -> "DocumentVersion | None":
        """Return the latest (is_latest=True) version, or None."""
        for v in self.versions:
            if v.is_latest:
                return v
        return self.versions[0] if self.versions else None


class DocumentVersion(Base):
    """Immutable physical binary — one version of a logical document.

    Contains the actual blob paths, file metadata, and PDF conversion state.
    Once created, a version's binary data is never modified.
    """

    __tablename__ = "document_versions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(255))
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    blob_path_original: Mapped[str] = mapped_column(String(1000), nullable=False)
    blob_path_pdf: Mapped[str | None] = mapped_column(String(1000))
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    is_latest: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # PDF conversion tracking
    pdf_conversion_status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    pdf_conversion_error: Mapped[str | None] = mapped_column(Text)
    pdf_converted_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Malware scan tracking
    scan_status: Mapped[str] = mapped_column(String(50), nullable=False, default="clean")
    scanned_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Upload provenance
    uploaded_by: Mapped[str] = mapped_column(String(255), nullable=False)
    uploaded_by_name: Mapped[str | None] = mapped_column(String(255))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    document: Mapped["Document"] = relationship(
        back_populates="versions", foreign_keys=[document_id]
    )

    __table_args__ = (
        Index("ix_docver_document_id", "document_id"),
        Index("ix_docver_is_latest", "document_id", "is_latest"),
        Index("ix_docver_version", "document_id", "version_number", unique=True),
    )


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    user_principal_name: Mapped[str | None] = mapped_column(String(255))
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String(500))
    resource_type: Mapped[str | None] = mapped_column(String(100))
    resource_id: Mapped[str | None] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    result: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[str | None] = mapped_column(Text)
    correlation_id: Mapped[str | None] = mapped_column(String(255))
    session_id: Mapped[str | None] = mapped_column(String(255))

    __table_args__ = (
        Index("ix_audit_timestamp", "event_timestamp"),
        Index("ix_audit_user_id", "user_id"),
        Index("ix_audit_resource_id", "resource_id"),
        Index("ix_audit_event_type", "event_type"),
        Index("ix_audit_correlation_id", "correlation_id"),
    )


class MigrationStatusRecord(Base):
    __tablename__ = "migration_status"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ucm_document_id: Mapped[str] = mapped_column(String(255), nullable=False)
    ucm_path: Mapped[str | None] = mapped_column(String(1000))
    azure_blob_path: Mapped[str | None] = mapped_column(String(1000))
    azure_document_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("documents.id"))
    migration_status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    source_checksum: Mapped[str | None] = mapped_column(String(64))
    target_checksum: Mapped[str | None] = mapped_column(String(64))
    checksum_match: Mapped[bool | None] = mapped_column(Boolean)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger)
    error_message: Mapped[str | None] = mapped_column(Text)
    migrated_at: Mapped[datetime | None] = mapped_column(DateTime)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    batch_id: Mapped[str | None] = mapped_column(String(100))

    __table_args__ = (
        Index("ix_migration_status", "migration_status"),
        Index("ix_migration_ucm_id", "ucm_document_id"),
        Index("ix_migration_batch", "batch_id"),
    )
