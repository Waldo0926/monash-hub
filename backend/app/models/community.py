"""Community tables: posts, answers, tags, votes, bookmarks, reports."""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Computed,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class CommunityTag(Base):
    __tablename__ = "community_tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    label: Mapped[str] = mapped_column(String(64))
    kind: Mapped[str] = mapped_column(String(24), default="topic")  # topic | unit | campus


class PostTag(Base):
    __tablename__ = "community_post_tags"
    __table_args__ = (UniqueConstraint("post_id", "tag_id", name="uq_post_tag"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("community_posts.id", ondelete="CASCADE"), index=True)
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("community_tags.id", ondelete="CASCADE"), index=True)

    tag: Mapped[CommunityTag] = relationship()


class CommunityPost(Base):
    __tablename__ = "community_posts"
    __table_args__ = (
        Index("ix_community_posts_search_vector", "search_vector", postgresql_using="gin"),
        # The three orderings the list endpoint offers. Without these, every
        # community page load is a sequential scan plus a sort once the table
        # stops being small.
        Index("ix_community_posts_feed", "is_hidden", "is_pinned", "updated_at"),
        Index("ix_community_posts_category_feed", "category", "is_hidden", "updated_at"),
        Index("ix_community_posts_unit_feed", "unit_code", "is_hidden", "updated_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(300))
    body: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(48), index=True)
    unit_code: Mapped[str | None] = mapped_column(String(16), index=True)

    # Written by the author, never changed afterwards. The author_id stays -
    # a post nobody owns cannot be moderated, edited or answered by its own
    # writer - and the serialiser is what withholds the name.
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False)
    is_solved: Mapped[bool] = mapped_column(Boolean, default=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    answer_count: Mapped[int] = mapped_column(Integer, default=0)
    vote_count: Mapped[int] = mapped_column(Integer, default=0)
    view_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    search_vector: Mapped[str | None] = mapped_column(
        TSVECTOR,
        Computed(
            "setweight(to_tsvector('english', coalesce(title, '') || ' ' || "
            "coalesce(unit_code, '')), 'A') || "
            "setweight(to_tsvector('english', coalesce(body, '')), 'D')",
            persisted=True,
        ),
    )

    author: Mapped["object"] = relationship("User", lazy="joined")
    answers: Mapped[list["CommunityAnswer"]] = relationship(
        primaryjoin=(
            "and_(CommunityPost.id == CommunityAnswer.post_id, "
            "CommunityAnswer.parent_id.is_(None))"
        ),
        back_populates="post", cascade="all, delete-orphan", order_by="CommunityAnswer.id")
    post_tags: Mapped[list[PostTag]] = relationship(cascade="all, delete-orphan", lazy="selectin")


class CommunityAnswer(Base):
    __tablename__ = "community_answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("community_posts.id", ondelete="CASCADE"), index=True)
    # A reply to another reply. One table and one self-reference, because a
    # thread is a thread whether it is two deep or five: a separate "comment"
    # table would need a third for comments on comments.
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("community_answers.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    body: Mapped[str] = mapped_column(Text)
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False)
    is_accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    vote_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    post: Mapped[CommunityPost] = relationship(back_populates="answers")
    author: Mapped["object"] = relationship("User", lazy="joined")
    children: Mapped[list["CommunityAnswer"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
        order_by="CommunityAnswer.created_at",
    )
    parent: Mapped["CommunityAnswer | None"] = relationship(
        back_populates="children", remote_side=[id]
    )


class CommunityVote(Base):
    __tablename__ = "community_votes"
    __table_args__ = (
        UniqueConstraint("user_id", "target_type", "target_id", name="uq_vote_once"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    target_type: Mapped[str] = mapped_column(String(16))  # post | answer
    target_id: Mapped[int] = mapped_column(Integer)
    value: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CommunityBookmark(Base):
    __tablename__ = "community_bookmarks"
    __table_args__ = (UniqueConstraint("user_id", "post_id", name="uq_bookmark_once"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("community_posts.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CommunityReport(Base):
    __tablename__ = "community_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    reporter_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    target_type: Mapped[str] = mapped_column(String(16))
    target_id: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(48))
    detail: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(24), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
