"""Search terms counted by day

Revision ID: b7e4d2c91a58
Revises: a3d9e6f1c254
Create Date: 2026-10-26 04:30:00.000000+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b7e4d2c91a58"
down_revision: str | None = "a3d9e6f1c254"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # A new table and nothing else, so it is safe to run while the site is up.
    # It holds a term, a day and a count: nothing about who searched.
    op.create_table(
        "search_terms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("term", sa.String(length=80), nullable=False),
        sa.Column("label", sa.String(length=80), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("hits", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("term", "day", name="uq_search_terms_term_day"),
    )
    op.create_index(op.f("ix_search_terms_term"), "search_terms", ["term"])
    op.create_index(op.f("ix_search_terms_day"), "search_terms", ["day"])


def downgrade() -> None:
    op.drop_index(op.f("ix_search_terms_day"), table_name="search_terms")
    op.drop_index(op.f("ix_search_terms_term"), table_name="search_terms")
    op.drop_table("search_terms")
