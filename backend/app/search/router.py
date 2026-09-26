"""The zero-AI question router.

A question goes through four deterministic stages:

    unit code?  ->  intent?  ->  Handbook field  ->  official FAQ / page  ->  community

Every answer it produces is a rendering of a stored field with a link back to
the source. Nothing is generated, which is why the answers can be checked - and
why the product works with no LLM budget at all.

**Language.** The sentences this module writes around the data ("The 2026
Handbook lists an examination") are interface text, so each one carries a
``key`` and ``params`` the frontend looks up in ``frontend/i18n``; the English
``text`` stays alongside as the fallback for any client that does not. The data
itself - Handbook values, official page text - is never rewritten here; a
curated FAQ is answered in the reader's language only where a person or a
labelled machine translation of it is stored.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import exists, select
from sqlalchemy.orm import Session, selectinload

from app.knowledge import translations
from app.models.handbook import Unit
from app.models.translation import FAQ_ENTRY
from app.search import service
from app.search.keywords import (
    UNIT_CODE_RE,
    classify_intent,
    extract_unit_codes,
    is_subjective,
)

# Students name campuses in either language, and a Chinese question about the
# Malaysia offering has to reach the same answer as the English one.
CAMPUS_ALIASES: dict[str, tuple[str, ...]] = {
    "Malaysia": ("malaysia", "马来西亚", "马校", "大马", "マレーシア", "말레이시아"),
    "Clayton": ("clayton", "克莱顿", "クレイトン", "클레이턴", "클레이튼"),
    "Caulfield": ("caulfield", "考菲尔德"),
    "Peninsula": ("peninsula",),
    "Parkville": ("parkville",),
    "Suzhou": ("suzhou", "苏州"),
}

MOODLE_CAVEAT = (
    "Teaching-period detail can still change - confirm against Moodle or the unit "
    "teaching team before you rely on it."
)
OFFICIAL_CAVEAT = "Always confirm deadlines and eligibility on the official Monash page."


def _say(key: str, text: str, **params: Any) -> dict[str, Any]:
    """A sentence of ours: the key the interface translates, and the English."""
    return {"key": f"answer.{key}", "params": params, "text": text}


def _verdict(key: str, text: str, **params: Any) -> dict[str, Any]:
    return {"type": "verdict", **_say(key, text, **params)}


def _title(key: str, text: str, **params: Any) -> dict[str, Any]:
    return {"title": text, "title_key": f"answer.{key}", "title_params": params}


def _load_unit(db: Session, code: str, year: int) -> Unit | None:
    return db.scalar(
        select(Unit)
        .where(Unit.unit_code == code.upper(), Unit.academic_year == year)
        .options(
            selectinload(Unit.offerings),
            selectinload(Unit.assessments),
            selectinload(Unit.requisite_groups),
            selectinload(Unit.learning_outcomes),
            selectinload(Unit.activities),
        )
    )


def _unit_source(unit: Unit) -> dict[str, Any]:
    return {
        "kind": "handbook",
        "label": f"Monash Handbook {unit.academic_year}",
        "url": unit.source_url,
        "last_checked": unit.last_crawled.isoformat() if unit.last_crawled else None,
    }


def _assessment_answer(unit: Unit) -> dict[str, Any]:
    rows = [
        {
            "number": item.number,
            "name": item.name,
            "type": item.assessment_type,
            "weight": f"{item.weight}%" if item.weight else None,
            "hurdle": item.hurdle,
        }
        for item in unit.assessments
    ]
    total = sum(
        int(item.weight) for item in unit.assessments if (item.weight or "").isdigit()
    )

    year = unit.academic_year
    # The year is the unit's, not a constant: this used to say "The 2026
    # Handbook" whatever year had been asked about.
    if unit.has_exam is True:
        verdict = _verdict(
            "assessment.hasExam",
            f"The {year} Handbook lists an examination for this unit.", year=year)
    elif unit.has_exam is False:
        verdict = _verdict(
            "assessment.noExam",
            f"The {year} Handbook does not list a final examination among the assessment "
            "items. That is not the same as a guarantee there is none.", year=year)
    else:
        verdict = _verdict(
            "assessment.unknown",
            f"The {year} Handbook does not publish assessment items for this unit yet.",
            year=year)

    blocks: list[dict[str, Any]] = [verdict]
    if rows:
        blocks.append(
            {
                "type": "table",
                "columns": ["#", "Assessment", "Type", "Weight", "Hurdle"],
                "column_keys": ["answer.col.number", "answer.col.assessment",
                                "answer.col.type", "answer.col.weight", "answer.col.hurdle"],
                "keys": ["number", "name", "type", "weight", "hurdle"],
                # How the frontend translates each cell: a Handbook closed-list
                # value is looked up, anything else is shown as published.
                "terms": {"name": "assessmentName", "type": "assessmentType",
                          "hurdle": "hurdle"},
                "rows": rows,
                "caption": f"{len(rows)} items, {total}% total" if total else None,
                "caption_key": "answer.assessment.caption" if total else None,
                "caption_params": {"count": len(rows), "total": total} if total else None,
            }
        )
    if unit.assessment_summary:
        blocks.append(
            {"type": "text", "title": "Handbook summary",
             "title_key": "answer.assessment.summary", "text": unit.assessment_summary}
        )

    return {
        "answer_type": "handbook_assessment",
        **_title("assessment.title", f"{unit.unit_code} · Assessment ({year} Handbook)",
                 code=unit.unit_code, year=year),
        "blocks": blocks,
        "caveat": MOODLE_CAVEAT,
        "caveat_key": "answer.caveat.moodle",
    }


def _requisite_answer(unit: Unit) -> dict[str, Any]:
    by_type: dict[str, list[dict[str, Any]]] = {}
    for group in unit.requisite_groups:
        by_type.setdefault(group.requisite_type, []).append(
            {
                "connector": group.connector,
                "description": group.description,
                "items": [
                    {"code": item.item_code, "name": item.item_name, "url": item.item_url}
                    for item in group.items
                ],
            }
        )

    year = unit.academic_year
    if not by_type:
        blocks = [_verdict(
            "requisite.none",
            f"The {year} Handbook lists no prerequisite, corequisite or prohibition "
            "for this unit.", year=year)]
    else:
        blocks = [_verdict(
            "requisite.intro",
            f"Requisites as published in the {year} Handbook. Units inside one group "
            "are joined by the group's connector.", year=year)]
        for req_type, groups in by_type.items():
            blocks.append({"type": "requisite_group", "requisite_type": req_type, "groups": groups})

    return {
        "answer_type": "handbook_requisite",
        **_title("requisite.title", f"{unit.unit_code} · Requisites ({year} Handbook)",
                 code=unit.unit_code, year=year),
        "blocks": blocks,
        "caveat": None,
    }


def _offering_answer(unit: Unit, query: str) -> dict[str, Any]:
    offerings = [
        {
            "campus": o.campus,
            "teaching_period": o.teaching_period,
            "attendance_mode": o.attendance_mode,
            "offering_code": o.display_name or o.offering_code,
        }
        for o in unit.offerings
        if o.offered
    ]
    lowered = (query or "").lower()
    focus = next(
        (campus for campus, aliases in CAMPUS_ALIASES.items()
         if any(alias in lowered for alias in aliases)),
        None,
    )
    code, year = unit.unit_code, unit.academic_year
    if focus:
        # "Malaysia" asks about every offering on that campus; the Handbook
        # also lists "Malaysia (Other)" and the like, which are the same place.
        matching = [
            o for o in offerings
            if (o["campus"] or "").lower() == focus.lower()
            or (o["campus"] or "").lower().startswith(f"{focus.lower()} (")
        ]
        if matching:
            n = len(matching)
            verdict = _verdict(
                "offering.yesOne" if n == 1 else "offering.yes",
                f"Yes - {code} has {n} published {focus} offering{'s' if n != 1 else ''} "
                f"in {year}.", code=code, count=n, campus=focus, year=year)
            verdict["terms"] = {"campus": "campus"}
        else:
            verdict = _verdict(
                "offering.noneAt",
                f"The {year} Handbook publishes no {focus} offering for {code}.",
                code=code, campus=focus, year=year)
            verdict["terms"] = {"campus": "campus"}
    elif offerings:
        n = len(offerings)
        verdict = _verdict(
            "offering.countOne" if n == 1 else "offering.count",
            f"{code} has {n} published offering{'s' if n != 1 else ''} in {year}.",
            code=code, count=n, year=year)
    else:
        verdict = _verdict(
            "offering.none", f"The {year} Handbook publishes no offerings for {code}.",
            code=code, year=year)

    blocks: list[dict[str, Any]] = [verdict]
    if offerings:
        blocks.append(
            {
                "type": "table",
                "columns": ["Campus", "Teaching period", "Mode", "Offering"],
                "column_keys": ["answer.col.campus", "answer.col.period",
                                "answer.col.mode", "answer.col.offering"],
                "keys": ["campus", "teaching_period", "attendance_mode", "offering_code"],
                "terms": {"campus": "campus", "teaching_period": "period",
                          "attendance_mode": "mode"},
                "rows": offerings,
                "caption": None,
            }
        )
    return {
        "answer_type": "handbook_offering",
        **_title("offering.title", f"{code} · Offerings ({year} Handbook)",
                 code=code, year=year),
        "blocks": blocks,
        "caveat": MOODLE_CAVEAT,
        "caveat_key": "answer.caveat.moodle",
    }


def _workload_answer(unit: Unit) -> dict[str, Any]:
    blocks: list[dict[str, Any]] = []
    if unit.workload_requirements:
        blocks.append(
            {
                "type": "text",
                "title": "Workload requirements",
                "title_key": "answer.workload.requirements",
                "text": unit.workload_requirements,
            }
        )
    if unit.activities:
        blocks.append(
            {
                "type": "table",
                "columns": ["Activity", "Duration"],
                "column_keys": ["answer.col.activity", "answer.col.duration"],
                "keys": ["activity_type", "name"],
                "terms": {"activity_type": "activityType"},
                "rows": [
                    {"activity_type": a.activity_type, "name": a.name} for a in unit.activities
                ],
                "caption": None,
            }
        )
    if not blocks:
        blocks.append(_verdict(
            "workload.none", "The Handbook publishes no workload detail for this unit."))
    return {
        "answer_type": "handbook_workload",
        **_title("workload.title",
                 f"{unit.unit_code} · Workload ({unit.academic_year} Handbook)",
                 code=unit.unit_code, year=unit.academic_year),
        "blocks": blocks,
        "caveat": None,
    }


def _outcomes_answer(unit: Unit) -> dict[str, Any]:
    items = [
        {"code": o.code, "text": o.description}
        for o in unit.learning_outcomes
        if o.description
    ]
    blocks = (
        [{"type": "list", "title": "Unit learning outcomes",
          "title_key": "answer.outcomes.list", "items": items}]
        if items
        else [_verdict("outcomes.none", "The Handbook publishes no learning outcomes yet.")]
    )
    return {
        "answer_type": "handbook_outcomes",
        **_title("outcomes.title",
                 f"{unit.unit_code} · Learning outcomes ({unit.academic_year} Handbook)",
                 code=unit.unit_code, year=unit.academic_year),
        "blocks": blocks,
        "caveat": None,
    }


HANDBOOK_ANSWERS = {
    "assessment": lambda unit, query: _assessment_answer(unit),
    "requisite": lambda unit, query: _requisite_answer(unit),
    "offering": _offering_answer,
    "workload": lambda unit, query: _workload_answer(unit),
    "outcomes": lambda unit, query: _outcomes_answer(unit),
}


def _unit_title(db: Session, unit, locale: str | None) -> str:
    """The unit's name in the reader's language, if we have one.

    The rest of this module answers in English, which is its own problem. This
    one line is the whole visible answer when somebody types a unit code, so it
    is worth reading in the language the page is in.
    """
    if not locale or locale == "en":
        return unit.title
    from app.knowledge import translations
    from app.models.translation import UNIT

    tr = translations.load(db, locale, UNIT, unit.unit_code, source_hash=unit.content_hash)
    return tr.field("title", unit.title) or unit.title


def _known_prefix(db: Session, code: str, year: int) -> bool:
    """Whether ``code`` looks like a real unit code rather than "year 2026".

    The code pattern is three or four letters and four digits, which "wam 2025"
    and "year 2026" also are. A prefix the Handbook actually uses is the
    difference.
    """
    prefix = UNIT_CODE_RE.match(code)
    if not prefix:
        return False
    return bool(db.scalar(select(exists().where(
        Unit.subject_prefix == prefix.group(1).upper(), Unit.academic_year == year,
    ))))


def _faq_answer(db: Session, entry, locale: str | None) -> dict[str, Any]:
    """A curated FAQ as the answer, in the reader's language where one is stored."""
    tr = translations.load(db, locale, FAQ_ENTRY, entry.slug, global_key=None)
    page = entry.official_page
    return {
        "answer_type": "official_faq",
        "faq_slug": entry.slug,
        "title": tr.field("question", entry.question) or entry.question,
        "blocks": [{"type": "text", "title": None,
                    "text": tr.field("answer", entry.answer) or entry.answer}],
        # Marked like every other translated source: unofficial, and whether a
        # person or a machine wrote it.
        "translation": tr.meta(),
        "applies_to": page.applies_to if page else None,
        "caveat": OFFICIAL_CAVEAT,
        "caveat_key": "answer.caveat.official",
        "sources": [
            {
                "kind": "official",
                "label": page.title if page else "Monash University",
                "url": entry.official_url or (page.canonical_url if page else None),
                "last_checked": page.last_checked.isoformat()
                if page and page.last_checked else None,
            }
        ],
    }


