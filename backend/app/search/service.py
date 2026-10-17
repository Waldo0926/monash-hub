"""Unified search over Handbook units and degrees, official pages, FAQ and posts.

PostgreSQL does all of this: ``tsvector`` for full text, ``pg_trgm`` for typo
tolerance on titles, and an exact-code shortcut in front of both because a
student typing ``FIT2102`` wants that unit first and nothing else.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from itertools import islice, product
from typing import Any

from sqlalchemy import (
    Integer,
    and_,
    case,
    cast,
    distinct,
    func,
    literal,
    literal_column,
    or_,
    select,
    text,
)
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
from app.search import english, faq_match, synonyms
from app.search.chinese import (
    chinese_for,
    concept_runs,
    concepts,
    expand,
    has_cjk,
    latin_part,
)
from app.search.keywords import extract_unit_codes
from app.search.normalise import fold


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
# what a sentence is not. It also has a digit: without one, "it" was a fragment
# of every FIT code and "sc" of every SCI and ASC one.
def _is_code_fragment(term: str) -> bool:
    return (term.isalnum() and term.isascii() and 2 <= len(term) <= 8
            and any(ch.isdigit() for ch in term))


def _is_code_prefix(term: str) -> bool:
    """Whether ``term`` can be how a unit code starts: "FIT", "fit20"."""
    return term.isalnum() and term.isascii() and 3 <= len(term) <= 8


def _websearch(text_: str, config: str = "english"):
    return func.websearch_to_tsquery(config, text_)


def _any_of(alternatives, config: str = "english") -> Any:
    query = None
    for alternative in alternatives:
        part = _websearch(alternative, config)
        query = part if query is None else query.op("||")(part)
    return query


def _with_variants(text_: str) -> list[str]:
    return [text_, *english.variants(text_)]


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

    English is ORed with its rewrites from ``app/search/english.py``: "drop a
    unit" is also "withdraw a unit".

    The raw term is always ORed in as well: a Chinese-only query contributes
    nothing to an English tsvector, but an English one is left exactly as it
    was.
    """
    groups = concepts(term)
    if not groups:
        return _any_of(_with_variants(term))
    latin = latin_part(term)
    parts = [_any_of(alternatives) for alternatives in groups]
    if latin:
        parts.append(_any_of(_with_variants(latin)))
    combined = parts[0]
    for part in parts[1:]:
        combined = combined.op("&&" if strict else "||")(part)
    return _websearch(term).op("||")(combined)


def _is_multi_concept(term: str) -> bool:
    """Whether strict and loose can give different answers for ``term``."""
    groups = concepts(term)
    return len(groups) + (1 if groups and latin_part(term) else 0) > 1


# Words a page title never needs to contain for the page to answer the
# question. The FAQ filler list plus the verbs of a request: "how to apply sc"
# is answered by "Extensions and special consideration".
_REQUEST_WORDS = frozenset({
    "apply", "applying", "application", "find", "check", "see", "view", "look",
})
_WORD = re.compile(r"[a-z0-9][a-z0-9+#'-]*")

# Phrasings past this add query time and no new titles.
MAX_PHRASINGS = 8


def _content_words(text_: str) -> list[str]:
    return [
        word for word in _WORD.findall(text_.lower())
        if word not in faq_match.EN_FILLER and word not in _REQUEST_WORDS
    ]


def _english_fallback(term: str) -> str | None:
    """``term`` without its filler, when that is a different query.

    websearch_to_tsquery drops English stop words, but not "still", "need" or
    "monash", so "can I still work on my visa" wanted "still" on the page.
    """
    if has_cjk(term):
        return None
    words = _content_words(term)
    # Only a query that lost a word: "_IT2102" is not "IT2102" with filler gone.
    return " ".join(words) if words and len(words) < len(_WORD.findall(term.lower())) else None


