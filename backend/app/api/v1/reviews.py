"""Student ratings of units: read by anyone, written by anyone.

These are community content. The unit page shows them under their own heading
with the community badge, never inside the Handbook sections, and they are not
machine-translated (see AGENTS.md).

Signing in is optional. A signed-out student's browser sends a random key it
made up (``X-Guest-Key``), and the rating belongs to that key, so the same
browser can change or remove it later. The key is easy to throw away, so
signed-out saves are also limited per network address. Both the key and the
address are stored only as keyed hashes.

Moderation reuses the forum's: a rating can be reported through
``POST /v1/community/reports`` with ``target_type=review``, and a moderator's
hide works the same way it does for a post.
"""
from __future__ import annotations

import hashlib
import hmac
import re

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import current_user_optional
from app.community import ratings
from app.core import throttle
from app.core.config import get_settings
from app.core.db import get_db
from app.models.handbook import Unit
from app.models.review import UnitReview
from app.models.user import User

router = APIRouter(prefix="/reviews", tags=["reviews"])

UNIT_CODE = re.compile(r"^[A-Z]{3,4}\d{4}$")
# A UUID is what the site sends; anything this shape is accepted.
GUEST_KEY = re.compile(r"^[A-Za-z0-9-]{16,64}$")
SORTS = {
    "recent": (UnitReview.updated_at.desc(),),
    "highest": (UnitReview.overall.desc(), UnitReview.updated_at.desc()),
    "lowest": (UnitReview.overall.asc(), UnitReview.updated_at.desc()),
}


class ReviewRequest(BaseModel):
    overall: int = Field(ge=1, le=5)
    teaching: int | None = Field(default=None, ge=1, le=5)
    content: int | None = Field(default=None, ge=1, le=5)
    assessment: int | None = Field(default=None, ge=1, le=5)
    difficulty: int | None = Field(default=None, ge=1, le=5)
    workload: int | None = Field(default=None, ge=1, le=5)
    body: str | None = Field(default=None, max_length=3000)
    taken_year: int | None = Field(default=None, ge=1990, le=2100)
    taken_period: str | None = Field(default=None, max_length=120)
    campus: str | None = Field(default=None, max_length=64)


def _code(raw: str) -> str:
    code = "".join(raw.split()).upper()
    if not UNIT_CODE.match(code):
        raise HTTPException(422, "That is not a unit code (for example FIT2004).")
    return code


def _keyed(value: str) -> str:
    return hmac.new(get_settings().secret_key.encode(), value.encode(), hashlib.sha256).hexdigest()


def guest_hash(raw: str | None) -> str | None:
    """The stored form of a browser's key, or None for a key that is not one.

    Hashed with the server's secret so that a copy of the table is not a list
    of keys anyone could send back to edit other people's ratings.
    """
    raw = (raw or "").strip()
    return _keyed(f"guest:{raw}") if GUEST_KEY.match(raw) else None


def _owned_by(user: User | None, guest: str | None):
    """The condition for "this reader's rating", or None for a reader with neither."""
    if user is not None:
        return UnitReview.author_id == user.id
    if guest is not None:
        return UnitReview.guest_key == guest
    return None


def initials(nickname: str | None) -> str:
    """What other readers see of the author: the first character, as in "W.".

    Less than a forum post shows, on purpose. A review says things about a
    teaching team, and a student should be able to be honest about a unit
    without their nickname sitting next to it.
    """
    first = (nickname or "").strip()[:1]
    return f"{first.upper()}." if first else "?"


def _serialise(review: UnitReview, mine: bool) -> dict:
    return {
        "id": review.id,
        "unit_code": review.unit_code,
        "overall": review.overall,
        "teaching": review.teaching,
        "content": review.content,
        "assessment": review.assessment,
        "difficulty": review.difficulty,
        "workload": review.workload,
        "body": review.body,
        "taken_year": review.taken_year,
        "taken_period": review.taken_period,
        "campus": review.campus,
        # A signed-out rating has no name at all, not even an initial.
        "author": initials(review.author.nickname) if review.author else None,
        "is_guest": review.author_id is None,
        "is_mine": mine,
        "created_at": review.created_at.isoformat() if review.created_at else None,
        "updated_at": review.updated_at.isoformat() if review.updated_at else None,
    }


@router.get("/summary")
def summary(
    codes: str = Query(max_length=2000, description="Comma-separated unit codes"),
    db: Session = Depends(get_db),
) -> dict:
    """Average and count for several units at once, for cards and lists."""
    wanted = list(dict.fromkeys(c.strip().upper() for c in codes.split(",") if c.strip()))[:100]
    return {"results": ratings.summaries(db, wanted)}