def _faq_questions(db: Session, entries, locale: str | None) -> list[str]:
    """FAQ questions as suggestion chips, in the reader's language."""
    if not entries:
        return []
    trs = translations.load_many(
        db, locale, FAQ_ENTRY, [e.slug for e in entries], global_key=None)
    return [trs[e.slug].field("question", e.question) or e.question for e in entries]


def _official_answer(pages, total: int) -> dict[str, Any]:
    return {
        "answer_type": "official_search",
        **_title("official.title", "Official Monash pages matching your question"),
        "blocks": [
            {
                "type": "page_list",
                "items": [
                    {
                        "slug": p.slug,
                        "title": p.title,
                        "summary": p.summary,
                        "url": p.canonical_url,
                        "category": p.category,
                        "applies_to": p.applies_to,
                        "last_checked": p.last_checked.isoformat()
                        if p.last_checked
                        else None,
                    }
                    for p in pages
                ],
            }
        ],
        "caveat": None,
    }


def _localise_pages(db: Session, payload: dict[str, Any], locale: str | None) -> None:
    """Page titles and summaries in the page list, where a translation is stored."""
    from app.models.translation import OFFICIAL_PAGE

    for block in payload.get("blocks", []):
        if block.get("type") != "page_list":
            continue
        slugs = [item["slug"] for item in block["items"]]
        trs = translations.load_many(db, locale, OFFICIAL_PAGE, slugs, global_key=None)
        for item in block["items"]:
            tr = trs[item["slug"]]
            item["title"] = tr.field("title", item["title"]) or item["title"]
            item["summary"] = tr.string(item["summary"]) if item["summary"] else None
            item["translation"] = tr.meta()


