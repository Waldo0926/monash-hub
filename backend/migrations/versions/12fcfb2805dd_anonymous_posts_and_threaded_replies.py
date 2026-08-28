"""anonymous posts and threaded replies

Anonymity is chosen per post and per reply, so it is a column on the row rather
than a setting on the account: the same person asks some questions under their
name and some not. ``author_id`` stays either way - a post nobody owns cannot
be moderated, edited or answered by its own writer - and the serialiser is what
refuses to say the name.

Replies nest through a self-reference on the answers table. One table, because
a thread is a thread whether it is two deep or five; a separate "comments"
table would need a third for comments on comments.

Revision ID: 12fcfb2805dd
Revises: 644c8a8e6772
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = '12fcfb2805dd'
down_revision: str | None = '644c8a8e6772'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

FK = "fk_community_answers_parent"


def upgrade() -> None:
    for table in ("community_posts", "community_answers"):
        op.add_column(
            table,
            sa.Column(
                "is_anonymous", sa.Boolean(), nullable=False, server_default=sa.false()
            ),
        )
    op.add_column(
        "community_answers", sa.Column("parent_id", sa.Integer(), nullable=True)
    )
    op.create_index(
        op.f("ix_community_answers_parent_id"), "community_answers", ["parent_id"]
    )
    op.create_foreign_key(
        FK, "community_answers", "community_answers",
        ["parent_id"], ["id"], ondelete="CASCADE",
    )


def downgrade() -> None:
    # A nested reply has no meaning without the reply it answers, and promoting
    # it to a top-level answer would put a remark about someone's answer
    # directly under the question.
    op.execute("DELETE FROM community_answers WHERE parent_id IS NOT NULL")
    op.drop_constraint(FK, "community_answers", type_="foreignkey")
    op.drop_index(op.f("ix_community_answers_parent_id"), table_name="community_answers")
    op.drop_column("community_answers", "parent_id")
    for table in ("community_answers", "community_posts"):
        op.drop_column(table, "is_anonymous")
