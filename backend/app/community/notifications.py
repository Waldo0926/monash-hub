"""Writing and reading notifications.

A notification is a flat row: it copies the actor's nickname, the post title and
a short excerpt at the moment it is created. That costs a little duplication and
buys two things - the notification list is a single indexed read with no joins,
and it still reads correctly after the post is edited, renamed or hidden.
"""
from __future__ import annotations

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.community import CommunityAnswer, CommunityPost
from app.models.user import Notification, User

EXCERPT_CHARS = 160


def _excerpt(text: str) -> str:
    flat = " ".join((text or "").split())
    return flat[:EXCERPT_CHARS] + ("…" if len(flat) > EXCERPT_CHARS else "")


def notify_answer(
    db: Session, *, post: CommunityPost, answer: CommunityAnswer, actor: User
) -> None:
    """Tell the asker that someone answered. Answering your own post is silent."""
    if post.author_id == actor.id:
        return
    db.add(
        Notification(
            user_id=post.author_id,
            kind="answer",
            actor_nickname=actor.nickname,
            post_id=post.id,
            post_title=post.title,
            answer_id=answer.id,
            excerpt=_excerpt(answer.body),
        )
    )


def notify_accepted(
    db: Session, *, post: CommunityPost, answer: CommunityAnswer, actor: User
) -> None:
    """Tell the answerer their answer was marked helpful."""
    if answer.author_id == actor.id:
        return
    db.add(
        Notification(
            user_id=answer.author_id,
            kind="accepted",
            actor_nickname=actor.nickname,
            post_id=post.id,
            post_title=post.title,
            answer_id=answer.id,
            excerpt=_excerpt(answer.body),
        )
    )


def unread_count(db: Session, user_id: int) -> int:
    return int(
        db.scalar(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id, Notification.is_read.is_(False)
            )
        )
        or 0
    )


def recent(db: Session, user_id: int, *, limit: int = 20, offset: int = 0) -> list[Notification]:
    return list(
        db.scalars(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc(), Notification.id.desc())
            .limit(limit)
            .offset(offset)
        )
    )


def mark_read(db: Session, user_id: int, notification_ids: list[int] | None) -> int:
    """Mark some or all of a user's notifications read. Returns the row count."""
    statement = (
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        .values(is_read=True)
    )
    if notification_ids:
        statement = statement.where(Notification.id.in_(notification_ids))
    result = db.execute(statement)
    db.commit()
    return result.rowcount or 0
