"""Notification endpoints.

Polled by the header badge and rendered on the home page, so the unread count
has to be cheap: it is one indexed count on ``(user_id, is_read, created_at)``.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.community import notifications
from app.core.db import get_db
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["notifications"])


class MarkReadRequest(BaseModel):
    ids: list[int] | None = None


def _brief(row) -> dict:
    return {
        "id": row.id,
        "kind": row.kind,
        "actor": row.actor_nickname,
        "post_id": row.post_id,
        "post_title": row.post_title,
        "answer_id": row.answer_id,
        "excerpt": row.excerpt,
        "is_read": row.is_read,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


@router.get("")
def list_notifications(
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> dict:
    rows = notifications.recent(db, user.id, limit=limit, offset=offset)
    return {
        "unread": notifications.unread_count(db, user.id),
        "limit": limit,
        "offset": offset,
        "results": [_brief(row) for row in rows],
    }


@router.get("/unread-count")
def get_unread_count(db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    return {"unread": notifications.unread_count(db, user.id)}


@router.post("/read")
def mark_read(
    payload: MarkReadRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> dict:
    """Mark the listed notifications read, or all of them when ``ids`` is absent."""
    updated = notifications.mark_read(db, user.id, payload.ids)
    return {"marked": updated, "unread": notifications.unread_count(db, user.id)}
