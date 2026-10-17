"""Store the SCA band as a bare number

Revision ID: a3d7e2b95c41
Revises: c4f1a7e93d28
Create Date: 2026-10-17 12:30:00.000000+00:00
"""
from collections.abc import Sequence

from alembic import op

revision: str = "a3d7e2b95c41"
down_revision: str | None = "c4f1a7e93d28"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # The first crawl after c4f1a7e93d28 stored the live label, "SCA Band 2",
    # and the page puts its own "Band" in front of it. The parser now strips
    # both words; this cleans the rows written before that. Units crawled
    # again later get the same value from the parser, so nothing is lost if
    # the next crawl rewrites them.
    op.execute(
        r"""
        UPDATE units
        SET sca_band = NULLIF(btrim(regexp_replace(sca_band, '^(sca\s+)?band\s*', '', 'i')), '')
        WHERE sca_band ~* '^(sca\s+)?band'
        """
    )


def downgrade() -> None:
    # Nothing to undo: the bare number is what the column was meant to hold.
    pass
