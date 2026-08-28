"""cricos codes can be a list

F2003 publishes "075112E (Bachelor of Fine Art), 085529G (Bachelor of Art
History and Curating)" - 78 characters into a column of 32, and it stopped the
course crawl at page 87.

This was measured rather than guessed the second time: every one of the 503
courses and 411 areas of study was parsed and every short string field
measured. Only this column was still wrong. The longest values found were
container titles at 123 and course titles at 105, both inside String(300).

Revision ID: a1c4e9f70b32
Revises: 987ff77ff67c
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = 'a1c4e9f70b32'
down_revision: str | None = '987ff77ff67c'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "courses",
        "cricos_code",
        existing_type=sa.String(length=32),
        type_=sa.String(length=200),
        existing_nullable=True,
    )


def downgrade() -> None:
    # Narrowing would cut a two-award code in half, which reads as a valid
    # single code and is worse than no code at all.
    op.execute("UPDATE courses SET cricos_code = NULL WHERE length(cricos_code) > 32")
    op.alter_column(
        "courses",
        "cricos_code",
        existing_type=sa.String(length=200),
        type_=sa.String(length=32),
        existing_nullable=True,
    )