def _phrasings(term: str) -> list[str]:
    """``term`` in the words a Monash title would use, filler taken out.

    For English that is the query and its rewrites; for Chinese, the English
    each concept stands for, combined. These are matched word for word (the
    ``simple`` text config, no stemming): a page *called* "Databases" is a
    better answer to 数据库 than one whose title merely stems the same way,
    and "accounting" is not "IT Account".
    """
    groups = concepts(term)
    if groups:
        latin = latin_part(term)
        combined = (" ".join(parts) for parts in islice(product(*groups), MAX_PHRASINGS))
        raw = [f"{text_} {latin}".strip() for text_ in combined]
    else:
        raw = _with_variants(term)
    phrasings = (" ".join(_content_words(text_)) for text_ in raw)
    return list(dict.fromkeys(p for p in phrasings if p))[:MAX_PHRASINGS]


def _literal_query(term: str, *, prefix: bool = True, first_only: bool = False):
    """Any phrasing of ``term``, every word of it, each word as a prefix.

    With ``prefix=False`` each word has to be a whole word, or its plural.
    ``first_only`` keeps the phrasing closest to what was typed.

    A prefix and not a stem: "visa" still finds "visas" and "defer" finds
    "deferred", but "accounting" is not found in "IT Account" the way the
    English stemmer finds it. Built from letters and digits only, so nothing
    a reader types reaches ``to_tsquery`` as syntax.
    """
    clauses = []
    phrasings = _phrasings(term)
    for phrasing in phrasings[:1] if first_only else phrasings:
        words = re.findall(r"[a-z0-9]+", phrasing)
        if words:
            if prefix:
                parts = [f"{word}:*" for word in words]
            else:
                # Still let a plural through: "visa" is in "student visas".
                parts = [f"({word} | {word}s)" for word in words]
            clauses.append("(" + " & ".join(parts) + ")")
    return func.to_tsquery("simple", " | ".join(clauses)) if clauses else None


def _literal_match(column, query):
    return func.to_tsvector("simple", func.coalesce(column, "")).op("@@")(query)


def _literal(column, query):
    """1 when ``column`` has every word of one phrasing, unstemmed, else 0."""
    if query is None:
        return literal(0)
    return case((_literal_match(column, query), 1), else_=0)


def _title_is(column, term: str):
    """1 when the whole title is ``term``'s first phrasing: "Fees" for 学费.

    Only the first. The later alternatives are there for recall, and an exact
    title on one of them put two faculty pages called "Course transfer" above
    the university's "Course or campus transfer" for 转专业.
    """
    phrasings = _phrasings(term)
    if not phrasings:
        return literal(0)
    return case((func.lower(column).in_([phrasings[0], f"{phrasings[0]}s"]), 1), else_=0)


def _subject_only(term: str) -> bool:
    """Whether ``term`` names only subjects or degrees: 操作系统, 计算机科学学士.

    The official pages are about running a degree, not its content, and a
    stemmed match on them is mostly accidental - 编程入门 found "Mentor-Mentee
    Program" and 操作系统 found the eExam device specifications.
    """
    zh = [run for run, _ in concept_runs(term)]
    en = [phrase for phrase, _ in english.phrase_runs(term)]
    return bool(zh or en) and all(run in synonyms.ZH_FIELD_TERMS for run in zh) and not any(
        english.is_admin(phrase) for phrase in en)


def _unexplained(term: str) -> tuple[list[str], list[str]]:
    """What the synonym tables and the filler lists cannot account for.

    ``(cjk, latin)``: the Chinese runs and English words left once every
    known concept, phrase, campus name and question word is taken out.
    """
    _, rest = campus_in_query(term)
    text_ = rest.lower()
    for run, _ in concept_runs(text_):
        text_ = text_.replace(run, " ", 1)
    text_ = " ".join(text_.split())
    for _, (start, end) in sorted(english.phrase_runs(text_), key=lambda r: -r[1][0]):
        text_ = text_[:start] + " " + text_[end:]
    latin = [w for w in _content_words(text_)
             if not extract_unit_codes(w) and w not in _GENERIC_WORDS]
    cjk_text = re.sub(r"[ -~]+", " ", text_)
    for phrase in faq_match.ZH_FILLER_PHRASES:
        cjk_text = cjk_text.replace(phrase, " ")
    cjk = [run for run in cjk_text.split() if has_cjk(run)]
    return cjk, latin


