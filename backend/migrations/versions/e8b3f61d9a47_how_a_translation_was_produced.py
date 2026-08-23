"""How a translation was produced

Revision ID: e8b3f61d9a47
Revises: d4a91c73e502
Create Date: 2026-08-23 11:36:21.909814+00:00

Every row that exists when this runs was written by a person, so 'human' is
both the backfill and the right answer for it. The default is dropped again
straight away: a row inserted without saying how it was produced should fail
loudly rather than quietly claim to be hand-written.
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = 'e8b3f61d9a47'
down_revision: str | None = 'd4a91c73e502'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "content_translations",
        sa.Column(
            "method",
            sa.String(length=24),
            nullable=False,
            server_default=sa.text("'human'"),
        ),
    )
    op.alter_column("content_translations", "method", server_default=None)


def downgrade() -> None:
    op.drop_column("content_translations", "method")
