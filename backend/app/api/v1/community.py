"""Community: posts, answers, votes, bookmarks, reports and moderation.

Anonymous visitors read everything. Writing needs an account. Moderation exists
from day one rather than after the first abuse report, because retrofitting it
onto a live forum is how communities get lost.
"""
from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.api.deps import current_admin, current_user, current_user_optional
from app.api.serializers import _shown as shown
from app.api.serializers import answer_brief, post_brief, post_detail
from app.community import notifications
from app.core import throttle
from app.core.db import get_db
from app.models.community import (
    CommunityAnswer,
    CommunityBookmark,
    CommunityPost,
    CommunityReport,
    CommunityTag,
    CommunityVote,
    PostTag,
)
from app.models.user import User
from app.search import service

router = APIRouter(prefix="/community", tags=["community"])

CATEGORIES = [
    {"key": "units", "label": "Units & Study"},
    {"key": "course-planning", "label": "Course Planning"},
    {"key": "exchange", "label": "Exchange & Abroad"},
    {"key": "malaysia", "label": "Malaysia Campus"},
    {"key": "international", "label": "International Students"},
    {"key": "campus-life", "label": "Campus Life"},
]
VALID_CATEGORIES = {c["key"] for c in CATEGORIES}
REPORT_REASONS = ("spam", "abuse", "privacy", "advertising", "misinformation", "other")
UNIT_CODE = re.compile(r"^[A-Z]{3,4}\d{4}$")


class PostRequest(BaseModel):
    title: str = Field(min_length=5, max_length=300)
    body: str = Field(min_length=10, max_length=20000)
    category: str
    unit_code: str | None = Field(default=None, max_length=16)
    tags: list[str] = Field(default_factory=list, max_length=6)
    # Chosen when writing, per post. Not an account setting: the same person
    # asks some questions under their name and some not.
    anonymous: bool = False


class AnswerRequest(BaseModel):
    body: str = Field(min_length=2, max_length=20000)
    anonymous: bool = False
    # The reply this replies to. None is a reply to the post itself.
    parent_id: int | None = None


class ReportRequest(BaseModel):
    target_type: str
    target_id: int
    reason: str
    detail: str | None = Field(default=None, max_length=2000)


def _voted(db: Session, user: User | None, target_type: str, ids: list[int]) -> set[int]:
    """Which of ``ids`` this reader has already voted on.

    Without it the heart cannot show its own state, and a reader who has
    already liked something sees the same button as one who has not.
    """
    if user is None or not ids:
        return set()
    return set(
        db.scalars(
            select(CommunityVote.target_id).where(
                CommunityVote.user_id == user.id,
                CommunityVote.target_type == target_type,
                CommunityVote.target_id.in_(ids),
            )
        )
    )


def _thread_ids(answers) -> list[int]:
    found: list[int] = []
    for answer in answers:
        found.append(answer.id)
        found += _thread_ids(answer.children)
    return found


@router.get("/categories")
def list_categories() -> dict:
    return {"categories": CATEGORIES}


@router.get("/posts")
def list_posts(
    q: str = Query("", max_length=300),
    category: str | None = None,
    unit_code: str | None = None,
    sort: str = Query("recent", pattern="^(recent|top|unanswered)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User | None = Depends(current_user_optional),
) -> dict:
    viewer = user.id if user else None
    if q or unit_code:
        # The category still applies to a search. It used to be dropped, so
        # searching inside "Malaysia Campus" searched the whole forum.
        posts, total = service.search_community(
            db, q, limit=limit, offset=offset, unit_code=unit_code, category=category,
            unanswered=sort == "unanswered",
        )
        voted = _voted(db, user, "post", [p.id for p in posts])
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "results": [post_brief(p, viewer, voted) for p in posts],
        }

    stmt = select(CommunityPost).where(CommunityPost.is_hidden.is_(False))
    count_stmt = select(func.count(CommunityPost.id)).where(CommunityPost.is_hidden.is_(False))
    if category:
        stmt = stmt.where(CommunityPost.category == category)
        count_stmt = count_stmt.where(CommunityPost.category == category)
    if sort == "top":
        stmt = stmt.order_by(CommunityPost.is_pinned.desc(), CommunityPost.vote_count.desc())
    elif sort == "unanswered":
        stmt = stmt.where(CommunityPost.answer_count == 0).order_by(CommunityPost.created_at.desc())
        count_stmt = count_stmt.where(CommunityPost.answer_count == 0)
    else:
        stmt = stmt.order_by(CommunityPost.is_pinned.desc(), CommunityPost.updated_at.desc())

    posts = db.scalars(
        stmt.options(selectinload(CommunityPost.post_tags).selectinload(PostTag.tag))
        .limit(limit)
        .offset(offset)
    ).all()
    voted = _voted(db, user, "post", [p.id for p in posts])
    return {
        "total": int(db.scalar(count_stmt) or 0),
        "limit": limit,
        "offset": offset,
        "results": [post_brief(p, viewer, voted) for p in posts],
    }


