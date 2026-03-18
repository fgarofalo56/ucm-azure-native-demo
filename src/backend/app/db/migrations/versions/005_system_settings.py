"""Add system_settings table for admin-configurable settings.

Revision ID: 005_settings
Revises: 004_seed_data
Create Date: 2026-03-18

Seeds default settings for PDF engine and malware scanning.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "005_settings"
down_revision: str | None = "004_seed_data"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "system_settings",
        sa.Column("key", sa.String(100), primary_key=True),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_by", sa.String(255), nullable=True),
    )

    settings_table = sa.table(
        "system_settings",
        sa.column("key", sa.String),
        sa.column("value", sa.Text),
        sa.column("description", sa.String),
    )
    op.bulk_insert(
        settings_table,
        [
            {
                "key": "pdf_engine",
                "value": "opensource",
                "description": "PDF conversion engine: 'opensource' (Pillow+fpdf2) or 'aspose' (licensed)",
            },
            {
                "key": "aspose_words_license",
                "value": "",
                "description": "Aspose.Words license key (leave empty for evaluation mode)",
            },
            {
                "key": "aspose_cells_license",
                "value": "",
                "description": "Aspose.Cells license key (leave empty for evaluation mode)",
            },
            {
                "key": "aspose_slides_license",
                "value": "",
                "description": "Aspose.Slides license key (leave empty for evaluation mode)",
            },
            {
                "key": "malware_scanning_enabled",
                "value": "true",
                "description": "Enable two-phase upload with malware scanning via staging container",
            },
            {
                "key": "gotenberg_url",
                "value": "",
                "description": "Gotenberg URL for Office conversion fallback (optional, e.g. http://gotenberg:3000)",
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("system_settings")
