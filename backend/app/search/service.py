"""Unified search over Handbook units and degrees, official pages, FAQ and posts.

PostgreSQL does all of this: ``tsvector`` for full text, ``pg_trgm`` for typo
tolerance on titles, and an exact-code shortcut in front of both because a
student typing ``FIT2102`` wants that unit first and nothing else.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from sqlalchemy import Integer, and_, case, cast, func, literal, literal_column, or_, select, text
from sqlalchemy.orm import Session, selectinload

from app.models.community import CommunityPost, PostTag
from app.models.curriculum import Course
from app.models.handbook import Unit, UnitOffering
from app.models.knowledge import FaqEntry, OfficialPage
from app.models.translation import (
    COURSE,
    CURATED,
    HUMAN,
    PUBLISHED,
    ContentTranslation,
)
from app.models.translation import (
    FAQ_ENTRY as FAQ_ENTRY_TRANSLATION,
)
from app.models.translation import (
    OFFICIAL_PAGE as OFFICIAL_PAGE_TRANSLATION,
)
from app.models.translation import (
    UNIT as UNIT_TRANSLATION,
)
from app.search import faq_match
from app.search.chinese import (
    chinese_for,
    concept_runs,
    concepts,
    expand,
    expanded_query,
    has_cjk,
    latin_part,
)
from app.search.keywords import extract_unit_codes


@dataclass
class SearchGroup:
    kind: str
    label: str
    total: int
    results: list[dict[str, Any]] = field(default_factory=list)


# A student who half-remembers a unit types the half they remember. "5215" is
# FIT5215 to them, and matching only from the start of the code answered
# "nothing indexed for this yet" for a unit that is indexed. A fragment is short,
# has no spaces and is letters and digits - which is what a code is made of, and
# what a sentence is not.
def _is_code_fragment(term: str) -> bool:
    return term.isalnum() and term.isascii() and 2 <= len(term) <= 8


def _websearch(text_: str):
    return func.websearch_to_tsquery("english", text_)


def _any_of(alternatives) -> Any:
    query = None
    for alternative in alternatives:
        part = _websearch(alternative)
        query = part if query is None else query.op("||")(part)
    return query


def _ts_query(term: str, *, strict: bool = True):
    """The English text-search query for ``term``.

    ``websearch_to_tsquery`` handles quotes and OR without us sanitising input.

    A CJK query is expanded through ``app/search/chinese.py`` into the concepts
    it names, each with its English alternatives. Strict - the default - wants
    every concept on the page: 学生签证续签 is (student visa) AND (renew OR
    extend OR ...). Loose wants any one of them, which is what the query used
    to be, and it found a page about visas for a question about renewing one.
    Callers fall back to loose only when strict finds nothing, so a question
    phrased in words no page uses still gets somewhere.

    The raw term is always ORed in as well: a Chinese-only query contributes
    nothing to an English tsvector, but an English one is left exactly as it
    was.
    """
    groups = concepts(term)
    if not groups:
        return _websearch(expanded_query(term))
    latin = latin_part(term)
    parts = [_any_of(alternatives) for alternatives in groups]
    if latin:
        parts.append(_websearch(latin))
    combined = parts[0]
    for part in parts[1:]:
        combined = combined.op("&&" if strict else "||")(part)
    return _websearch(term).op("||")(combined)


def _is_multi_concept(term: str) -> bool:
    """Whether strict and loose can give different answers for ``term``."""
    groups = concepts(term)
    return len(groups) + (1 if groups and latin_part(term) else 0) > 1


# Chinese has no word boundaries, so a student typing 学籍统计 is typing a
# contiguous run and means it. Substring is the honest query, and pg_trgm makes
# it an indexed one. The similarity fallback catches a query that is close but
# not contained - a synonym the glossary happens to know differently.
ZH_SIMILARITY = 0.3


def _like(term: str) -> str:
    """``term`` with LIKE's wildcards escaped, so "100%" is not "100 then anything"."""
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _contains(column, term: str):
    return column.ilike(f"%{_like(term)}%", escape="\\")


def _starts(column, term: str):
    return column.ilike(f"{_like(term)}%", escape="\\")


def _zh_match(column, term: str):
    """Match a Chinese query against a column holding translated text."""
    return or_(
        _contains(column, term),
        func.similarity(column, term) > ZH_SIMILARITY,
    )


