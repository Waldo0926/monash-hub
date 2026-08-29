"""The zero-AI question router.

A question goes through four deterministic stages:

    unit code?  ->  intent?  ->  Handbook field  ->  official FAQ / page  ->  community

Every answer it produces is a rendering of a stored field with a link back to
the source. Nothing is generated, which is why the answers can be checked - and
why the product works with no LLM budget at all.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.handbook import Unit
from app.search import service
from app.search.keywords import classify_intent, extract_unit_codes, is_subjective

# Students name campuses in either language, and a Chinese question about the
# Malaysia offering has to reach the same answer as the English one.
CAMPUS_ALIASES: dict[str, tuple[str, ...]] = {
    "Malaysia": ("malaysia", "马来西亚", "马校", "大马"),
    "Clayton": ("clayton", "克莱顿"),
    "Caulfield": ("caulfield", "考菲尔德"),
    "Peninsula": ("peninsula",),
    "Parkville": ("parkville",),
    "Suzhou": ("suzhou", "苏州"),
}

MOODLE_CAVEAT = (
    "Teaching-period detail can still change - confirm against Moodle or the unit "
    "teaching team before you rely on it."
)


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

    if unit.has_exam is True:
        verdict = "The 2026 Handbook lists an examination for this unit."
    elif unit.has_exam is False:
        verdict = (
            "The 2026 Handbook does not list a final examination among the assessment items. "
            "That is not the same as a guarantee there is none."
        )
    else:
        verdict = "The 2026 Handbook does not publish assessment items for this unit yet."

    blocks: list[dict[str, Any]] = [{"type": "verdict", "text": verdict}]
    if rows:
        blocks.append(
            {
                "type": "table",
                "columns": ["#", "Assessment", "Type", "Weight", "Hurdle"],
                "keys": ["number", "name", "type", "weight", "hurdle"],
                "rows": rows,
                "caption": f"{len(rows)} items, {total}% total" if total else None,
            }
        )
    if unit.assessment_summary:
        blocks.append(
            {"type": "text", "title": "Handbook summary", "text": unit.assessment_summary}
        )

    return {
        "answer_type": "handbook_assessment",
        "title": f"{unit.unit_code} · Assessment ({unit.academic_year} Handbook)",
        "blocks": blocks,
        "caveat": MOODLE_CAVEAT,
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

    if not by_type:
        blocks = [
            {
                "type": "verdict",
                "text": "The 2026 Handbook lists no prerequisite, corequisite or prohibition "
                "for this unit.",
            }
        ]
    else:
        blocks = [
            {
                "type": "verdict",
                "text": "Requisites as published in the 2026 Handbook. Units inside one group "
                "are joined by the group's connector.",
            }
        ]
        for req_type, groups in by_type.items():
            blocks.append({"type": "requisite_group", "requisite_type": req_type, "groups": groups})

    return {
        "answer_type": "handbook_requisite",
        "title": f"{unit.unit_code} · Requisites ({unit.academic_year} Handbook)",
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
    if focus:
        matching = [o for o in offerings if (o["campus"] or "").lower() == focus.lower()]
        verdict = (
            f"Yes - {unit.unit_code} has {len(matching)} published "
            f"{focus} offering{'s' if len(matching) != 1 else ''} in {unit.academic_year}."
            if matching
            else f"The {unit.academic_year} Handbook publishes no {focus} offering "
            f"for {unit.unit_code}."
        )
    elif offerings:
        verdict = (
            f"{unit.unit_code} has {len(offerings)} published offerings "
            f"in {unit.academic_year}."
        )
    else:
        verdict = f"The {unit.academic_year} Handbook publishes no offerings for {unit.unit_code}."

    blocks: list[dict[str, Any]] = [{"type": "verdict", "text": verdict}]
    if offerings:
        blocks.append(
            {
                "type": "table",
                "columns": ["Campus", "Teaching period", "Mode", "Offering"],
                "keys": ["campus", "teaching_period", "attendance_mode", "offering_code"],
                "rows": offerings,
                "caption": None,
            }
        )
    return {
        "answer_type": "handbook_offering",
        "title": f"{unit.unit_code} · Offerings ({unit.academic_year} Handbook)",
        "blocks": blocks,
        "caveat": MOODLE_CAVEAT,
    }


def _workload_answer(unit: Unit) -> dict[str, Any]:
    blocks: list[dict[str, Any]] = []
    if unit.workload_requirements:
        blocks.append(
            {
                "type": "text",
                "title": "Workload requirements",
                "text": unit.workload_requirements,
            }
        )
    if unit.activities:
        blocks.append(
            {
                "type": "table",
                "columns": ["Activity", "Duration"],
                "keys": ["activity_type", "name"],
                "rows": [
                    {"activity_type": a.activity_type, "name": a.name} for a in unit.activities
                ],
                "caption": None,
            }
        )
    if not blocks:
        blocks.append(
            {
                "type": "verdict",
                "text": "The Handbook publishes no workload detail for this unit.",
            }
        )
    return {
        "answer_type": "handbook_workload",
        "title": f"{unit.unit_code} · Workload ({unit.academic_year} Handbook)",
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
        [{"type": "list", "title": "Unit learning outcomes", "items": items}]
        if items
        else [{"type": "verdict", "text": "The Handbook publishes no learning outcomes yet."}]
    )
    return {
        "answer_type": "handbook_outcomes",
        "title": f"{unit.unit_code} · Learning outcomes ({unit.academic_year} Handbook)",
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


def answer(db: Session, query: str, *, year: int) -> dict[str, Any]:
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
        payload["title"] = f"{unit.unit_code} · What the Handbook publishes"
        payload["blocks"].insert(
            0,
            {
                "type": "verdict",
                "text": "This is a matter of opinion, so there is no official answer. "
                "Here is the published workload, and what students have said.",
            },
        )
        base.update(payload)
        base["sources"] = [_unit_source(unit)]
        base["related_community"] = [_post_brief(p) for p in posts]
        base["suggestions"] = _unit_suggestions(unit.unit_code)
        return base

    if unit is not None and intent in HANDBOOK_ANSWERS:
        base.update(HANDBOOK_ANSWERS[intent](unit, query))
        base["sources"] = [_unit_source(unit)]
        posts, _ = service.search_community(db, query, unit_code=unit.unit_code, limit=3)
        base["related_community"] = [_post_brief(p) for p in posts]
        base["suggestions"] = _unit_suggestions(unit.unit_code)
        return base

    if unit is not None:
        # We know the unit but not what was being asked about it.
        #
        # This used to answer with the whole overview. On a phone that is the
        # entire first screen, so a reader searching a unit code met a wall of
        # prose and never scrolled to the unit itself. A code is a request for
        # the unit, not for an essay about it: the facts fit in four rows, and
        # the link is the thing they came for.
        offered = [o for o in unit.offerings if o.offered]
        periods = sorted({o.teaching_period for o in offered if o.teaching_period})
        campuses = sorted({o.campus for o in offered if o.campus})
        facts = [
            {"field": "Credit points", "value": unit.credit_points},
            {"field": "Level", "value": unit.level},
            {"field": "Campus", "value": "、".join(campuses) if campuses else None},
            {"field": "Teaching period", "value": "、".join(periods) if periods else None},
        ]
        base.update(
            {
                "answer_type": "handbook_overview",
                "title": f"{unit.unit_code} · {unit.title}",
                "blocks": [
                    {
                        "type": "table",
                        "columns": ["Field", "Value"],
                        "keys": ["field", "value"],
                        "rows": [f for f in facts if f["value"]],
                    },
                    {
                        "type": "link",
                        "to": f"/units/{unit.unit_code}",
                        "label": f"Open {unit.unit_code}",
                    },
                ],
                "caveat": None,
            }
        )
        base["sources"] = [_unit_source(unit)]
        base["suggestions"] = _unit_suggestions(unit.unit_code)
        return base

    # No unit code: try the curated FAQ, then the official page index.
    faqs = service.search_faq(db, query, limit=3)
    if faqs:
        top = faqs[0]
        base.update(
            {
                "answer_type": "official_faq",
                "title": top.question,
                "blocks": [{"type": "text", "title": None, "text": top.answer}],
                "caveat": "Always confirm deadlines and eligibility on the official Monash page.",
            }
        )
        base["sources"] = [
            {
                "kind": "official",
                "label": top.official_page.title if top.official_page else "Monash University",
                "url": top.official_url
                or (top.official_page.canonical_url if top.official_page else None),
                "last_checked": top.official_page.last_checked.isoformat()
                if top.official_page and top.official_page.last_checked
                else None,
            }
        ]
        base["suggestions"] = [f.question for f in faqs[1:]]
        return base

    pages, total = service.search_official(db, query, limit=5)
    if pages:
        base.update(
            {
                "answer_type": "official_search",
                "title": "Official Monash pages matching your question",
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
        )
        base["fallback"] = {"total_official": total, "ask_community": True}
        return base

    posts, _ = service.search_community(db, query, limit=5)
    base.update(
        {
            "answer_type": "community_fallback",
            "title": "No official answer indexed for this yet",
            "blocks": [
                {
                    "type": "verdict",
                    "text": "Nothing in the Handbook or the indexed official pages answers this. "
                    "Try different keywords, or ask the community.",
                }
            ],
            "caveat": None,
        }
    )
    base["related_community"] = [_post_brief(p) for p in posts]
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


def _unit_suggestions(code: str) -> list[str]:
    return [
        f"Does {code} have a final exam?",
        f"What are the prerequisites for {code}?",
        f"Is {code} offered in Malaysia?",
        f"{code} 的工作量是多少？",
    ]
