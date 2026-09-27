"""Sign-in throttling, author deletion, and anonymous notifications

Three things:

* ``auth_throttle`` counts failed sign-ins and code requests, so an account
  can be protected from password guessing without locking out a campus.
* ``deleted_at`` on posts and replies records that the author took it down,
  which a moderator's "unhide" must not undo.
* Notifications about an anonymous reply, or from an anonymous asker, were
  written with the writer's nickname in them. The rows already written are
  scrubbed here; the code no longer writes the name.

Revision ID: a9d3e7c15b20
Revises: f2a8c6d41e93
Create Date: 2026-09-27 12:00:00+00:00
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = 'a9d3e7c15b20'
down_revision: str | None = 'f2a8c6d41e93'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'auth_throttle',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('kind', sa.String(length=32), nullable=False),
        sa.Column('key', sa.String(length=320), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                  nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_auth_throttle_lookup', 'auth_throttle', ['kind', 'key', 'created_at'])
    op.create_index('ix_auth_throttle_created_at', 'auth_throttle', ['created_at'])

    op.add_column('community_posts',
                  sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('community_answers',
                  sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))

    op.execute(
        "UPDATE notifications AS n SET actor_nickname = NULL "
        "FROM community_answers AS a "
        "WHERE n.kind = 'answer' AND n.answer_id = a.id AND a.is_anonymous"
    )
    op.execute(
        "UPDATE notifications AS n SET actor_nickname = NULL "
        "FROM community_posts AS p "
        "WHERE n.kind = 'accepted' AND n.post_id = p.id "
        "AND (p.is_anonymous OR n.actor_nickname IS DISTINCT FROM "
        "(SELECT u.nickname FROM users AS u WHERE u.id = p.author_id))"
    )


def downgrade() -> None:
    op.drop_column('community_answers', 'deleted_at')
    op.drop_column('community_posts', 'deleted_at')
    op.drop_index('ix_auth_throttle_created_at', table_name='auth_throttle')
    op.drop_index('ix_auth_throttle_lookup', table_name='auth_throttle')
    op.drop_table('auth_throttle')
