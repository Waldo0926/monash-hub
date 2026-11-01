"""Stored Chinese translations say 禁修课程, not 互斥课程

Revision ID: c8e2f4a6b913
Revises: b7e4d2c91a58
Create Date: 2026-11-01 18:00:00.000000+00:00
"""
from collections.abc import Sequence

from alembic import op

revision: str = "c8e2f4a6b913"
down_revision: str | None = "b7e4d2c91a58"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # The glossary rendered "prohibition" as 互斥课程, which reads as mutual. A
    # prohibition runs one way (ETW1001 lists ETW2001, not the reverse), so the
    # glossary now says 禁修课程. Rows translated before the change keep the old
    # word until they are next re-translated; this swaps it in place. The
    # source hash is untouched: the English did not change, only our term.
    op.execute(
        """
        UPDATE content_translations
        SET text = replace(text, '互斥课程', '禁修课程')
        WHERE locale LIKE 'zh%' AND text LIKE '%互斥课程%'
        """
    )
    # String maps are JSONB; jsonb's text form keeps Chinese unescaped.
    op.execute(
        """
        UPDATE content_translations
        SET data = replace(data::text, '互斥课程', '禁修课程')::jsonb
        WHERE locale LIKE 'zh%' AND data::text LIKE '%互斥课程%'
        """
    )


def downgrade() -> None:
    # Not reversed: 禁修课程 may also have come from translations made after the
    # glossary changed, and turning those into 互斥课程 would bring the error back.
    pass