# Words every Monash question uses. "drop a unit" is about withdrawing, not
# about units called anything.
_GENERIC_WORDS = frozenset({
    "unit", "units", "subject", "subjects", "class", "classes", "course", "courses",
    "semester", "take", "monash", "malaysia", "australia",
})

_DEGREE_EN = re.compile(
    r"(?<![a-z])(bachelors?|masters?|degrees?|undergrad(uate)?|postgrad(uate)?|phd|diploma|mba)"
    r"(?![a-z])")
_DEGREE_ZH = ("学士", "硕士", "本科", "研究生", "博士", "双学位", "文凭", "学位")


def _about_units(term: str) -> bool:
    """Whether a unit's title or overview can answer ``term``.

    Not when it names a degree - "bachelor of computer science" is a degree,
    and its words are in a hundred unit overviews. Not when it is only admin:
    学费, "how to enroll" and 毕业 are questions for the official pages, and
    they listed hundreds of units that mention fees, enrolment or graduates.
    A subject word, or anything the tables do not know, keeps units in.
    """
    text_ = term.lower()
    if _DEGREE_EN.search(text_) or any(word in term for word in _DEGREE_ZH):
        return False
    zh = [run for run, _ in concept_runs(term)]
    en = [phrase for phrase, _ in english.phrase_runs(term)]
    if not zh and not en:
        return True
    if any(run in synonyms.ZH_FIELD_TERMS for run in zh) or any(
            not english.is_admin(phrase) for phrase in en):
        return True
    cjk, latin = _unexplained(term)
    return bool(cjk or latin)


# Chinese has no word boundaries, so a student typing 学籍统计 is typing a
# contiguous run and means it. Substring is the honest query, and pg_trgm makes
# it an indexed one (from three characters; see _search_units for two).
def _like(term: str) -> str:
    """``term`` with LIKE's wildcards escaped, so "100%" is not "100 then anything"."""
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _contains(column, term: str):
    return column.ilike(f"%{_like(term)}%", escape="\\")


def _starts(column, term: str):
    return column.ilike(f"{_like(term)}%", escape="\\")


def _zh_match(column, term: str):
    """Match a Chinese query against a column holding translated text.

    This used to OR in ``similarity(column, term) > 0.3`` as well. Against a
    whole page of Chinese that is never true - a short query is a vanishing
    fraction of a long text's trigrams - and checked on the production
    snapshot it matched nothing the substring had not, for any query tried.
    It was also most of the cost of a Chinese unit search: computed over
    every unit, it took 0.9 of the 2.5 seconds 学费 spent there.
    """
    return _contains(column, term)


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
    query = fold(query)
    found = _search_units(db, query, year=year, **kwargs)
    if found[1] == 0 and _is_multi_concept(query):
        return _search_units(db, query, year=year, strict=False, **kwargs)
    if found[1] == 0 and (content := _english_fallback(query)):
        return _search_units(db, content, year=year, **kwargs)
    return found


Choice = str | list[str] | tuple[str, ...] | None

# The filters a unit list can be narrowed by, and the column each one reads.
# Campus and teaching period live on the offering; see _unit_filters.
UNIT_FACETS = ("campus", "teaching_period", "level", "prefix", "faculty", "school", "has_exam")