def _array_contained_in_query(column: str, term: str, alternatives: tuple[str, ...] = ()):
    """True when any tag/keyword in ``column`` appears inside the query text.

    The usual direction - does the query match the text - fails for a bilingual
    product: PostgreSQL's English stemmer does nothing useful with "怎么申请 SC",
    and a student typing that still means special consideration. Checking the
    other way round - "does the query contain one of this row's curated
    keywords" - handles both languages without a second text-search config.

    ``alternatives`` are the English phrases a CJK query expands to. A tag
    has to *be* one of them, not sit inside one: 续签 expands to "visa
    extension", and the special consideration page's tag "extension" is not
    what a student renewing a visa is looking for.

    Keyword and tag values are curated in the repository, never user input, so
    they are safe to use as a regex pattern here.
    """
    return text(
        f"EXISTS (SELECT 1 FROM unnest({column}) AS kw WHERE kw <> '' AND (CASE "
        # Latin keywords need a word boundary: without it the curated keyword
        # "sc" fires on "scooter" and every stray question lands on the special
        # consideration page.
        "WHEN kw ~ '^[[:ascii:]]+$' "
        "THEN :kw_query ~* ('(^|[^[:alnum:]])' || kw || '([^[:alnum:]]|$)') "
        # CJK has no word boundaries to anchor to, so substring is the only
        # sensible test - and Chinese keywords are long enough not to collide.
        "ELSE :kw_query ILIKE '%%' || kw || '%%' END "
        "OR lower(kw) = ANY(CAST(:kw_alternatives AS text[]))))"
    ).bindparams(kw_query=term, kw_alternatives=[a.lower() for a in alternatives])


def search_units(db: Session, query: str, *, year: int, **kwargs) -> tuple[list[Unit], int]:
    """Units matching ``query``, most relevant first.

    A query naming several concepts is first asked for units about all of them.
    Only when none are is it asked again for units about any: 延期考试 used to
    list 1,247 units - every one that mentions an exam - because the loose
    query was the only one there was.
    """
    found = _search_units(db, query, year=year, **kwargs)
    if found[1] == 0 and _is_multi_concept((query or "").strip()):
        return _search_units(db, query, year=year, strict=False, **kwargs)
    return found


def _search_units(
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
    strict: bool = True,
) -> tuple[list[Unit], int]:
    stmt = select(Unit).where(Unit.academic_year == year, Unit.is_active.is_(True))
    count_stmt = select(func.count(Unit.id)).where(
        Unit.academic_year == year, Unit.is_active.is_(True)
    )

    codes = extract_unit_codes(query)
    term = (query or "").strip()
    translated_title = (
        _translated_title(Unit, UNIT_TRANSLATION, Unit.unit_code, Unit.title)
        if has_cjk(term)
        else None
    )

    if term:
        if codes:
            matches = [
                Unit.unit_code.in_(codes),
                Unit.search_vector.op("@@")(_ts_query(term, strict=strict)),
            ]
        else:
            matches = [
                _starts(Unit.unit_code, term),
                *([_contains(Unit.unit_code, term)] if _is_code_fragment(term) else []),
                Unit.search_vector.op("@@")(_ts_query(term, strict=strict)),
                func.similarity(Unit.title, term) > 0.25,
            ]
        if translated_title is not None:
            matches.extend(
                [_contains(translated_title, term), _zh_match(Unit.search_zh, term)]
            )
        match = or_(*matches)
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
        # A code carrying the fragment beats a title that merely resembles it:
        # searching "5215" should put FIT5215 above anything with a 5215 in its
        # prose.
        in_code = case((_contains(Unit.unit_code, term), 1), else_=0) \
            if _is_code_fragment(term) else literal(0)
        rank = func.ts_rank(Unit.search_vector, _ts_query(term, strict=strict))
        # A Chinese query gets little or nothing from ts_rank even after the
        # glossary expansion, so the Chinese text is what orders those results.
        zh_rank = (
            func.coalesce(func.similarity(Unit.search_zh, term), 0)
            if has_cjk(term) else literal(0)
        )
        exact_translation = (
            case((translated_title == term, 1), else_=0)
            if translated_title is not None
            else literal(0)
        )
        translated_title_contains = (
            case((_contains(translated_title, term), 1), else_=0)
            if translated_title is not None
            else literal(0)
        )
        stmt = stmt.order_by(
            exact.desc(), in_code.desc(), exact_translation.desc(),
            translated_title_contains.desc(), rank.desc(), zh_rank.desc(),
            func.similarity(Unit.title, term).desc(),
        )
    else:
        stmt = stmt.order_by(Unit.unit_code)

    stmt = stmt.options(
        selectinload(Unit.offerings),
        selectinload(Unit.assessments),
    ).limit(limit).offset(offset)

    return list(db.scalars(stmt)), int(db.scalar(count_stmt) or 0)


