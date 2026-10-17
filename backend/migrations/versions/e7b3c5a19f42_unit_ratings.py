"""Unit ratings

Revision ID: e7b3c5a19f42
Revises: a3d7e2b95c41
Create Date: 2026-10-17 12:40:00.000000+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e7b3c5a19f42"
down_revision: str | None = "a3d7e2b95c41"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # A new table and nothing else, so it is safe to run while the site is up.
    # unit_code is a plain column, not a key into units, because unit rows are
    # replaced every Handbook year and a rating has to outlive that.
    op.create_table('unit_reviews',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('unit_code', sa.String(length=16), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('guest_key', sa.String(length=64), nullable=True),
    sa.Column('overall', sa.SmallInteger(), nullable=False),
    sa.Column('teaching', sa.SmallInteger(), nullable=True),
    sa.Column('content', sa.SmallInteger(), nullable=True),
    sa.Column('assessment', sa.SmallInteger(), nullable=True),
    sa.Column('difficulty', sa.SmallInteger(), nullable=True),
    sa.Column('workload', sa.SmallInteger(), nullable=True),
    sa.Column('body', sa.Text(), nullable=True),
    sa.Column('taken_year', sa.Integer(), nullable=True),
    sa.Column('taken_period', sa.String(length=120), nullable=True),
    sa.Column('campus', sa.String(length=64), nullable=True),
    sa.Column('is_hidden', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('assessment IS NULL OR assessment BETWEEN 1 AND 5', name='ck_unit_review_assessment'),
    sa.CheckConstraint('author_id IS NOT NULL OR guest_key IS NOT NULL', name='ck_unit_review_owner'),
    sa.CheckConstraint('content IS NULL OR content BETWEEN 1 AND 5', name='ck_unit_review_content'),
    sa.CheckConstraint('difficulty IS NULL OR difficulty BETWEEN 1 AND 5', name='ck_unit_review_difficulty'),
    sa.CheckConstraint('overall BETWEEN 1 AND 5', name='ck_unit_review_overall'),
    sa.CheckConstraint('teaching IS NULL OR teaching BETWEEN 1 AND 5', name='ck_unit_review_teaching'),
    sa.CheckConstraint('workload IS NULL OR workload BETWEEN 1 AND 5', name='ck_unit_review_workload'),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('author_id', 'unit_code', name='uq_unit_review_once'),
    sa.UniqueConstraint('guest_key', 'unit_code', name='uq_unit_review_guest_once')
    )
    op.create_index(op.f('ix_unit_reviews_author_id'), 'unit_reviews', ['author_id'], unique=False)
    op.create_index('ix_unit_reviews_unit_feed', 'unit_reviews', ['unit_code', 'is_hidden', 'updated_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_unit_reviews_unit_feed', table_name='unit_reviews')
    op.drop_index(op.f('ix_unit_reviews_author_id'), table_name='unit_reviews')
    op.drop_table('unit_reviews')
