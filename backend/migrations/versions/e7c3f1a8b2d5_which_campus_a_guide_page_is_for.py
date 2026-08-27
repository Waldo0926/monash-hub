"""Which campus a guide page is for

Revision ID: e7c3f1a8b2d5
Revises: d4a91c73e502
Create Date: 2026-08-27 10:00:00.000000+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e7c3f1a8b2d5"
down_revision: str | None = "d4a91c73e502"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Every page in the table today was crawled from monash.edu, the Australian
    # student site, so that is the backfill. The default stays on the column:
    # the seed list states it for each page, and a page that arrives without one
    # is far likelier to be another monash.edu page than a Malaysian one.
    op.add_column(
        "official_pages",
        sa.Column(
            "applies_to",
            sa.String(length=16),
            nullable=False,
            server_default="australia",
        ),
    )
    op.create_index(
        op.f("ix_official_pages_applies_to"), "official_pages", ["applies_to"]
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_official_pages_applies_to"), table_name="official_pages")
    op.drop_column("official_pages", "applies_to")