def _translated_title(model, target_type: str, target_key, source_title):
    """One Chinese title for the outer source row, when one is published.

    Translations are stored as an exact English-to-Chinese string map. Looking
    up the row's own English title inside that JSON map lets a query match only
    the translated title; matching the whole translation row would also return
    an item merely because its overview happened to contain the words.

    This direct lookup also makes titles searchable immediately after a curated
    correction is deployed. The flattened ``search_zh`` column remains the
    indexed path for longer translated prose.
    """
    return (
        select(
            func.coalesce(
                ContentTranslation.text,
                func.jsonb_extract_path_text(
                    ContentTranslation.data, "strings", source_title
                ),
            )
        )
        .where(
            ContentTranslation.locale == "zh",
            ContentTranslation.target_type == target_type,
            ContentTranslation.target_key == target_key,
            ContentTranslation.status == PUBLISHED,
            or_(
                ContentTranslation.field == "title",
                ContentTranslation.field == "content",
            ),
        )
        .order_by(
            case(
                (ContentTranslation.provenance == HUMAN, 2),
                (ContentTranslation.provenance == CURATED, 1),
                else_=0,
            ).desc()
        )
        .limit(1)
        .correlate(model)
        .scalar_subquery()
    )


def search_courses(
    db: Session,
    query: str,
    *,
    year: int,
    limit: int = 10,
    offset: int = 0,
    campus: str | None = None,
    course_type: str | None = None,
    faculty: str | None = None,
) -> tuple[list[Course], int]:
    """Search degrees by code, English title, or their published Chinese title."""
    stmt = select(Course).where(Course.academic_year == year, Course.is_active.is_(True))
    count_stmt = select(func.count(Course.id)).where(
        Course.academic_year == year, Course.is_active.is_(True)
    )
    term = (query or "").strip()
    translated_title = (
        _translated_title(Course, COURSE, Course.course_code, Course.title)
        if has_cjk(term)
        else None
    )

    if term:
        matches = [
            _starts(Course.course_code, term),
            _contains(Course.title, term),
            _starts(Course.abbreviated_name, term),
        ]
        if translated_title is not None:
            matches.append(_contains(translated_title, term))
        # 商科学士 is "bachelor" and "commerce or business". Degree titles are
        # short and English, so every concept has to appear in the title.
        groups = concepts(term)
        if groups:
            matches.append(and_(*(
                or_(*(_contains(Course.title, alternative) for alternative in alternatives))
                for alternatives in groups
            )))
        match = or_(*matches)
        stmt = stmt.where(match)
        count_stmt = count_stmt.where(match)

    filters = []
    if campus:
        filters.append(Course.campuses.any(campus))
    if course_type:
        filters.append(Course.course_type == course_type)
    if faculty:
        filters.append(Course.faculty == faculty)
    for condition in filters:
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)

    if term:
        exact_code = case((func.upper(Course.course_code) == term.upper(), 1), else_=0)
        exact_translation = (
            case((func.lower(translated_title) == term.lower(), 1), else_=0)
            if translated_title is not None
            else literal(0)
        )
        stmt = stmt.order_by(exact_code.desc(), exact_translation.desc(), Course.title)
    else:
        stmt = stmt.order_by(Course.title)

    stmt = stmt.limit(limit).offset(offset)
    return list(db.scalars(stmt)), int(db.scalar(count_stmt) or 0)


