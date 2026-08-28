"""a double degree carries two AQF levels

B6043 publishes "Level 9 - Master's Degree (Coursework) / Level 9 - Master's
Degree (Coursework)" - 79 characters, and the column was 64. Measured across a
sample covering every double-degree prefix, 79 is the longest in 2026; 200
leaves room for a Handbook that concatenates a third.

Revision ID: 987ff77ff67c
Revises: 94dbbe2277d9
Create Date: 2026-08-28 12:22:49.763118+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = '987ff77ff67c'
down_revision: str | None = '94dbbe2277d9'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "courses",
        "aqf_level",
        existing_type=sa.String(length=64),
        type_=sa.String(length=200),
        existing_nullable=True,
    )


def downgrade() -> None:
    # Narrowing would truncate the double degrees this widened for, so the rows
    # that need the width are cleared rather than silently cut in half.
    op.execute("UPDATE courses SET aqf_level = NULL WHERE length(aqf_level) > 64")
    op.alter_column(
        "courses",
        "aqf_level",
        existing_type=sa.String(length=200),
        type_=sa.String(length=64),
        existing_nullable=True,
    )
