"""Unified search over Handbook units, official pages, FAQ and community posts.

PostgreSQL does all of this: ``tsvector`` for full text, ``pg_trgm`` for typo
tolerance on titles, and an exact-code shortcut in front of both because a
student typing ``FIT2102`` wants that unit first and nothing else.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import and_, case, func, or_, select, text
from sqlalchemy.orm import Session, selectinload

from app.models.community import CommunityPost, PostTag
from app.models.handbook import Unit, UnitOffering
from app.models.knowledge import FaqEntry, OfficialPage
from app.search.keywords import extract_unit_codes


@dataclass
class SearchGroup:
    kind: str
    label: str
    total: int
    results: list[dict[str, Any]] = field(default_factory=list)


def _ts_query(term: str):
    """``websearch_to_tsquery`` handles quotes and OR without us sanitising input."""
    return func.websearch_to_tsquery("english", term)


def _array_contained_in_query(column: str, term: str):
    """True when any tag/keyword in ``column`` appears inside the query text.

    The usual direction - does the query match the text - fails for a bilingual
    product: PostgreSQL's English stemmer does nothing useful with "怎么申请 SC",
    and a student typing that still means special consideration. Checking the
    other way round - "does the query contain one of this row's curated
    keywords" - handles both languages without a second text-search config.

    Keyword and tag values are curated in the repository, never user input, so
    they are safe to use as a regex pattern here.
    """
    return text(
        f"EXISTS (SELECT 1 FROM unnest({column}) AS kw WHERE kw <> '' AND CASE "
        # Latin keywords need a word boundary: without it the curated keyword
        # "sc" fires on "scooter" and every stray question lands on the special
        # consideration page.
        "WHEN kw ~ '^[[:ascii:]]+$' "
        "THEN :kw_query ~* ('(^|[^[:alnum:]])' || kw || '([^[:alnum:]]|$)') "
        # CJK has no word boundaries to anchor to, so substring is the only
        # sensible test - and Chinese keywords are long enough not to collide.
        "ELSE :kw_query ILIKE '%%' || kw || '%%' END)"
    ).bindparams(kw_query=term)


def search_units(
    db: Session,
    query: str,
    *,
    year: int,
    limit: int = 10,
    offset: int = 0,
    campus: str | None = None,
    teaching_period: str | None = None,
    level: str | None = None,
    prefix: str | None = None,
    has_exam: bool | None = None,
    sort: str = "relevance",
) -> tuple[list[Unit], int]:
    stmt = select(Unit).where(Unit.academic_year == year, Unit.is_active.is_(True))
    count_stmt = select(func.count(Unit.id)).where(
        Unit.academic_year == year, Unit.is_active.is_(True)
    )

    codes = extract_unit_codes(query)
    term = (query or "").strip()

    if term:
        if codes:
            match = or_(
                Unit.unit_code.in_(codes),
                Unit.search_vector.op("@@")(_ts_query(term)),
            )
        else:
            match = or_(
                Unit.unit_code.ilike(f"{term}%"),
                Unit.search_vector.op("@@")(_ts_query(term)),
                func.similarity(Unit.title, term) > 0.25,
            )
        stmt = stmt.where(match)
        count_stmt = count_stmt.where(match)

    filters = []
    # Campus and teaching period have to be true of the *same* offering. Asked
    # separately they are two EXISTS clauses, and a unit taught at Malaysia in
    # first semester and at Clayton over the full year answered "Malaysia, full
    # year" - a combination it is not taught in anywhere. On the small campuses
    # that was most of the page: "Suzhou (SEU), second semester" listed 27 units
    # of which 2 are actually offered there then, and "Clayton, October intake
    # teaching period, Malaysia campus" listed 13 of which none are.
    offering = [
        column == value
        for column, value in ((UnitOffering.campus, campus),
                              (UnitOffering.teaching_period, teaching_period))
        if value
    ]
    if offering:
        filters.append(Unit.offerings.any(and_(*offering)))
    if level:
        filters.append(Unit.level == level)
    if prefix:
        filters.append(Unit.subject_prefix == prefix.upper())
    if has_exam is not None:
        filters.append(Unit.has_exam.is_(has_exam))
    for condition in filters:
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)

    if sort == "code":
        stmt = stmt.order_by(Unit.unit_code)
    elif sort == "title":
        stmt = stmt.order_by(Unit.title)
    elif term:
        # Exact code first, then text rank, then trigram similarity on title.
        # A boolean cannot be cast to a number in PostgreSQL, so rank it via CASE.
        exact = case((Unit.unit_code.in_(codes or [term.upper()]), 1), else_=0)
        rank = func.ts_rank(Unit.search_vector, _ts_query(term))
        stmt = stmt.order_by(exact.desc(), rank.desc(), func.similarity(Unit.title, term).desc())
    else:
        stmt = stmt.order_by(Unit.unit_code)

    stmt = stmt.options(
        selectinload(Unit.offerings),
        selectinload(Unit.assessments),
    ).limit(limit).offset(offset)

    return list(db.scalars(stmt)), int(db.scalar(count_stmt) or 0)


def search_official(
    db: Session, query: str, *, limit: int = 10, offset: int = 0, category: str | None = None
) -> tuple[list[OfficialPage], int]:
    stmt = select(OfficialPage).where(OfficialPage.status == "ok")
    count_stmt = select(func.count(OfficialPage.id)).where(OfficialPage.status == "ok")
    term = (query or "").strip()
    if term:
        match = or_(
            OfficialPage.search_vector.op("@@")(_ts_query(term)),
            func.similarity(OfficialPage.title, term) > 0.2,
            _array_contained_in_query("official_pages.tags", term),
        )
        stmt = stmt.where(match)
        count_stmt = count_stmt.where(match)
    if category:
        stmt = stmt.where(OfficialPage.category == category)
        count_stmt = count_stmt.where(OfficialPage.category == category)
    if term:
        stmt = stmt.order_by(
            func.ts_rank(OfficialPage.search_vector, _ts_query(term)).desc(),
            func.similarity(OfficialPage.title, term).desc(),
        )
    else:
        stmt = stmt.order_by(OfficialPage.category, OfficialPage.title)
    stmt = stmt.limit(limit).offset(offset)
    return list(db.scalars(stmt)), int(db.scalar(count_stmt) or 0)


def search_faq(db: Session, query: str, *, limit: int = 5) -> list[FaqEntry]:
    term = (query or "").strip()
    stmt = select(FaqEntry)
    if term:
        stmt = stmt.where(
            or_(
                FaqEntry.search_vector.op("@@")(_ts_query(term)),
                _array_contained_in_query("faq_entries.keywords", term),
                func.similarity(FaqEntry.question, term) > 0.2,
            )
        ).order_by(
            FaqEntry.priority.desc(),
            func.ts_rank(FaqEntry.search_vector, _ts_query(term)).desc(),
        )
    else:
        stmt = stmt.order_by(FaqEntry.priority.desc())
    return list(db.scalars(stmt.limit(limit)))


def search_community(
    db: Session, query: str, *, limit: int = 10, offset: int = 0, unit_code: str | None = None
) -> tuple[list[CommunityPost], int]:
    stmt = select(CommunityPost).where(CommunityPost.is_hidden.is_(False))
    count_stmt = select(func.count(CommunityPost.id)).where(CommunityPost.is_hidden.is_(False))
    term = (query or "").strip()
    codes = extract_unit_codes(term)
    if unit_code:
        stmt = stmt.where(CommunityPost.unit_code == unit_code.upper())
        count_stmt = count_stmt.where(CommunityPost.unit_code == unit_code.upper())
    elif term:
        match = or_(
            CommunityPost.search_vector.op("@@")(_ts_query(term)),
            CommunityPost.unit_code.in_(codes) if codes else CommunityPost.id.is_(None),
        )
        stmt = stmt.where(match)
        count_stmt = count_stmt.where(match)
    # post_brief reads every result's tags, so load them in one extra query
    # rather than one per row.
    stmt = (
        stmt.options(selectinload(CommunityPost.post_tags).selectinload(PostTag.tag))
        .order_by(CommunityPost.is_pinned.desc(), CommunityPost.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(stmt)), int(db.scalar(count_stmt) or 0)
