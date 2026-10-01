"""Official pages behind Monash sign-in

Revision ID: b6e2d9f40a17
Revises: a9d3e7c15b20
Create Date: 2026-10-02 09:00:00.000000+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b6e2d9f40a17"
down_revision: str | None = "a9d3e7c15b20"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # A page Monash shows only after Okta sign-in is listed by title, a
    # description of our own and its link - never its text. See seeds.py.
    op.add_column(
        "official_pages",
        sa.Column("requires_sign_in", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("official_pages", "requires_sign_in")
