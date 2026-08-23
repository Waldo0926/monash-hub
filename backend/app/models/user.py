"""Accounts and the email challenges that guard them.

Nickname-first by design: the MVP never asks for a real name or a student ID,
because registration friction is the fastest way to end up with an empty forum.
Email is collected so an account can be recovered, not so anyone is identified
publicly.
"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    nickname: Mapped[str] = mapped_column(String(48), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Bumped whenever the password changes. Tokens carry the version they were
    # issued under, so a password reset signs every existing session out without
    # needing a session table to revoke against.
    token_version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class EmailVerificationCode(Base):
    """One issued email challenge.

    Only a keyed digest of the code is stored, so a database dump does not hand
    anyone a working code. Rows are kept after use: the send-rate and
    failed-attempt limits are counted from this table, and deleting consumed
    rows immediately would erase the evidence those limits depend on.
    """

    __tablename__ = "email_verification_codes"
    __table_args__ = (
        Index("ix_evc_lookup", "email", "purpose", "consumed_at", "expires_at"),
        Index("ix_evc_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), index=True)
    purpose: Mapped[str] = mapped_column(String(24), index=True)  # registration | password_reset
    code_digest: Mapped[str] = mapped_column(String(64))

    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=5)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Notification(Base):
    """Something that happened to a person's own content.

    Written when someone answers your question or marks your answer helpful.
    Denormalised on purpose - it stores the actor's nickname and the post title
    as they were at the time - so the notification list is one indexed read with
    no joins, and still reads correctly after a post is edited or hidden.
    """

    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_user_unread", "user_id", "is_read", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(24))  # answer | accepted

    actor_nickname: Mapped[str | None] = mapped_column(String(48))
    post_id: Mapped[int | None] = mapped_column(Integer, index=True)
    post_title: Mapped[str | None] = mapped_column(String(300))
    answer_id: Mapped[int | None] = mapped_column(Integer)
    excerpt: Mapped[str | None] = mapped_column(String(300))

    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