def search_official(
    db: Session, query: str, *, limit: int = 10, offset: int = 0,
    category: str | None = None, strong_only: bool = False, campus: str | None = None,
) -> tuple[list[OfficialPage], int]:
    """Official pages matching ``query``; strict first, loose if strict finds nothing.

    ``strong_only`` keeps the pages that are *about* the query - it is in their
    title, summary or curated tags - and drops the ones that merely mention it
    somewhere in the body. The answer card uses it: "accounting" matched five
    pages because each of them says "your Monash account", and the card listed
    them as the official answer to a question about studying accounting.
    """
    if campus is None:
        # The campus is who is asking, not what about: "马莫怎么交学费" is a
        # question about paying fees, from Malaysia. Left in, 马来西亚 found
        # Malaysia's calendar pages for a question about campus transfer.
        named, query = campus_in_query(query or "")
        if named:
            found = _search_with_fallback(
                db, query, limit=limit, offset=offset, category=category,
                strong_only=strong_only, campus=named)
            if found[1]:
                return found
    return _search_with_fallback(db, query, limit=limit, offset=offset, category=category,
                                 strong_only=strong_only, campus=campus)


def _search_with_fallback(db: Session, query: str, **kwargs) -> tuple[list[OfficialPage], int]:
    found = _search_official(db, query, **kwargs)
    if found[1] == 0 and _is_multi_concept((query or "").strip()):
        return _search_official(db, query, strict=False, **kwargs)
    return found


# How students name a campus. Monash Malaysia is 马莫 to its students, after the
# way 澳莫 is Monash Australia; Sunway is the town it is in.
_CAMPUS_WORDS = {
    "malaysia": re.compile(
        r"马莫|大马|马来西亚(?:校区)?|马校|吉隆坡|双威|monash\s+malaysia|\bmalaysia(?:n)?\b|"
        r"\bmum\b|\bsunway\b", re.IGNORECASE),
    "australia": re.compile(
        r"澳莫|澳洲|澳大利亚|墨尔本|克莱顿|考菲尔德|\bclayton\b|\bcaulfield\b|\bmelbourne\b|"
        r"\baustralia(?:n)?\b", re.IGNORECASE),
}


# Things only one campus has. They point the search at that campus and stay in
# the query - they are what the question is about. A Malaysian student pass is
# not an Australian visa, and 学生准证续签 was answered with the visa page.
_CAMPUS_HINTS = {
    "malaysia": re.compile(r"学生准证|student pass|\bemgs\b|jompay|令吉|马币|\bringgit\b",
                           re.IGNORECASE),
    "australia": re.compile(r"\boshc\b|hecs|fee-help|\bcsp\b|centrelink|subclass 500",
                            re.IGNORECASE),
}


def campus_in_query(query: str) -> tuple[str | None, str]:
    """``(campus, rest)``: the campus the question names, and the question without it.

    One campus named narrows the search to that campus's pages and the ones for
    every campus. Both named - "转校区 马来西亚 澳洲" - narrow nothing, but the
    names still come out of the query. A query that is only a campus name is
    left alone: "马莫" by itself is a search for Monash Malaysia.
    """
    term = (query or "").strip()
    named = [campus for campus, words in _CAMPUS_WORDS.items() if words.search(term)]
    hinted = [campus for campus, words in _CAMPUS_HINTS.items() if words.search(term)]
    if not named:
        return (hinted[0] if len(hinted) == 1 else None), term
    rest = term
    for words in _CAMPUS_WORDS.values():
        rest = words.sub(" ", rest)
    rest = re.sub(r"\s+", " ", rest).strip(" ,，、?？的")
    if len(rest) < 2:
        return None, term
    named = list(dict.fromkeys(named + hinted))
    return (named[0] if len(named) == 1 else None), rest


#: The campuses a reader can narrow official pages to (OfficialPage.applies_to).
CAMPUSES = ("australia", "malaysia")


# Title and summary carry weights A and B in the search vector (see the model);
# body text is D. Ranking with D and C zeroed asks "is the query in the part of
# the page that says what the page is about".
HEADLINE_WEIGHTS = literal_column("ARRAY[0, 0, 1, 1]::float4[]")

# Trigram similarity against a title. 0.2 let "accounting" resemble "Academic
# records"; typo tolerance ("intermision") scores well above this.
TITLE_SIMILARITY = 0.3


_YEAR_IN_TITLE = r"((?:19|20)[0-9]{2})"


