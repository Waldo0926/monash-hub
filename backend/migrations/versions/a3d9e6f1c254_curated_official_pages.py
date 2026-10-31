"""Official pages picked by hand

Revision ID: a3d9e6f1c254
Revises: b8e4d2a6c917
Create Date: 2026-10-25 13:30:00.000000+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a3d9e6f1c254"
down_revision: str | None = "b8e4d2a6c917"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # False for every row until the next official crawl registers the seed
    # list, which marks the hand-picked pages.
    op.add_column(
        "official_pages",
        sa.Column("curated", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("official_pages", "curated")
