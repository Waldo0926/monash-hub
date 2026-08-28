"""Community: posts, answers, votes, bookmarks, reports and moderation.

Anonymous visitors read everything. Writing needs an account. Moderation exists
from day one rather than after the first abuse report, because retrofitting it
onto a live forum is how communities get lost.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, selectinload

from app.api.deps import current_admin, current_user, current_user_optional
from app.api.serializers import answer_brief, post_brief, post_detail
from app.community import notifications
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
    q: str = "",
    category: str | None = None,
    unit_code: str | None = None,
    sort: str = Query("recent", pattern="^(recent|top|unanswered)$"),
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
    user: User | None = Depends(current_user_optional),
) -> dict:
    viewer = user.id if user else None
    if q or unit_code:
        posts, total = service.search_community(
            db, q, limit=limit, offset=offset, unit_code=unit_code
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
    for raw in slugs:
        slug = raw.strip().lower().replace(" ", "-")[:64]
        if not slug:
            continue
        tag = db.scalar(select(CommunityTag).where(CommunityTag.slug == slug))
        if tag is None:
            tag = CommunityTag(slug=slug, label=raw.strip()[:64], kind="topic")
            db.add(tag)
            db.flush()
        tags.append(tag)
    return tags


@router.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> dict:
    if payload.category not in VALID_CATEGORIES:
        raise HTTPException(400, f"Unknown category: {payload.category}")
    post = CommunityPost(
        author_id=user.id,
        title=payload.title.strip(),
        body=payload.body.strip(),
        category=payload.category,
        unit_code=payload.unit_code.upper() if payload.unit_code else None,
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
    post = db.get(CommunityPost, post_id)
    if post is None or post.is_hidden:
        raise HTTPException(404, "Post not found")

    parent = None
    if payload.parent_id is not None:
        parent = db.get(CommunityAnswer, payload.parent_id)
        # A reply has to belong to the thread it claims to be in, or it would
        # appear under a post its author never opened.
        if parent is None or parent.post_id != post.id or parent.is_hidden:
            raise HTTPException(404, "The reply you are replying to is not in this thread")

    answer = CommunityAnswer(
        post_id=post.id,
        parent_id=parent.id if parent else None,
        author_id=user.id,
        body=payload.body.strip(),
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
    if answer is None:
        raise HTTPException(404, "Answer not found")
    post = db.get(CommunityPost, answer.post_id)
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
    if target is None:
        raise HTTPException(404, "Nothing to vote on")

    # Same reasoning as the view counter: the unique constraint stops one person
    # voting twice, but two different people voting at once would still lose a
    # count if this were a read-modify-write.
    delta = -1 if existing else 1
    if existing:
        db.delete(existing)
    else:
        db.add(CommunityVote(user_id=user.id, target_type=target_type, target_id=target_id))
    db.flush()
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
    db.add(CommunityBookmark(user_id=user.id, post_id=post_id))
    db.commit()
    return {"bookmarked": True}


@router.post("/reports", status_code=status.HTTP_201_CREATED)
def create_report(
    payload: ReportRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(current_user_optional),
) -> dict:
    if payload.reason not in REPORT_REASONS:
        raise HTTPException(400, f"reason must be one of {', '.join(REPORT_REASONS)}")
    if payload.target_type not in ("post", "answer"):
        raise HTTPException(400, "target_type must be post or answer")
    report = CommunityReport(
        reporter_id=user.id if user else None,
        target_type=payload.target_type,
        target_id=payload.target_id,
        reason=payload.reason,
        detail=payload.detail,
    )
    db.add(report)
    db.commit()
    return {"id": report.id, "status": report.status}


@router.get("/reports")
def list_reports(db: Session = Depends(get_db), admin: User = Depends(current_admin)) -> dict:
    reports = db.scalars(
        select(CommunityReport)
        .where(CommunityReport.status == "open")
        .order_by(CommunityReport.created_at.desc())
    ).all()
    return {
        "total": len(reports),
        "results": [
            {
                "id": r.id,
                "target_type": r.target_type,
                "target_id": r.target_id,
                "reason": r.reason,
                "detail": r.detail,
                "created_at": r.created_at.isoformat(),
            }
            for r in reports
        ],
    }


@router.post("/moderate/{target_type}/{target_id}")
def moderate(
    target_type: str,
    target_id: int,
    action: str = Query(pattern="^(hide|unhide|pin|unpin)$"),
    db: Session = Depends(get_db),
    admin: User = Depends(current_admin),
) -> dict:
    model = CommunityPost if target_type == "post" else CommunityAnswer
    target = db.get(model, target_id)
    if target is None:
        raise HTTPException(404, "Nothing to moderate")
    if action in ("hide", "unhide"):
        target.is_hidden = action == "hide"
    elif isinstance(target, CommunityPost):
        target.is_pinned = action == "pin"
    else:
        raise HTTPException(400, "Only posts can be pinned")
    db.commit()
    return {"target_type": target_type, "target_id": target_id, "action": action}