def _past_year_title():
    """1 for a page whose title names a year before this one ("Principal dates 2023"), else 0."""
    year = func.substring(OfficialPage.title, _YEAR_IN_TITLE)
    return case(
        (and_(year.isnot(None), cast(year, Integer) < date.today().year), 1),
        else_=0,
    )


def _search_official(
    db: Session, query: str, *, limit: int = 10, offset: int = 0, category: str | None = None,
    strict: bool = True, strong_only: bool = False, campus: str | None = None,
) -> tuple[list[OfficialPage], int]:
    stmt = select(OfficialPage).where(OfficialPage.status == "ok")
    count_stmt = select(func.count(OfficialPage.id)).where(OfficialPage.status == "ok")
    term = (query or "").strip()
    translated_title = (
        _translated_title(
            OfficialPage,
            OFFICIAL_PAGE_TRANSLATION,
            OfficialPage.slug,
            OfficialPage.title,
        )
        if has_cjk(term)
        else None
    )
    if term:
        ts_query = _ts_query(term, strict=strict)
        # A curated tag is English or Chinese; the question may be the other.
        # 抄袭 has to reach the page tagged "plagiarism", so the tags are also
        # tried against the English the question expands to.
        tag_hit = _array_contained_in_query(
            "official_pages.tags", term, tuple(expand(term)))
        title_like = func.similarity(OfficialPage.title, term) > TITLE_SIMILARITY
        headline = and_(
            OfficialPage.search_vector.op("@@")(ts_query),
            func.ts_rank(HEADLINE_WEIGHTS, OfficialPage.search_vector, ts_query) > 0,
        )
        strong = [tag_hit, title_like, headline]
        if translated_title is not None:
            strong.append(_contains(translated_title, term))
        matches = [OfficialPage.search_vector.op("@@")(ts_query), *strong]
        if translated_title is not None:
            matches.append(_zh_match(OfficialPage.search_zh, term))
        match = or_(*(strong if strong_only else matches))
        stmt = stmt.where(match)
        count_stmt = count_stmt.where(match)
    if category:
        stmt = stmt.where(OfficialPage.category == category)
        count_stmt = count_stmt.where(OfficialPage.category == category)
    if campus in CAMPUSES:
        # A page for every campus belongs to both lists; a page for the other
        # campus belongs to neither reader's.
        here = OfficialPage.applies_to.in_((campus, "all"))
        stmt = stmt.where(here)
        count_stmt = count_stmt.where(here)
    if term:
        zh_rank = (
            func.coalesce(func.similarity(OfficialPage.search_zh, term), 0)
            if has_cjk(term) else literal(0)
        )
        exact_translation = (
            case((translated_title == term, 1), else_=0)
            if translated_title is not None
            else literal(0)
        )
        # The whole query in the title: "student pass" is the Student Pass page
        # before "After Your Studies", which only talks about one.
        # A Chinese query is matched against the Chinese title: 学生签证 is in
        # 学生签证（Student Pass）, and not in "Peer Assisted Study Session (PASS)",
        # which an English expansion to "student pass" also reaches.
        if translated_title is not None:
            title_phrase = case((_contains(translated_title, term), 1), else_=0)
        elif len(term) >= 3:
            title_phrase = case(
                (func.lower(OfficialPage.title).contains(term.lower()), 1), else_=0)
        else:
            title_phrase = literal(0)
        stmt = stmt.order_by(
            exact_translation.desc(),
            # A page the query is about beats a page that mentions it.
            case((or_(*strong), 1), else_=0).desc(),
            # Then this year's pages before ones a past year names in their title:
            # 考试时间表 led with "Principal dates for Monash University Malaysia (2022)".
            _past_year_title().asc(),
            title_phrase.desc(),
            # Then the pages someone tagged with what was asked. Among the "about it"
            # pages a curated tag is the surest signal: 转专业 is a tag on the internal
            # course transfer pages, and without this a pharmacy page whose summary
            # happened to say "course" came first; 心理咨询 put one counsellor's
            # profile above the counselling service.
            case((tag_hit, 1), else_=0).desc(),
            func.ts_rank(HEADLINE_WEIGHTS, OfficialPage.search_vector, ts_query).desc(),
            func.ts_rank(OfficialPage.search_vector, ts_query).desc(),
            zh_rank.desc(),
            func.similarity(OfficialPage.title, term).desc(),
            OfficialPage.title,
        )
    else:
        stmt = stmt.order_by(OfficialPage.category, OfficialPage.title)
    stmt = stmt.limit(limit).offset(offset)
    return list(db.scalars(stmt)), int(db.scalar(count_stmt) or 0)


