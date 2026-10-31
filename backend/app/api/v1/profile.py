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
import secrets

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.api.deps import current_user
from app.api.serializers import post_brief
from app.core import avatars, throttle
from app.core.db import get_db
from app.core.security import hash_password, verify_password
from app.models.community import (
    CommunityAnswer,
    CommunityBookmark,
    CommunityPost,
    CommunityReport,
    PostTag,
)
from app.models.user import AuthThrottle, EmailVerificationCode, Notification, User

log = logging.getLogger(__name__)

router = APIRouter(prefix="/profile", tags=["profile"])

BIO_MAX = 280


class ProfileUpdate(BaseModel):
    nickname: str | None = Field(default=None, max_length=48)
    bio: str | None = Field(default=None, max_length=BIO_MAX)


def _counts(db: Session, user: User) -> dict:
    return {
        "posts": int(db.scalar(
            select(func.count(CommunityPost.id)).where(
                CommunityPost.author_id == user.id, CommunityPost.deleted_at.is_(None))
        ) or 0),
        "answers": int(db.scalar(
            select(func.count(CommunityAnswer.id)).where(
                CommunityAnswer.author_id == user.id, CommunityAnswer.deleted_at.is_(None))
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
    from app.api.v1.auth import (  # circular at module scope
        _nickname_problem,
        _normalise_nickname,
    )

    if payload.nickname is not None:
        # The same folding sign-up applies, or "ｗaldo" could be taken by
        # renaming when it cannot be taken by registering.
        nickname = _normalise_nickname(payload.nickname)
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

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "That nickname is taken.") from exc
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
        .where(CommunityPost.author_id == user.id, CommunityPost.deleted_at.is_(None))
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
        .where(CommunityAnswer.author_id == user.id, CommunityAnswer.deleted_at.is_(None))
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


class DeleteAccountRequest(BaseModel):
    password: str = Field(min_length=1, max_length=128)
    # Off: what you wrote stays, with no name on it, so the threads it answered
    # still make sense. On: it is taken down as if you had deleted each item.
    delete_content: bool = False


@router.delete("")
def delete_account(
    payload: DeleteAccountRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Close your account and remove what identifies you.

    There was no way to leave. The row is kept as an empty tombstone rather
    than removed, because posts and replies point at it; everything that says
    who it was - email, nickname, picture, bio, the nickname copied into other
    people's notifications - is removed, and every session is signed out.
    The email address can be used to register again straight away.
    """
    # The password, because a session left open on a library computer should
    # not be enough to erase somebody's account. Guesses count against the
    # same limit as signing in.
    try:
        throttle.check(db, throttle.SIGNIN_PER_ACCOUNT, user.email)
    except throttle.Throttled as limited:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS, "Too many attempts. Try again later.",
            headers={"Retry-After": str(limited.retry_after_seconds)},
        ) from limited
    if not verify_password(payload.password, user.password_hash):
        throttle.record(db, throttle.SIGNIN_PER_ACCOUNT, user.email)
        db.commit()
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Wrong password")

    old_email, old_nickname = user.email, user.nickname

    if payload.delete_content:
        db.execute(
            update(CommunityPost)
            .where(CommunityPost.author_id == user.id, CommunityPost.deleted_at.is_(None))
            .values(is_hidden=True, deleted_at=func.now())
        )
        answers = db.scalars(select(CommunityAnswer).where(
            CommunityAnswer.author_id == user.id, CommunityAnswer.deleted_at.is_(None))).all()
        for answer in answers:
            if not answer.is_hidden:
                db.execute(
                    update(CommunityPost)
                    .where(CommunityPost.id == answer.post_id)
                    .values(answer_count=func.greatest(CommunityPost.answer_count - 1, 0),
                            **({"is_solved": False} if answer.is_accepted else {}))
                )
            answer.is_accepted = False
            answer.deleted_at = func.now()
    else:
        db.execute(update(CommunityPost).where(CommunityPost.author_id == user.id)
                   .values(is_anonymous=True))
        db.execute(update(CommunityAnswer).where(CommunityAnswer.author_id == user.id)
                   .values(is_anonymous=True))

    db.execute(delete(CommunityBookmark).where(CommunityBookmark.user_id == user.id))
    db.execute(delete(Notification).where(Notification.user_id == user.id))
    # Other people's notifications carry the nickname as text.
    db.execute(update(Notification).where(Notification.actor_nickname == old_nickname)
               .values(actor_nickname=None))
    db.execute(update(CommunityReport).where(CommunityReport.reporter_id == user.id)
               .values(reporter_id=None))
    db.execute(delete(EmailVerificationCode).where(EmailVerificationCode.email == old_email))
    db.execute(delete(AuthThrottle).where(AuthThrottle.key == old_email))

    previous_avatar = user.avatar_file
    user.email = f"deleted-{user.id}@deleted.invalid"
    user.nickname = f"deleted-{user.id}"
    user.password_hash = hash_password(secrets.token_urlsafe(32)[:60])
    user.avatar_file = None
    user.bio = None
    user.is_active = False
    user.is_admin = False
    user.token_version += 1
    db.commit()
    avatars.remove(previous_avatar)
    return {"deleted": True, "content_removed": payload.delete_content}

