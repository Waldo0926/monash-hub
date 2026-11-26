"""Preserve course, area and requirement reference links.

Revision ID: d7a1e3b5c902
Revises: c8e2f4a6b913
"""
from alembic import op
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

revision = "d7a1e3b5c902"
down_revision = "c8e2f4a6b913"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table in ("courses", "areas_of_study", "curriculum_containers"):
        op.add_column(table, Column("reference_links", JSONB(), nullable=True))


def downgrade() -> None:
    for table in ("curriculum_containers", "areas_of_study", "courses"):
        op.drop_column(table, "reference_links")