def _faq_questions(db: Session) -> dict[str, list[str]]:
    """Every published translation of every FAQ question, by slug.

    They are part of what the question may be asked with: a reader who clicks
    the Chinese question as a suggestion is asking exactly that question.
    """
    rows = db.execute(
        select(ContentTranslation.target_key, ContentTranslation.text).where(
            ContentTranslation.target_type == FAQ_ENTRY_TRANSLATION,
            ContentTranslation.field == "question",
            ContentTranslation.status == PUBLISHED,
            ContentTranslation.text.is_not(None),
        )
    ).all()
    found: dict[str, list[str]] = {}
    for slug, question in rows:
        found.setdefault(slug, []).append(question)
    return found


def match_faqs(
    db: Session, query: str, *, ignore: set[str] | None = None
) -> list[tuple[FaqEntry, faq_match.FaqMatch]]:
    """Curated answers triggered by ``query``, the ones that cover it first.

    See app/search/faq_match.py for what "triggered" and "cover" mean. The
    table is a few dozen hand-written rows, so it is read whole and matched in
    Python, where the rules can be read and tested.
    """
    term = (query or "").strip()
    if not term:
        return []
    entries = list(db.scalars(select(FaqEntry).options(selectinload(FaqEntry.official_page))))
    translated = _faq_questions(db)
    by_slug = {entry.slug: entry for entry in entries}
    candidates = [
        faq_match.FaqCandidate(
            slug=entry.slug,
            question=entry.question,
            keywords=tuple(entry.keywords or ()),
            tags=tuple(entry.tags or ()),
            priority=entry.priority or 0,
            translated_questions=tuple(translated.get(entry.slug, ())),
        )
        for entry in entries
    ]
    return [
        (by_slug[found.candidate.slug], found)
        for found in faq_match.match(term, candidates, ignore=ignore)
    ]


def search_faq(db: Session, query: str, *, limit: int = 5) -> list[FaqEntry]:
    """The FAQ group of unified search: answers first, then related questions.

    An empty query lists the curated set by priority, as the browse view does.
    """
    term = (query or "").strip()
    if not term:
        stmt = select(FaqEntry).order_by(FaqEntry.priority.desc(), FaqEntry.slug)
        return list(db.scalars(stmt.limit(limit)))
    return [entry for entry, _ in match_faqs(db, term)][:limit]


def search_community(
    db: Session, query: str, *, limit: int = 10, offset: int = 0, unit_code: str | None = None,
    category: str | None = None, unanswered: bool = False,
) -> tuple[list[CommunityPost], int]:
    stmt = select(CommunityPost).where(CommunityPost.is_hidden.is_(False))
    count_stmt = select(func.count(CommunityPost.id)).where(CommunityPost.is_hidden.is_(False))
    for condition in (
        CommunityPost.category == category if category else None,
        CommunityPost.answer_count == 0 if unanswered else None,
    ):
        if condition is not None:
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)
    term = (query or "").strip()
    codes = extract_unit_codes(term)
    if unit_code:
        stmt = stmt.where(CommunityPost.unit_code == unit_code.upper())
        count_stmt = count_stmt.where(CommunityPost.unit_code == unit_code.upper())
    elif term:
        def written(word: str):
            return or_(_contains(CommunityPost.title, word), _contains(CommunityPost.body, word))

        chinese: list = []
        if has_cjk(term):
            # Nothing to translate here - a post written in Chinese already is
            # Chinese, and the English tsvector simply cannot see it. The whole
            # query as typed, or every concept it names: 退课截止日期 should
            # find a post that says 退课 … 截止日期 with words in between.
            chinese.append(written(term))
            runs = [run for run, _ in concept_runs(term)]
            if runs:
                chinese.append(and_(*(written(run) for run in runs)))
        else:
            # And the other way: "withdraw" should find a post titled 退课.
            chinese.extend(written(run) for run in chinese_for(term))
        match = or_(
            CommunityPost.search_vector.op("@@")(_ts_query(term)),
            CommunityPost.unit_code.in_(codes) if codes else CommunityPost.id.is_(None),
            *chinese,
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