def _resolve_tags(db: Session, slugs: list[str]) -> list[CommunityTag]:
    tags: list[CommunityTag] = []
    seen: set[str] = set()
    for raw in slugs:
        slug = "-".join(raw.strip().lower().split())[:64]
        if not slug or slug in seen:
            # The same tag twice would violate uq_post_tag and fail the post.
            continue
        seen.add(slug)
        tag = db.scalar(select(CommunityTag).where(CommunityTag.slug == slug))
        if tag is None:
            try:
                # A savepoint, so losing a race to create the same new tag
                # costs one lookup rather than the whole post.
                with db.begin_nested():
                    tag = CommunityTag(slug=slug, label=raw.strip()[:64], kind="topic")
                    db.add(tag)
            except IntegrityError:
                tag = db.scalar(select(CommunityTag).where(CommunityTag.slug == slug))
        if tag is not None:
            tags.append(tag)
    return tags


def _visible_post(db: Session, post_id: int) -> CommunityPost:
    post = db.get(CommunityPost, post_id)
    if post is None or post.is_hidden:
        raise HTTPException(404, "Post not found")
    return post


@router.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> dict:
    if payload.category not in VALID_CATEGORIES:
        raise HTTPException(400, f"Unknown category: {payload.category}")
    title, body = payload.title.strip(), payload.body.strip()
    # The length limits are on the raw text; five spaces are not a title.
    if len(title) < 5 or len(body) < 10:
        raise HTTPException(422, "Write a real title and a question with some detail.")
    unit_code = "".join((payload.unit_code or "").split()).upper() or None
    if unit_code and not UNIT_CODE.match(unit_code):
        raise HTTPException(422, "That is not a unit code (for example FIT2086).")
    post = CommunityPost(
        author_id=user.id,
        title=title,
        body=body,
        category=payload.category,
        unit_code=unit_code,
        is_anonymous=payload.anonymous,
    )
    db.add(post)
    db.flush()
    for tag in _resolve_tags(db, payload.tags):
        db.add(PostTag(post_id=post.id, tag_id=tag.id))
    db.commit()
    db.refresh(post)
    return post_detail(post, viewer_id=user.id)


@router.get("/posts/{post_id}")
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(current_user_optional),
) -> dict:
    post = db.scalar(
        select(CommunityPost)
        .where(CommunityPost.id == post_id, CommunityPost.is_hidden.is_(False))
        .options(
            selectinload(CommunityPost.answers)
            .selectinload(CommunityAnswer.children)
            .selectinload(CommunityAnswer.children),
            selectinload(CommunityPost.post_tags).selectinload(PostTag.tag),
        )
    )
    if post is None:
        raise HTTPException(404, "Post not found")
    # Counted with an atomic UPDATE rather than read-modify-write: two people
    # opening the same thread at once would otherwise each read the same number
    # and write it back, losing one of the views.
    db.execute(
        update(CommunityPost)
        .where(CommunityPost.id == post_id)
        .values(view_count=CommunityPost.view_count + 1)
    )
    db.commit()
    return post_detail(
        post,
        viewer_id=user.id if user else None,
        voted_posts=_voted(db, user, "post", [post.id]),
        voted_answers=_voted(db, user, "answer", _thread_ids(post.answers)),
    )


