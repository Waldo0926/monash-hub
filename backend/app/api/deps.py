"""Shared FastAPI dependencies."""
from __future__ import annotations

from fastapi import Depends, Header, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import decode_access_token
from app.models.user import User


def current_user_optional(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User | None:
    """Anonymous reading is a product decision, so this never raises."""
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    claims = decode_access_token(authorization.split(" ", 1)[1].strip())
    if claims is None:
        return None
    subject, version = claims
    try:
        user_id = int(subject)
    except ValueError:
        return None
    user = db.scalar(select(User).where(User.id == user_id, User.is_active.is_(True)))
    # A token issued before the last password reset is no longer a session.
    if user is None or user.token_version != version:
        return None
    return user


def current_user(user: User | None = Depends(current_user_optional)) -> User:
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sign in to do that")
    return user


def current_admin(user: User = Depends(current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Moderator access required")
    return user


# The four interface languages. An unknown value is treated as "no translation"
# rather than rejected: a stale bookmark with ?locale=fr should show the page in
# English, not a 422.
LOCALES = ("en", "zh", "ja", "ko")


def requested_locale(locale: str | None = Query(None, pattern="^[A-Za-z-]{0,16}$")) -> str | None:
    """Which language to look translations up in, or ``None`` for the source.

    A query parameter rather than ``Accept-Language``: the language is a thing
    the reader chose in the switcher, it has to be part of the URL for the cache
    and the SSR fetch to agree on it, and a header that varies per browser is a
    poor cache key for a page that is otherwise identical for everyone.
    """
    if not locale:
        return None
    code = locale.strip().lower().split("-")[0]
    return code if code in LOCALES else None