def answer(db: Session, query: str, *, year: int, locale: str | None = None) -> dict[str, Any]:
    """Route one question. Always returns a payload - never raises on a miss."""
    query = (query or "").strip()
    codes = extract_unit_codes(query)
    intent, matched = classify_intent(query)
    subjective = is_subjective(query)

    base: dict[str, Any] = {
        "query": query,
        "intent": intent,
        "matched_keywords": matched,
        "unit_code": codes[0] if codes else None,
        "sources": [],
        "related_community": [],
        "suggestions": [],
        "fallback": None,
    }

    unit = _load_unit(db, codes[0], year) if codes else None

    # A subjective question about a real unit gets the published workload plus
    # community threads - never a fabricated difficulty rating.
    if unit is not None and subjective:
        posts, _ = service.search_community(db, query, unit_code=unit.unit_code, limit=5)
        payload = _workload_answer(unit)
        payload["answer_type"] = "subjective"
        payload.update(_title(
            "subjective.title", f"{unit.unit_code} · What the Handbook publishes",
            code=unit.unit_code))
        payload["blocks"].insert(0, _verdict(
            "subjective.verdict",
            "This is a matter of opinion, so there is no official answer. "
            "Here is the published workload, and what students have said."))
        base.update(payload)
        base["sources"] = [_unit_source(unit)]
        base["related_community"] = [_post_brief(p) for p in posts]
        base["suggestions"] = _unit_suggestions(unit.unit_code, locale)
        return base

    if unit is not None and intent in HANDBOOK_ANSWERS:
        base.update(HANDBOOK_ANSWERS[intent](unit, query))
        base["sources"] = [_unit_source(unit)]
        posts, _ = service.search_community(db, query, unit_code=unit.unit_code, limit=3)
        base["related_community"] = [_post_brief(p) for p in posts]
        base["suggestions"] = _unit_suggestions(unit.unit_code, locale)
        return base

    # The unit code is the router's business; it must not count against a FAQ
    # as something the FAQ fails to cover. "FIT2004 怎么退课" is a question
    # about withdrawing, asked by someone who named the unit.
    ignore = {c.lower() for c in codes}
    for code in codes:
        found = UNIT_CODE_RE.match(code)
        if found:
            ignore.update({found.group(1).lower(), found.group(2)})
    faqs = service.match_faqs(db, query, ignore=ignore)
    confident = [entry for entry, found in faqs if found.confident]
    related = [entry for entry, found in faqs if not found.confident]

    if unit is not None and confident:
        top = confident[0]
        base.update(_faq_answer(db, top, locale))
        base["blocks"].append(
            {"type": "link", "to": f"/units/{unit.unit_code}", "label": unit.unit_code})
        base["suggestions"] = _faq_questions(db, [*confident[1:], *related][:3], locale)
        return base

    if unit is not None:
        # We know the unit but not what was being asked about it.
        #
        # This used to answer with the whole overview. On a phone that is the
        # entire first screen, so a reader searching a unit code met a wall of
        # prose and never scrolled to the unit itself. A code is a request for
        # the unit, not for an essay about it: the facts fit in four rows, and
        # the link is the thing they came for.
        base.update(
            {
                "answer_type": "handbook_overview",
                "title": f"{unit.unit_code} · {_unit_title(db, unit, locale)}",
                # Just the way in. A table of facts was the first thing tried
                # and it filled a phone screen too, which put the link back
                # below the fold - and this whole path exists because the
                # reader typed a code, which is a request for the unit.
                "blocks": [
                    {
                        "type": "link",
                        "to": f"/units/{unit.unit_code}",
                        "label": unit.unit_code,
                    }
                ],
                "caveat": None,
            }
        )
        base["sources"] = [_unit_source(unit)]
        base["suggestions"] = _unit_suggestions(unit.unit_code, locale)
        return base

    # A real-looking code the Handbook does not have this year. Saying so beats
    # answering a question about ABC1234 with pages about something else.
    if codes and _known_prefix(db, codes[0], year):
        base.update(
            {
                "answer_type": "unit_not_found",
                **_title("unitNotFound.title", f"{codes[0]} is not in the {year} Handbook",
                         code=codes[0], year=year),
                "blocks": [_verdict(
                    "unitNotFound.verdict",
                    f"There is no unit {codes[0]} in the {year} Handbook. Check the code, "
                    "or search by the unit's name.", code=codes[0], year=year)],
                "caveat": None,
            }
        )
        base["fallback"] = {"ask_community": True}
        return base

    # No unit code: the curated FAQ, when one genuinely covers the question.
    if confident:
        top = confident[0]
        base.update(_faq_answer(db, top, locale))
        base["suggestions"] = _faq_questions(db, [*confident[1:], *related][:3], locale)
        return base

    # Otherwise the official pages that are *about* the question - not every
    # page that mentions one of its words somewhere in the body. A FAQ that was
    # triggered but does not cover the question is offered, honestly, as a
    # related question rather than drawn as the answer.
    pages, total = service.search_official(db, query, limit=5, strong_only=True)
    if pages:
        base.update(_official_answer(pages, total))
        _localise_pages(db, base, locale)
        base["suggestions"] = _faq_questions(db, related[:3], locale)
        base["fallback"] = {"total_official": total, "ask_community": True}
        return base

    posts, _ = service.search_community(db, query, limit=5)
    base.update(
        {
            "answer_type": "community_fallback",
            **_title("fallback.title", "No official answer indexed for this yet"),
            "blocks": [_verdict(
                "fallback.verdict",
                "Nothing in the Handbook or the indexed official pages answers this. "
                "Try different keywords, or ask the community.")],
            "caveat": None,
        }
    )
    base["related_community"] = [_post_brief(p) for p in posts]
    base["suggestions"] = _faq_questions(db, related[:3], locale)
    base["fallback"] = {"ask_community": True}
    return base