@router.get("/posts/{post_id}/answers")
def list_answers(
    post_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(current_user_optional),
) -> dict:
    answers = db.scalars(
        select(CommunityAnswer)
        .where(
            CommunityAnswer.post_id == post_id,
            CommunityAnswer.parent_id.is_(None),
            CommunityAnswer.is_hidden.is_(False),
        )
        .order_by(CommunityAnswer.is_accepted.desc(), CommunityAnswer.vote_count.desc())
    ).all()
    answers = [a for a in answers if shown(a)]
    voted = _voted(db, user, "answer", _thread_ids(answers))
    viewer = user.id if user else None
    return {
        "total": len(answers),
        "results": [answer_brief(a, viewer, voted) for a in answers],
    }


@router.post("/posts/{post_id}/answers", status_code=status.HTTP_201_CREATED)
def create_answer(
    post_id: int,
    payload: AnswerRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> dict:
    post = _visible_post(db, post_id)
    body = payload.body.strip()
    if len(body) < 2:
        raise HTTPException(422, "Write a reply first.")

    parent = None
    if payload.parent_id is not None:
        parent = db.get(CommunityAnswer, payload.parent_id)
        # A reply has to belong to the thread it claims to be in, or it would
        # appear under a post its author never opened.
        if (parent is None or parent.post_id != post.id or parent.is_hidden
                or parent.deleted_at is not None):
            raise HTTPException(404, "The reply you are replying to is not in this thread")

    answer = CommunityAnswer(
        post_id=post.id,
        parent_id=parent.id if parent else None,
        author_id=user.id,
        body=body,
        is_anonymous=payload.anonymous,
    )
    db.add(answer)
    db.flush()
    db.execute(
        update(CommunityPost)
        .where(CommunityPost.id == post.id)
        .values(answer_count=CommunityPost.answer_count + 1, updated_at=func.now())
    )
    notifications.notify_answer(db, post=post, answer=answer, actor=user)
    db.commit()
    db.refresh(answer)
    return answer_brief(answer, viewer_id=user.id)


@router.post("/answers/{answer_id}/accept")
def accept_answer(
    answer_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> dict:
    answer = db.get(CommunityAnswer, answer_id)
    if answer is None or answer.is_hidden or answer.deleted_at is not None:
        raise HTTPException(404, "Answer not found")
    post = _visible_post(db, answer.post_id)
    if post.author_id != user.id and not user.is_admin:
        raise HTTPException(403, "Only the person who asked can mark an answer as helpful")
    for other in post.answers:
        other.is_accepted = other.id == answer.id
    post.is_solved = True
    notifications.notify_accepted(db, post=post, answer=answer, actor=user)
    db.commit()
    return {"post_id": post.id, "accepted_answer_id": answer.id, "is_solved": True}


@router.post("/vote")
def vote(
    target_type: str = Query(pattern="^(post|answer)$"),
    target_id: int = Query(),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> dict:
    """One vote per user per target; voting again takes it back."""
    existing = db.scalar(
        select(CommunityVote).where(
            CommunityVote.user_id == user.id,
            CommunityVote.target_type == target_type,
            CommunityVote.target_id == target_id,
        )
    )
    model = CommunityPost if target_type == "post" else CommunityAnswer
    target = db.get(model, target_id)
    if target is None or target.is_hidden or getattr(target, "deleted_at", None) is not None:
        raise HTTPException(404, "Nothing to vote on")

    # Same reasoning as the view counter: the unique constraint stops one person
    # voting twice, but two different people voting at once would still lose a
    # count if this were a read-modify-write.
    delta = -1 if existing else 1
    if existing:
        db.delete(existing)
    else:
        db.add(CommunityVote(user_id=user.id, target_type=target_type, target_id=target_id))
    try:
        db.flush()
    except IntegrityError as exc:
        # A double click: the other request already recorded this vote.
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "That vote is already counted") from exc
    db.execute(
        update(model)
        .where(model.id == target_id)
        .values(vote_count=func.greatest(model.vote_count + delta, 0))
    )
    db.commit()
    db.refresh(target)
    return {"voted": delta > 0, "vote_count": target.vote_count}


@router.post("/bookmarks/{post_id}")
def toggle_bookmark(
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> dict:
    existing = db.scalar(
        select(CommunityBookmark).where(
            CommunityBookmark.user_id == user.id, CommunityBookmark.post_id == post_id
        )
    )
    if existing:
        db.delete(existing)
        db.commit()
        return {"bookmarked": False}
    _visible_post(db, post_id)
    db.add(CommunityBookmark(user_id=user.id, post_id=post_id))
    try:
        db.commit()
    except IntegrityError:
        # Saved twice at once - it is saved, which is what was asked for.
        db.rollback()
    return {"bookmarked": True}


@router.post("/reports", status_code=status.HTTP_201_CREATED)
def create_report(
    payload: ReportRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(current_user_optional),
) -> dict:
    if payload.reason not in REPORT_REASONS:
        raise HTTPException(400, f"reason must be one of {', '.join(REPORT_REASONS)}")
    if payload.target_type not in ("post", "answer"):
        raise HTTPException(400, "target_type must be post or answer")
    model = CommunityPost if payload.target_type == "post" else CommunityAnswer
    if db.get(model, payload.target_id) is None:
        raise HTTPException(404, "Nothing to report")

    reporter = f"user:{user.id}" if user else f"ip:{throttle.client_address(request)}"
    # The same person reporting the same thing again adds nothing for the
    # moderator to read; answer as if it were filed, because it is.
    if user is not None:
        existing = db.scalar(select(CommunityReport).where(
            CommunityReport.reporter_id == user.id,
            CommunityReport.target_type == payload.target_type,
            CommunityReport.target_id == payload.target_id,
            CommunityReport.status == "open",
        ))
        if existing is not None:
            return {"id": existing.id, "status": existing.status}
    try:
        throttle.check(db, throttle.REPORTS_PER_REPORTER, reporter)
    except throttle.Throttled as limited:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS, "Too many reports. Try again later.",
            headers={"Retry-After": str(limited.retry_after_seconds)},
        ) from limited

    report = CommunityReport(
        reporter_id=user.id if user else None,
        target_type=payload.target_type,
        target_id=payload.target_id,
        reason=payload.reason,
        detail=(payload.detail or "").strip() or None,
    )
    db.add(report)
    throttle.record(db, throttle.REPORTS_PER_REPORTER, reporter)
    db.commit()
    return {"id": report.id, "status": report.status}


def _report_target(db: Session, report: CommunityReport) -> dict | None:
    """What a moderator needs to judge a report without opening five tabs."""
    if report.target_type == "post":
        post = db.get(CommunityPost, report.target_id)
        if post is None:
            return None
        return {"post_id": post.id, "title": post.title, "excerpt": post.body[:400],
                "author": post.author.nickname if post.author else None,
                "anonymous": post.is_anonymous, "hidden": post.is_hidden,
                "deleted": post.deleted_at is not None}
    answer = db.get(CommunityAnswer, report.target_id)
    if answer is None:
        return None
    post = db.get(CommunityPost, answer.post_id)
    return {"post_id": answer.post_id, "title": post.title if post else None,
            "excerpt": answer.body[:400],
            "author": answer.author.nickname if answer.author else None,
            "anonymous": answer.is_anonymous, "hidden": answer.is_hidden,
            "deleted": answer.deleted_at is not None}


@router.get("/reports")
def list_reports(
    status_filter: str = Query("open", alias="status", pattern="^(open|resolved|dismissed)$"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    admin: User = Depends(current_admin),
) -> dict:
    reports = db.scalars(
        select(CommunityReport)
        .where(CommunityReport.status == status_filter)
        .order_by(CommunityReport.created_at.desc())
        .limit(limit)
    ).all()
    total = db.scalar(select(func.count(CommunityReport.id)).where(
        CommunityReport.status == status_filter)) or 0
    return {
        "total": int(total),
        "results": [
            {
                "id": r.id,
                "target_type": r.target_type,
                "target_id": r.target_id,
                "reason": r.reason,
                "detail": r.detail,
                "status": r.status,
                "created_at": r.created_at.isoformat(),
                "target": _report_target(db, r),
            }
            for r in reports
        ],
    }


@router.post("/reports/{report_id}/resolve")
def resolve_report(
    report_id: int,
    action: str = Query(pattern="^(hide|dismiss)$"),
    db: Session = Depends(get_db),
    admin: User = Depends(current_admin),
) -> dict:
    """Close a report: hide what it is about, or decide it is fine.

    Reports could be filed and listed but never closed, so the queue only grew
    and a moderator could not tell today's reports from last month's. Hiding
    closes every open report about the same thing at once.
    """
    report = db.get(CommunityReport, report_id)
    if report is None:
        raise HTTPException(404, "Report not found")
    if action == "hide":
        model = CommunityPost if report.target_type == "post" else CommunityAnswer
        target = db.get(model, report.target_id)
        if target is not None and not target.is_hidden:
            if isinstance(target, CommunityAnswer):
                _count_answer(db, target.post_id, -1)
            target.is_hidden = True
        _close_reports(db, report.target_type, report.target_id, "resolved")
    else:
        report.status = "dismissed"
    db.commit()
    return {"id": report.id, "status": report.status}


def _close_reports(db: Session, target_type: str, target_id: int, outcome: str) -> None:
    db.execute(
        update(CommunityReport)
        .where(CommunityReport.target_type == target_type,
               CommunityReport.target_id == target_id,
               CommunityReport.status == "open")
        .values(status=outcome)
        .execution_options(synchronize_session="fetch")
    )


@router.post("/moderate/{target_type}/{target_id}")
def moderate(
    target_type: str,
    target_id: int,
    action: str = Query(pattern="^(hide|unhide|pin|unpin)$"),
    db: Session = Depends(get_db),
    admin: User = Depends(current_admin),
) -> dict:
    if target_type not in ("post", "answer"):
        raise HTTPException(400, "target_type must be post or answer")
    model = CommunityPost if target_type == "post" else CommunityAnswer
    target = db.get(model, target_id)
    if target is None:
        raise HTTPException(404, "Nothing to moderate")
    if action in ("hide", "unhide"):
        if action == "unhide" and target.deleted_at is not None:
            raise HTTPException(409, "Its author deleted this; it cannot be restored")
        hide = action == "hide"
        if isinstance(target, CommunityAnswer) and target.is_hidden != hide:
            _count_answer(db, target.post_id, -1 if hide else 1)
        target.is_hidden = hide
        if hide:
            _close_reports(db, target_type, target_id, "resolved")
    elif isinstance(target, CommunityPost):
        target.is_pinned = action == "pin"
    else:
        raise HTTPException(400, "Only posts can be pinned")
    db.commit()
    return {"target_type": target_type, "target_id": target_id, "action": action}


def _count_answer(db: Session, post_id: int, delta: int) -> None:
    db.execute(
        update(CommunityPost)
        .where(CommunityPost.id == post_id)
        .values(answer_count=func.greatest(CommunityPost.answer_count + delta, 0))
    )


@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> dict:
    """Take down your own question.

    There was no way to do this at all: a student who posted something they
    regretted - their name in a screenshot, a message meant for somebody else -
    had to report their own post and wait. The row is kept, hidden, so reports
    about it and the replies under it stay intact for moderation.
    """
    post = _visible_post(db, post_id)
    if post.author_id != user.id and not user.is_admin:
        raise HTTPException(403, "Only its author can delete this")
    post.is_hidden = True
    post.deleted_at = func.now()
    db.commit()
    return {"id": post.id, "deleted": True}


@router.delete("/answers/{answer_id}")
def delete_answer(
    answer_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> dict:
    """Take down your own reply. Replies under it stay, under a placeholder."""
    answer = db.get(CommunityAnswer, answer_id)
    if answer is None or answer.is_hidden or answer.deleted_at is not None:
        raise HTTPException(404, "Answer not found")
    if answer.author_id != user.id and not user.is_admin:
        raise HTTPException(403, "Only its author can delete this")
    answer.deleted_at = func.now()
    if answer.is_accepted:
        answer.is_accepted = False
        db.execute(
            update(CommunityPost)
            .where(CommunityPost.id == answer.post_id)
            .values(is_solved=False)
        )
    _count_answer(db, answer.post_id, -1)
    db.commit()
    return {"id": answer.id, "deleted": True}
