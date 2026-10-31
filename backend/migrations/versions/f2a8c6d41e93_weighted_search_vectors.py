"""Weighted search vectors

Every search vector used to be one flat run of words, so a page whose *title*
was "Academic integrity" ranked no higher for "academic integrity" than a page
that used the phrase once in its tenth paragraph. The titles and summaries now
carry more weight than the body, and the search can tell a page that is about a
word from one that merely mentions it.

A generated column's expression cannot be altered in place, so each column is
dropped and added again; PostgreSQL recomputes it for every row as part of the
ADD COLUMN.

Revision ID: f2a8c6d41e93
Revises: b5e21d9c4f08
Create Date: 2026-09-27 10:00:00+00:00
"""
from collections.abc import Sequence

from alembic import op


revision: str = 'f2a8c6d41e93'
down_revision: str | None = 'b5e21d9c4f08'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


WEIGHTED = {
    'official_pages': (
        "setweight(to_tsvector('english', coalesce(title, '')), 'A') || "
        "setweight(to_tsvector('english', coalesce(summary, '')), 'B') || "
        "setweight(to_tsvector('english', coalesce(category, '')), 'C') || "
        "setweight(to_tsvector('english', coalesce(clean_text, '')), 'D')"
    ),
    'faq_entries': (
        "setweight(to_tsvector('english', coalesce(question, '')), 'A') || "
        "setweight(to_tsvector('english', coalesce(answer, '')), 'D')"
    ),
    'units': (
        "setweight(to_tsvector('english', coalesce(unit_code, '') || ' ' || "
        "coalesce(title, '')), 'A') || "
        "setweight(to_tsvector('english', coalesce(areas_of_study, '')), 'B') || "
        "setweight(to_tsvector('english', coalesce(overview, '')), 'D')"
    ),
    'community_posts': (
        "setweight(to_tsvector('english', coalesce(title, '') || ' ' || "
        "coalesce(unit_code, '')), 'A') || "
        "setweight(to_tsvector('english', coalesce(body, '')), 'D')"
    ),
}

FLAT = {
    'official_pages': (
        "to_tsvector('english', coalesce(title, '') || ' ' || "
        "coalesce(summary, '') || ' ' || coalesce(category, '') || ' ' || "
        "coalesce(clean_text, ''))"
    ),
    'faq_entries': (
        "to_tsvector('english', coalesce(question, '') || ' ' || coalesce(answer, ''))"
    ),
    'units': (
        "to_tsvector('english', coalesce(unit_code, '') || ' ' || "
        "coalesce(title, '') || ' ' || coalesce(overview, '') || ' ' || "
        "coalesce(areas_of_study, ''))"
    ),
    'community_posts': (
        "to_tsvector('english', coalesce(title, '') || ' ' || "
        "coalesce(body, '') || ' ' || coalesce(unit_code, ''))"
    ),
}


def _replace(expressions: dict[str, str]) -> None:
    for table, expression in expressions.items():
        op.execute(f"DROP INDEX IF EXISTS ix_{table}_search_vector")
        op.execute(f"ALTER TABLE {table} DROP COLUMN search_vector")
        op.execute(
            f"ALTER TABLE {table} ADD COLUMN search_vector tsvector "
            f"GENERATED ALWAYS AS ({expression}) STORED"
        )
        op.execute(
            f"CREATE INDEX ix_{table}_search_vector ON {table} USING gin (search_vector)"
        )


def upgrade() -> None:
    _replace(WEIGHTED)


def downgrade() -> None:
    _replace(FLAT)
