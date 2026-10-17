"""Course codes without spaces

Revision ID: b8e4d2a6c917
Revises: e7b3c5a19f42
Create Date: 2026-10-17 15:30:00.000000+00:00
"""
from collections.abc import Sequence

from alembic import op

revision: str = "b8e4d2a6c917"
down_revision: str | None = "e7b3c5a19f42"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # M6011 is published as "M6011 M6019", and before the parser kept only
    # the first code the pair was stored as the course code. /courses/M6011
    # M6019 is not a link anyone can follow. Where the year already has a
    # row under the first code, the paired row is a duplicate and goes (its
    # requirement groups cascade); otherwise it takes the first code.
    op.execute("""
        DELETE FROM courses AS paired
        USING courses AS single
        WHERE paired.course_code LIKE '% %'
          AND single.academic_year = paired.academic_year
          AND single.course_code = split_part(paired.course_code, ' ', 1)
    """)
    op.execute("""
        UPDATE courses SET course_code = split_part(course_code, ' ', 1)
        WHERE course_code LIKE '% %'
    """)
    # Translations are stored by code. A row under the paired code is moved
    # to the first code unless one is already there.
    op.execute("""
        DELETE FROM content_translations AS paired
        USING content_translations AS single
        WHERE paired.target_type = 'course'
          AND paired.target_key LIKE '% %'
          AND single.target_type = 'course'
          AND single.target_key = split_part(paired.target_key, ' ', 1)
          AND single.locale = paired.locale
          AND single.field = paired.field
          AND single.provenance = paired.provenance
    """)
    op.execute("""
        UPDATE content_translations SET target_key = split_part(target_key, ' ', 1)
        WHERE target_type = 'course' AND target_key LIKE '% %'
    """)


def downgrade() -> None:
    # Nothing to restore: the paired code was never a usable identifier.
    pass
