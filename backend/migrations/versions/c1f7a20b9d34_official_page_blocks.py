"""Structured blocks for official pages

Revision ID: c1f7a20b9d34
Revises: be5d8c40c314
Create Date: 2026-08-23 06:12:04.883021+00:00

The column starts empty on every existing row and stays that way until the next
crawl. That is deliberate rather than a backfill: the blocks can only come from
the source HTML, which we do not keep, so there is nothing on this side to
convert. ``EXTRACTOR_VERSION`` in app/knowledge/cleaner.py is what makes the
next crawl treat every page as changed and fill them in.
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = 'c1f7a20b9d34'
down_revision: str | None = 'be5d8c40c314'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    for table in ("official_pages", "official_page_versions"):
        op.add_column(
            table,
            sa.Column(
                "blocks",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default=sa.text("'[]'::jsonb"),
            ),
        )
        # The default exists so the column can be NOT NULL on rows that predate
        # it; new writes always supply a value.
        op.alter_column(table, "blocks", server_default=None)


def downgrade() -> None:
    op.drop_column("official_page_versions", "blocks")
    op.drop_column("official_pages", "blocks")