def _post_brief(post) -> dict[str, Any]:
    return {
        "id": post.id,
        "title": post.title,
        "answer_count": post.answer_count,
        "is_solved": post.is_solved,
        "unit_code": post.unit_code,
        "updated_at": post.updated_at.isoformat() if post.updated_at else None,
    }


def _unit_suggestions(code: str, locale: str | None = None) -> list[str]:
    """Follow-up questions, phrased so this router can answer them.

    They are questions the reader clicks and we then have to route, so each
    one uses a word ``INTENT_KEYWORDS`` knows in that language - the tests ask
    every one of them back.
    """
    if locale == "ja":
        return [
            f"{code} に期末試験はありますか？",
            f"{code} の履修条件は何ですか？",
            f"{code} はマレーシアで開講されますか？",
            f"{code} の学習時間はどのくらいですか？",
        ]
    if locale == "ko":
        return [
            f"{code}에 기말시험이 있나요?",
            f"{code}의 선수과목은 무엇인가요?",
            f"{code}는 말레이시아에서 개설되나요?",
            f"{code}의 학습량은 어느 정도인가요?",
        ]
    if locale == "zh":
        return [
            f"{code} 有期末考试吗？",
            f"{code} 的先修课是什么？",
            f"{code} 在马来西亚开课吗？",
            f"{code} 的工作量是多少？",
        ]
    return [
        f"Does {code} have a final exam?",
        f"What are the prerequisites for {code}?",
        f"Is {code} offered in Malaysia?",
        f"What is the workload for {code}?",
    ]
