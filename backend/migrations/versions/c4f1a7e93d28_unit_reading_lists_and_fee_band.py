"""Unit reading lists, SCA band and study abroad flag

Revision ID: c4f1a7e93d28
Revises: b6e2d9f40a17
Create Date: 2026-10-17 11:00:00.000000+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c4f1a7e93d28"
down_revision: str | None = "b6e2d9f40a17"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # All three are nullable and filled by the next crawl. Adding them to the
    # parsed record changes every unit's content hash, so that crawl rewrites
    # each unit once; after it, unchanged units are skipped as before.
    op.add_column("units", sa.Column("learning_resources", postgresql.JSONB(), nullable=True))
    op.add_column("units", sa.Column("sca_band", sa.String(length=16), nullable=True))
    op.add_column("units", sa.Column("study_abroad", sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column("units", "study_abroad")
    op.drop_column("units", "sca_band")
    op.drop_column("units", "learning_resources")
