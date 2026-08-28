"""requisite groups nest

FIT2099 asks for one of six programming units *or* an engineering pair. The
parser flattened that into sibling groups, which reads as "all of the above",
and the planner told a student who had passed FIT1045 that they still needed
two ENG units they will never take.

The nesting is the rule, so the groups now form a tree. Existing rows all
become roots, which is the shape they were already being read as; the values
are only correct again after units are re-crawled.

Revision ID: 644c8a8e6772
Revises: a1c4e9f70b32
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = '644c8a8e6772'
down_revision: str | None = 'a1c4e9f70b32'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

FK = "fk_unit_requisite_groups_parent"


def upgrade() -> None:
    op.add_column(
        "unit_requisite_groups", sa.Column("parent_id", sa.Integer(), nullable=True)
    )
    # A server default, because the table already has rows and the column is
    # NOT NULL. Existing groups keep the order they were written in.
    op.add_column(
        "unit_requisite_groups",
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index(
        op.f("ix_unit_requisite_groups_parent_id"),
        "unit_requisite_groups",
        ["parent_id"],
    )
    op.create_foreign_key(
        FK, "unit_requisite_groups", "unit_requisite_groups",
        ["parent_id"], ["id"], ondelete="CASCADE",
    )


def downgrade() -> None:
    # Nested groups would be orphaned from a parent that no longer exists, so
    # they go with it rather than being promoted into rules of their own.
    op.execute("DELETE FROM unit_requisite_groups WHERE parent_id IS NOT NULL")
    op.drop_constraint(FK, "unit_requisite_groups", type_="foreignkey")
    op.drop_index(op.f("ix_unit_requisite_groups_parent_id"), table_name="unit_requisite_groups")
    op.drop_column("unit_requisite_groups", "order_index")
    op.drop_column("unit_requisite_groups", "parent_id")
