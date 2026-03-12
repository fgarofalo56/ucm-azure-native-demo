"""Add RBAC tables: app_users, roles, permissions, user_roles, role_permissions.

Revision ID: 002_rbac
Revises: 001_initial
Create Date: 2026-03-12

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_rbac"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # app_users
    op.create_table(
        "app_users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("entra_oid", sa.String(255), nullable=False, unique=True),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("last_login_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_app_users_entra_oid", "app_users", ["entra_oid"])

    # roles
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default=sa.text("0")),
    )

    # permissions
    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("resource", sa.String(100), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
    )
    op.create_index(
        "ix_permissions_resource_action", "permissions", ["resource", "action"], unique=True
    )

    # user_roles
    op.create_table(
        "user_roles",
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("app_users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "role_id",
            sa.Integer,
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    # role_permissions
    op.create_table(
        "role_permissions",
        sa.Column(
            "role_id",
            sa.Integer,
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "permission_id",
            sa.Integer,
            sa.ForeignKey("permissions.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    # Composite index for document queries
    op.create_index(
        "ix_documents_inv_deleted", "documents", ["investigation_id", "is_deleted"]
    )

    # Seed roles
    roles_table = sa.table(
        "roles",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("display_name", sa.String),
        sa.column("description", sa.String),
        sa.column("is_system", sa.Boolean),
    )
    op.bulk_insert(
        roles_table,
        [
            {"id": 1, "name": "admin", "display_name": "Administrator", "description": "Full system access", "is_system": True},
            {"id": 2, "name": "case_manager", "display_name": "Case Manager", "description": "Manage investigations and documents", "is_system": True},
            {"id": 3, "name": "document_manager", "display_name": "Document Manager", "description": "Upload, manage, and merge documents", "is_system": True},
            {"id": 4, "name": "reviewer", "display_name": "Reviewer", "description": "Read-only access with audit visibility", "is_system": True},
            {"id": 5, "name": "viewer", "display_name": "Viewer", "description": "Basic read-only access", "is_system": True},
        ],
    )

    # Seed permissions
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
            {"id": 1, "resource": "investigations", "action": "create", "description": "Create new investigations"},
            {"id": 2, "resource": "investigations", "action": "read", "description": "View investigations"},
            {"id": 3, "resource": "investigations", "action": "update", "description": "Update investigation details"},
            {"id": 4, "resource": "investigations", "action": "delete", "description": "Delete investigations"},
            {"id": 5, "resource": "documents", "action": "create", "description": "Upload documents"},
            {"id": 6, "resource": "documents", "action": "read", "description": "View and download documents"},
            {"id": 7, "resource": "documents", "action": "download", "description": "Download document files"},
            {"id": 8, "resource": "documents", "action": "delete", "description": "Delete documents"},
            {"id": 9, "resource": "documents", "action": "merge", "description": "Merge PDF documents"},
            {"id": 10, "resource": "audit", "action": "read", "description": "View audit logs"},
            {"id": 11, "resource": "users", "action": "read", "description": "View user list"},
            {"id": 12, "resource": "users", "action": "manage", "description": "Manage user accounts"},
            {"id": 13, "resource": "roles", "action": "manage", "description": "Manage role assignments"},
        ],
    )

    # Seed role-permission mappings
    rp_table = sa.table(
        "role_permissions",
        sa.column("role_id", sa.Integer),
        sa.column("permission_id", sa.Integer),
    )
    op.bulk_insert(
        rp_table,
        [
            # admin = all 13 permissions
            *[{"role_id": 1, "permission_id": pid} for pid in range(1, 14)],
            # case_manager: investigations.* + documents.create/read/download
            {"role_id": 2, "permission_id": 1},
            {"role_id": 2, "permission_id": 2},
            {"role_id": 2, "permission_id": 3},
            {"role_id": 2, "permission_id": 4},
            {"role_id": 2, "permission_id": 5},
            {"role_id": 2, "permission_id": 6},
            {"role_id": 2, "permission_id": 7},
            # document_manager: documents.* + investigations.read
            {"role_id": 3, "permission_id": 2},
            {"role_id": 3, "permission_id": 5},
            {"role_id": 3, "permission_id": 6},
            {"role_id": 3, "permission_id": 7},
            {"role_id": 3, "permission_id": 8},
            {"role_id": 3, "permission_id": 9},
            # reviewer: investigations.read + documents.read/download + audit.read
            {"role_id": 4, "permission_id": 2},
            {"role_id": 4, "permission_id": 6},
            {"role_id": 4, "permission_id": 10},
            # viewer: investigations.read + documents.read
            {"role_id": 5, "permission_id": 2},
            {"role_id": 5, "permission_id": 6},
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_documents_inv_deleted", table_name="documents")
    op.drop_table("role_permissions")
    op.drop_table("user_roles")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_table("app_users")