def _many(value: Choice) -> list[str]:
    """A filter value as a list: one string from an old link, several from the checkboxes."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    return [v for v in value if v]


@dataclass
class _UnitMatch:
    """What a text query matches, and what ranking it later needs."""

    where: Any
    term: str
    codes: list[str]
    ts_query: Any
    translated_title: Any


def _unit_match(query: str, *, strict: bool = True) -> _UnitMatch:
    codes = extract_unit_codes(query)
    # A campus is where the student is, not what the unit is about: 马莫 in
    # 马莫学费 matched 242 units whose overview says "Monash Malaysia".
    _, term = campus_in_query(query or "")
    translated_title = (
        _translated_title(Unit, UNIT_TRANSLATION, Unit.unit_code, Unit.title)
        if has_cjk(term)
        else None
    )
    about_units = bool(term) and _about_units(term)
    ts_query = _ts_query(term, strict=strict) if term else None

    where = None
    if term:
        matches = [Unit.unit_code.in_(codes)] if codes else [
            *([_starts(Unit.unit_code, term)] if _is_code_prefix(term) else []),
            *([_contains(Unit.unit_code, term)] if _is_code_fragment(term) else []),
        ]
        if about_units:
            matches.append(Unit.search_vector.op("@@")(ts_query))
            if not codes:
                matches.append(func.similarity(Unit.title, term) > 0.25)
            if translated_title is not None:
                matches.append(_contains(translated_title, term))
                # The translated overview. pg_trgm cannot index a pattern of
                # two characters, so 算法 or 学费 here is a sequential scan of
                # every unit's Chinese - 0.4 seconds, twice with the count.
                # A two-character word the synonym tables know is already
                # searched in English, so only an unknown one pays for it.
                if len(term) >= 3 or _unexplained(term)[0]:
                    matches.append(_zh_match(Unit.search_zh, term))
        where = or_(*matches) if matches else literal(False)
    return _UnitMatch(where, term, codes, ts_query, translated_title)


def _offering_filter(campus: list[str], teaching_period: list[str]):
    """Campus and teaching period, true of the same offering.

    Asked separately they are two EXISTS clauses, and a unit taught at Malaysia
    in first semester and at Clayton over the full year answered "Malaysia, full
    year" - a combination it is not taught in anywhere. On the small campuses
    that was most of the page: "Suzhou (SEU), second semester" listed 27 units
    of which 2 are actually offered there then, and "Clayton, October intake
    teaching period, Malaysia campus" listed 13 of which none are.
    """
    parts = []
    if campus:
        parts.append(UnitOffering.campus.in_(campus))
    if teaching_period:
        parts.append(UnitOffering.teaching_period.in_(teaching_period))
    return and_(*parts) if parts else None


def _unit_filters(
    *,
    campus: Choice = None,
    teaching_period: Choice = None,
    level: Choice = None,
    prefix: Choice = None,
    faculty: Choice = None,
    school: Choice = None,
    has_exam: bool | None = None,
) -> list:
    """WHERE clauses for the side filters. Several values in one filter mean any of them."""
    filters = []
    offering = _offering_filter(_many(campus), _many(teaching_period))
    if offering is not None:
        filters.append(Unit.offerings.any(offering))
    if levels := _many(level):
        filters.append(Unit.level.in_(levels))
    if prefixes := _many(prefix):
        filters.append(Unit.subject_prefix.in_([p.upper() for p in prefixes]))
    if faculties := _many(faculty):
        filters.append(Unit.faculty.in_(faculties))
    if schools := _many(school):
        filters.append(Unit.school.in_(schools))
    if has_exam is not None:
        filters.append(Unit.has_exam.is_(has_exam))
    return filters


def _search_units(
    db: Session,
    query: str,
    *,
    year: int,
    limit: int = 10,
    offset: int = 0,
    sort: str = "relevance",
    strict: bool = True,
    **filter_values,
) -> tuple[list[Unit], int]:
    stmt = select(Unit).where(Unit.academic_year == year, Unit.is_active.is_(True))
    count_stmt = select(func.count(Unit.id)).where(
        Unit.academic_year == year, Unit.is_active.is_(True)
    )

    match = _unit_match(query, strict=strict)
    term, codes, ts_query, translated_title = (
        match.term, match.codes, match.ts_query, match.translated_title
    )
    if match.where is not None:
        stmt = stmt.where(match.where)
        count_stmt = count_stmt.where(match.where)

    for condition in _unit_filters(**filter_values):
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
        rank = func.ts_rank(Unit.search_vector, ts_query)
        # Then the title, in decreasing order of how exactly it says what was
        # asked. "databases" listed "Spatial databases" above "Databases",
        # and "linear algebra" put the Honours computational unit first.
        phrasings = _phrasings(term)
        title_exact = (
            case((func.lower(Unit.title).in_(phrasings), 1), else_=0)
            if phrasings else literal(0)
        )
        title_starts = (
            case((or_(*(_starts(Unit.title, p) for p in phrasings)), 1), else_=0)
            if phrasings else literal(0)
        )
        title_literal = _literal(Unit.title, _literal_query(term))
        title_stemmed = case(
            (func.to_tsvector("english", Unit.title).op("@@")(ts_query), 1), else_=0)
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
        says_it = or_(translated_title_contains == 1, title_literal == 1)
        title_says_it = case((says_it, 1), else_=0)
        # Among the titles that say it, first year before honours: "psychology"
        # led with three PSY4xxx honours units and "data science" lost
        # FIT1043 Introduction to data science below the project units.
        # Research units are numbered 0xxx and go last. Everything else keeps
        # the same value so the text rank still decides.
        first_digit = func.substring(Unit.unit_code, "[0-9]")
        level = case((says_it, func.coalesce(func.nullif(first_digit, "0"), "9")), else_="0")
        stmt = stmt.order_by(
            exact.desc(), in_code.desc(), exact_translation.desc(), title_exact.desc(),
            title_says_it.desc(), level, title_starts.desc(), title_stemmed.desc(),
            rank.desc(), zh_rank.desc(), func.similarity(Unit.title, term).desc(),
            # Among equals the shorter title is the more general unit:
            # "Machine learning" before "Machine learning for finance".
            func.length(Unit.title), Unit.unit_code,
        )
    else:
        stmt = stmt.order_by(Unit.unit_code)

    stmt = stmt.options(
        selectinload(Unit.offerings),
        selectinload(Unit.assessments),
    ).limit(limit).offset(offset)

    return list(db.scalars(stmt)), int(db.scalar(count_stmt) or 0)


def unit_facets(
    db: Session, query: str, *, year: int, **filter_values
) -> dict[str, dict[str, int]]:
    """How many units each filter value would leave, given everything else chosen.

    Each filter is counted with every other filter applied but not itself, so
    ticking Clayton still shows how many units Malaysia would add. The text
    query falls back exactly as ``search_units`` does, so the numbers agree
    with the result list beside them.
    """
    query = fold(query)
    base = [Unit.academic_year == year, Unit.is_active.is_(True)]

    def total_for(match: _UnitMatch) -> int:
        conditions = [*base, *([match.where] if match.where is not None else [])]
        conditions += _unit_filters(**filter_values)
        return int(db.scalar(select(func.count(Unit.id)).where(*conditions)) or 0)

    match = _unit_match(query)
    if query and total_for(match) == 0:
        if _is_multi_concept(query):
            match = _unit_match(query, strict=False)
        elif content := _english_fallback(query):
            match = _unit_match(content)
    if match.where is not None:
        base.append(match.where)

    out: dict[str, dict[str, int]] = {}
    for facet in UNIT_FACETS:
        others = {k: v for k, v in filter_values.items() if k != facet}
        if facet in ("campus", "teaching_period"):
            # The other half of the offering pair has to hold on the same
            # offering row that is being counted, not on any offering.
            if facet == "campus":
                column = UnitOffering.campus
                same_row = _offering_filter([], _many(others.pop("teaching_period", None)))
            else:
                column = UnitOffering.teaching_period
                same_row = _offering_filter(_many(others.pop("campus", None)), [])
            conditions = [*base, *_unit_filters(**others), column.is_not(None)]
            if same_row is not None:
                conditions.append(same_row)
            stmt = (
                select(column, func.count(distinct(Unit.id)))
                .join(UnitOffering, UnitOffering.unit_id == Unit.id)
                .where(*conditions)
                .group_by(column)
            )
        else:
            column = {
                "level": Unit.level,
                "prefix": Unit.subject_prefix,
                "faculty": Unit.faculty,
                "school": Unit.school,
                "has_exam": Unit.has_exam,
            }[facet]
            stmt = (
                select(column, func.count(Unit.id))
                .where(*base, *_unit_filters(**others), column.is_not(None))
                .group_by(column)
            )
        out[facet] = {
            (str(value).lower() if isinstance(value, bool) else value): int(count)
            for value, count in db.execute(stmt)
        }
    return out


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
    query = fold(query)
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
            _starts(Course.abbreviated_name, term),
        ]
        # Two letters inside a title are not a search: "sc" was in every
        # Science degree.
        if len(term) >= 3:
            matches.append(_contains(Course.title, term))
        if translated_title is not None:
            matches.append(_contains(translated_title, term))
        # 商科学士 is "bachelor" and "commerce or business". Degree titles are
        # short and English, so every concept has to appear in the title. The
        # same goes for English typed in any order: "bachelor computer science"
        # is not a substring of "Bachelor of Computer Science", and found none.
        groups = _course_groups(term)
        title_words = and_(*(
            or_(*(_title_word(Course.title, alternative) for alternative in alternatives))
            for alternatives in groups
        )) if groups else None
        if title_words is not None:
            matches.append(title_words)
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
        # Alphabetical used to put "Bachelor of Business and Commerce and
        # Bachelor of Computer Science" first for "computer science". A single
        # degree is the likelier answer than a double, and the shortest title
        # is the degree itself rather than its Honours or Advanced variant.
        # With no level asked for, a bachelor comes before a graduate
        # certificate - most of the people searching are undergraduates.
        double = case((Course.title.ilike("% and bachelor of %"), 1),
                      (Course.title.ilike("% and master of %"), 1), else_=0)
        level_named = _DEGREE_EN.search(term.lower()) or any(w in term for w in _DEGREE_ZH)
        undergraduate = (
            literal(0) if level_named
            # A vertical double (BMedSc and MD) is entered from school too.
            else case((Course.course_type.ilike("UG%"), 0),
                      (Course.course_type == "Vertical double", 0), else_=1)
        )
        # "bcom" is BCom before it is the start of BCompSci.
        abbreviation = case(
            (func.lower(Course.abbreviated_name) == term.lower(), 1),
            (func.lower(Course.abbreviated_name).startswith(term.lower() + "("), 1),
            else_=0)
        # The words as a phrase, then each at the start of a word: "medicine"
        # is Doctor of Medicine before it is the end of Paramedicine, and "MBA"
        # is Master of Business Administration before Business Analytics.
        # The query or its first rewrite beats a later one: "MBA" is Master of
        # Business Administration before Bachelor of Business Administration.
        phrases = [p for p in _with_variants(term) if len(p) >= 3]
        first = [p for p in [term.lower(), *english.variants(term)[:1]] if len(p) >= 3]
        whens = [(or_(*(_title_word(Course.title, p) for p in group)), weight)
                 for group, weight in ((first, 2), (phrases, 1)) if group]
        phrase = case(*whens, else_=0) if whens and not has_cjk(term) else literal(0)
        words = case((title_words, 1), else_=0) if title_words is not None else literal(0)
        stmt = stmt.order_by(
            exact_code.desc(), exact_translation.desc(), abbreviation.desc(), phrase.desc(),
            words.desc(), double, undergraduate, func.length(Course.title), Course.title,
        )
    else:
        stmt = stmt.order_by(Course.title)

    stmt = stmt.limit(limit).offset(offset)
    return list(db.scalars(stmt)), int(db.scalar(count_stmt) or 0)


# "honours" and "double degree" are not here: they narrow the list to a kind
# of degree, where "bachelor" alone is half the Handbook.
_LEVEL_WORDS = frozenset({
    "bachelor", "bachelors", "master", "masters", "graduate", "postgraduate", "diploma",
    "certificate", "doctor", "undergraduate",
})

# Words that say "a degree" without saying which. They are not in any title.
_COURSE_FILLER = frozenset({
    "degree", "degrees", "course", "courses", "program", "programs", "programme",
    "programmes", "study", "studies", "studying", "major", "majors",
})


def _course_groups(term: str) -> list[tuple[str, ...]]:
    """What a degree title has to contain for ``term``, as groups of alternatives.

    Chinese concepts as before; English word by word, each word or the
    abbreviation it stands for ("IT" is information technology).
    """
    groups = list(concepts(term))
    latin = latin_part(term) if has_cjk(term) else term
    if not latin:
        return groups
    runs = sorted(english.phrase_runs(latin), key=lambda run: run[1][0])
    text_ = fold(latin).lower()
    last = 0
    for phrase, (start, end) in runs:
        groups.extend((word,) for word in _content_words(text_[last:start])
                      if word not in _COURSE_FILLER)
        groups.append(english.EN_TERMS[phrase])
        last = end
    groups.extend((word,) for word in _content_words(text_[last:])
                  if word not in _COURSE_FILLER)
    # A level alone is every degree at that level: "apply to graduate" is not
    # a search for the Graduate Diplomas.
    if all(set(alternatives) <= _LEVEL_WORDS for alternatives in groups):
        return []
    return groups


def _title_word(column, phrase: str):
    """``phrase`` in ``column`` starting at a word: "IT" is not inside "Architecture"."""
    return column.op("~*")(r"\m" + re.escape(phrase))


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
    query = fold(query)
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
    if found[1] == 0 and (content := _english_fallback(query or "")):
        return _search_official(db, content, **kwargs)
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
            "official_pages.tags", term, (*expand(term), *english.alternatives(term)))
        title_like = func.similarity(OfficialPage.title, term) > TITLE_SIMILARITY
        headline = and_(
            OfficialPage.search_vector.op("@@")(ts_query),
            func.ts_rank(HEADLINE_WEIGHTS, OfficialPage.search_vector, ts_query) > 0,
        )
        literal_query = _literal_query(term)
        if _subject_only(term) and literal_query is not None:
            # A tag like 毕业 sits inside 毕业设计, so tags are no help here.
            strong = [title_like, _literal_match(
                func.concat_ws(" ", OfficialPage.title, OfficialPage.summary), literal_query)]
        else:
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
        # Every word of the question, as Monash would write it, in the title -
        # unstemmed, so "accounting" does not count "IT Account" as a match.
        # "supp exam" is answered by "Supplementary assessments", and before
        # this the eExam pages came first because each says "exam" twice.
        title_literal = _literal(OfficialPage.title, literal_query)
        # Whole words before prefixes, and the words as typed before the
        # rewrites: "pay fees" is "Pay your fees" before "Fees non-payment",
        # where "pay" is only the start of "payment".
        # A Chinese query has no typed English, its first phrasing is just
        # the first alternative in the table.
        title_typed = literal(0) if has_cjk(term) else _literal(
            OfficialPage.title, _literal_query(term, prefix=False, first_only=True))
        title_words = _literal(OfficialPage.title, _literal_query(term, prefix=False))
        summary_literal = _literal(
            func.concat_ws(" ", OfficialPage.title, OfficialPage.summary), literal_query)
        stmt = stmt.order_by(
            exact_translation.desc(),
            # A page called what was asked: "Graduations" for 毕业, "Fees" for 学费.
            _title_is(OfficialPage.title, term).desc(),
            # A page the query is about beats a page that mentions it.
            case((or_(*strong), 1), else_=0).desc(),
            # Then this year's pages before ones a past year names in their title:
            # 考试时间表 led with "Principal dates for Monash University Malaysia (2022)".
            _past_year_title().asc(),
            title_phrase.desc(),
            title_typed.desc(),
            title_words.desc(),
            title_literal.desc(),
            # Then the pages someone tagged with what was asked. Among the "about it"
            # pages a curated tag is the surest signal: 转专业 is a tag on the internal
            # course transfer pages, and without this a pharmacy page whose summary
            # happened to say "course" came first; 心理咨询 put one counsellor's
            # profile above the counselling service.
            case((tag_hit, 1), else_=0).desc(),
            summary_literal.desc(),
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
    term = fold(query)
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
    term = fold(query)
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
    term = fold(query)
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
