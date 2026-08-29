"""Your own account: what it says about you, and what you have written.

Everything here is about the signed-in user and nobody else. There is no
endpoint that takes a user id, because the moment one exists somebody can
enumerate the community's real names and email addresses, and a student forum
where that is possible is a worse product than one without profiles at all.

The public view of a person is still just their nickname on a post. What this
adds is the private view: your own picture, your own bio, and the list of what
you have written - which the site could not show you before, so a question you
asked last month was findable only by scrolling the category you asked it in.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import current_user
from app.api.serializers import post_brief
from app.core import avatars
from app.core.db import get_db
from app.models.community import CommunityAnswer, CommunityBookmark, CommunityPost, PostTag
from app.models.user import User

log = logging.getLogger(__name__)

router = APIRouter(prefix="/profile", tags=["profile"])

BIO_MAX = 280


class ProfileUpdate(BaseModel):
    nickname: str | None = Field(default=None, max_length=48)
    bio: str | None = Field(default=None, max_length=BIO_MAX)


def _counts(db: Session, user: User) -> dict:
    return {
        "posts": int(db.scalar(
            select(func.count(CommunityPost.id)).where(CommunityPost.author_id == user.id)
        ) or 0),
        "answers": int(db.scalar(
            select(func.count(CommunityAnswer.id)).where(CommunityAnswer.author_id == user.id)
        ) or 0),
        "bookmarks": int(db.scalar(
            select(func.count(CommunityBookmark.id)).where(CommunityBookmark.user_id == user.id)
        ) or 0),
    }


def _profile(db: Session, user: User) -> dict:
    return {
        "id": user.id,
        "nickname": user.nickname,
        "email": user.email,
        "is_admin": user.is_admin,
        "bio": user.bio,
        "avatar_url": avatars.url_for(user.avatar_file),
        "joined_at": user.created_at.isoformat() if user.created_at else None,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "counts": _counts(db, user),
    }


@router.get("")
def get_profile(user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    return _profile(db, user)


@router.patch("")
def update_profile(
    payload: ProfileUpdate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Change the nickname or the bio.

    The nickname is validated with the same rules registration uses, because a
    name that could not be registered should not be reachable by editing either.
    """
    from app.api.v1.auth import _nickname_problem  # circular at module scope

    if payload.nickname is not None:
        nickname = payload.nickname.strip()
        if nickname != user.nickname:
            problem = _nickname_problem(nickname)
            if problem:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, problem)
            taken = db.scalar(
                select(User).where(
                    func.lower(User.nickname) == nickname.lower(), User.id != user.id
                )
            )
            if taken is not None:
                raise HTTPException(status.HTTP_409_CONFLICT, "That nickname is taken.")
            user.nickname = nickname

    if payload.bio is not None:
        # An empty bio is a deliberate "remove it", not a missing field.
        user.bio = payload.bio.strip() or None

    db.commit()
    db.refresh(user)
    return _profile(db, user)


@router.post("/avatar")
def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Replace the profile picture.

    The bytes are decoded and re-encoded rather than stored as given - see
    app/core/avatars.py for why that is not optional.
    """
    data = file.file.read(avatars.MAX_BYTES + 1)
    try:
        name = avatars.store(data, user.id)
    except avatars.AvatarError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    except Exception as exc:  # pragma: no cover - a full disk, a bad mount
        log.exception("could not store an avatar")
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "We could not save that picture just now.",
        ) from exc

    previous = user.avatar_file
    user.avatar_file = name
    db.commit()
    # Only after the new one is committed: a crash between the two leaves an
    # orphan file, which is tidiness. The other order leaves a profile pointing
    # at a file that is gone.
    avatars.remove(previous)
    db.refresh(user)
    return _profile(db, user)


@router.delete("/avatar")
def delete_avatar(
    user: User = Depends(current_user), db: Session = Depends(get_db)
) -> dict:
    previous = user.avatar_file
    user.avatar_file = None
    db.commit()
    avatars.remove(previous)
    db.refresh(user)
    return _profile(db, user)


@router.get("/activity")
def my_activity(
    limit: int = 20,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict:
    """What you have written, and what you saved.

    Hidden posts are included: they are yours, you can see them, and a post that
    vanishes without explanation is worse than one shown as hidden.
    """
    limit = max(1, min(limit, 50))
    loader = selectinload(CommunityPost.post_tags).selectinload(PostTag.tag)

    posts = db.scalars(
        select(CommunityPost)
        .where(CommunityPost.author_id == user.id)
        .options(loader)
        .order_by(CommunityPost.created_at.desc())
        .limit(limit)
    ).all()

    # Grouped rather than DISTINCT: answering the same thread twice must not
    # list it twice, and PostgreSQL will not order a DISTINCT by a column that
    # is not selected. Grouping also gives the sort key the intent wants -
    # when you last answered, not when the thread was created.
    answered_at = (
        select(
            CommunityAnswer.post_id.label("post_id"),
            func.max(CommunityAnswer.created_at).label("answered_at"),
        )
        .where(CommunityAnswer.author_id == user.id)
        .group_by(CommunityAnswer.post_id)
        .subquery()
    )
    answered = db.scalars(
        select(CommunityPost)
        .join(answered_at, answered_at.c.post_id == CommunityPost.id)
        .options(loader)
        .order_by(answered_at.c.answered_at.desc())
        .limit(limit)
    ).all()

    saved = db.scalars(
        select(CommunityPost)
        .join(CommunityBookmark, CommunityBookmark.post_id == CommunityPost.id)
        .where(CommunityBookmark.user_id == user.id, CommunityPost.is_hidden.is_(False))
        .options(loader)
        .order_by(CommunityBookmark.created_at.desc())
        .limit(limit)
    ).all()

    return {
        "posts": [post_brief(p) for p in posts],
        "answered": [post_brief(p) for p in answered],
        "bookmarks": [post_brief(p) for p in saved],
    }