@router.get("/units/{code}")
def list_reviews(
    code: str,
    sort: str = Query("recent", pattern="^(recent|highest|lowest)$"),
    # limit=0 is the summary on its own, for the unit page header and its
    # common questions, which need the averages but none of the reviews.
    limit: int = Query(20, ge=0, le=50),
    offset: int = Query(0, ge=0, le=10_000),
    db: Session = Depends(get_db),
    user: User | None = Depends(current_user_optional),
    x_guest_key: str | None = Header(default=None),
) -> dict:
    code = _code(code)
    guest = None if user else guest_hash(x_guest_key)
    owned = _owned_by(user, guest)
    visible = (UnitReview.unit_code == code, UnitReview.is_hidden.is_(False))
    reviews = db.scalars(
        select(UnitReview).where(*visible).order_by(*SORTS[sort]).limit(limit).offset(offset)
    ).all()
    total = db.scalar(select(func.count(UnitReview.id)).where(*visible)) or 0
    mine = None
    if owned is not None:
        # The reader's own rating comes back even when a moderator hid it, so
        # they can see it and edit it rather than wonder where it went.
        own = db.scalar(select(UnitReview).where(UnitReview.unit_code == code, owned))
        if own is not None:
            mine = {**_serialise(own, True), "hidden": own.is_hidden}
    return {
        "unit_code": code,
        "summary": ratings.detail(db, code),
        "total": int(total),
        "sort": sort,
        "results": [_serialise(r, mine is not None and r.id == mine["id"]) for r in reviews],
        "mine": mine,
    }


@router.put("/units/{code}")
def save_review(
    code: str,
    payload: ReviewRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(current_user_optional),
    x_guest_key: str | None = Header(default=None),
) -> dict:
    """Rate a unit, or change your rating. One per student (or browser) per unit."""
    code = _code(code)
    guest = None if user else guest_hash(x_guest_key)
    owned = _owned_by(user, guest)
    if owned is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sign in, or send X-Guest-Key")
    # Any Handbook year will do: a unit that has since been retired is still
    # one people took.
    if db.scalar(select(Unit.id).where(Unit.unit_code == code).limit(1)) is None:
        raise HTTPException(404, f"{code} is not in the Handbook index")

    limits = [(throttle.REVIEWS_PER_AUTHOR, f"user:{user.id}" if user else f"guest:{guest}")]
    if user is None:
        address = _keyed(f"ip:{throttle.client_address(request)}")[:32]
        limits.append((throttle.REVIEWS_PER_ADDRESS, address))
    try:
        for limit, key in limits:
            throttle.check(db, limit, key)
    except throttle.Throttled as limited:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS, "Too many ratings today. Try again later.",
            headers={"Retry-After": str(limited.retry_after_seconds)},
        ) from limited

    fields = payload.model_dump()
    fields["body"] = (fields["body"] or "").strip() or None
    fields["taken_period"] = (fields["taken_period"] or "").strip() or None
    fields["campus"] = (fields["campus"] or "").strip() or None

    review = db.scalar(select(UnitReview).where(UnitReview.unit_code == code, owned))
    created = review is None
    if created:
        review = UnitReview(unit_code=code, author_id=user.id if user else None,
                            guest_key=guest, **fields)
        db.add(review)
    else:
        for name, value in fields.items():
            setattr(review, name, value)
    for limit, key in limits:
        throttle.record(db, limit, key)
    try:
        db.commit()
    except IntegrityError:
        # Two saves at once from the same account: the other one won, and
        # this one becomes an edit of it.
        db.rollback()
        review = db.scalar(select(UnitReview).where(UnitReview.unit_code == code, owned))
        if review is None:
            raise
        for name, value in fields.items():
            setattr(review, name, value)
        db.commit()
        created = False
    db.refresh(review)
    return {**_serialise(review, True), "hidden": review.is_hidden, "created": created}


@router.delete("/units/{code}")
def delete_review(
    code: str,
    db: Session = Depends(get_db),
    user: User | None = Depends(current_user_optional),
    x_guest_key: str | None = Header(default=None),
) -> dict:
    """Take back your rating. It is removed, not hidden: nothing hangs off it."""
    code = _code(code)
    owned = _owned_by(user, None if user else guest_hash(x_guest_key))
    review = None if owned is None else db.scalar(
        select(UnitReview).where(UnitReview.unit_code == code, owned))
    if review is None:
        raise HTTPException(404, "You have not rated this unit")
    db.delete(review)
    db.commit()
    return {"unit_code": code, "deleted": True}
