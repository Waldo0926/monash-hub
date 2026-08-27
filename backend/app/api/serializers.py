"""ORM row -> JSON shapes.

Kept in one place so that "official" and "community" payloads always carry the
fields the UI needs to label them differently: a source, and when we last
checked it.

Official payloads optionally carry a third thing: a ``translation`` object, set
when a human-written translation was applied. The UI needs it to say so on
screen - a Chinese paragraph presented as though Monash wrote it in Chinese is
the one outcome the whole translation feature has to avoid. ``None`` means what
you are reading is the source, verbatim.
"""
from __future__ import annotations

from typing import Any

from app.knowledge.translations import Translation, translate_blocks, translated_headings
from app.models.community import CommunityAnswer, CommunityPost
from app.models.handbook import Unit
from app.models.knowledge import FaqEntry, OfficialPage

# A translation that has nothing in it: every serialiser can take one, so the
# untranslated path is the same code as the translated one.
NO_TRANSLATION = Translation("")


def _iso(value) -> str | None:
    return value.isoformat() if value else None


def unit_brief(unit: Unit, tr: Translation = NO_TRANSLATION) -> dict[str, Any]:
    """The card shown in search results, on the home page and in a unit header.

    It takes a translation because this is the payload a reader meets first. A
    home page of English unit titles under a Chinese heading is the version of
    "partially translated" that just looks broken.
    """
    return {
        "unit_code": unit.unit_code,
        "title": tr.field("title", unit.title),
        "academic_year": unit.academic_year,
        "credit_points": unit.credit_points,
        "level": tr.string(unit.level),
        "faculty": tr.string(unit.faculty),
        "has_exam": unit.has_exam,
        "assessment_count": len(unit.assessments),
        "offerings": [
            {
                "campus": tr.string(o.campus),
                "teaching_period": tr.string(o.teaching_period),
                "attendance_mode": tr.string(o.attendance_mode),
            }
            for o in unit.offerings
            if o.offered
        ],
        "source_url": unit.source_url,
        "last_checked": _iso(unit.last_crawled),
        "translation": tr.meta(),
    }


def unit_detail(unit: Unit, tr: Translation = NO_TRANSLATION) -> dict[str, Any]:
    return {
        **unit_brief(unit, tr),
        "school": tr.string(unit.school),
        "overview": tr.field("overview", unit.overview),
        "areas_of_study": tr.field("areas_of_study", unit.areas_of_study),
        "teaching_approach": tr.field("teaching_approach", unit.teaching_approach),
        "workload_requirements": tr.field("workload_requirements", unit.workload_requirements),
        "assessment_summary": tr.field("assessment_summary", unit.assessment_summary),
        # One string, identical on thousands of units - it lives in the global
        # set rather than being stored 2,596 times.
        "assessment_static_text": tr.string(unit.assessment_static_text),
        "translation": tr.meta(),
        "handbook_version": unit.handbook_version,
        "assessments": [
            {
                "number": a.number,
                "name": a.name,
                "type": a.assessment_type,
                "weight": a.weight,
                "hurdle": a.hurdle,
                "description": a.description,
                "learning_outcomes": a.learning_outcomes,
            }
            for a in unit.assessments
        ],
        "requisites": [
            {
                "requisite_type": g.requisite_type,
                "connector": g.connector,
                "title": g.title,
                "description": tr.string(g.description),
                "items": [
                    {
                        "code": i.item_code,
                        # The Handbook's own wording, translated - not the
                        # unit's current title. A requisite record is a snapshot:
                        # FIT2102 names FIT1008 as "Introduction to computer
                        # science", which is what it was called in 2019, and
                        # replacing that with today's title would put words in
                        # the Handbook's mouth.
                        "name": tr.string(i.item_name),
                        "type": i.item_type,
                        "url": i.item_url,
                        "credit_points": i.credit_points,
                    }
                    for i in g.items
                ],
            }
            for g in unit.requisite_groups
        ],
        "learning_outcomes": [
            {"code": o.code, "number": o.number, "description": tr.string(o.description)}
            for o in unit.learning_outcomes
        ],
        "activities": [
            {"activity_type": a.activity_type, "name": a.name, "description": a.description}
            for a in unit.activities
        ],
    }


def official_brief(page: OfficialPage, tr: Translation = NO_TRANSLATION) -> dict[str, Any]:
    return {
        "slug": page.slug,
        "title": tr.field("title", page.title),
        "category": page.category,
        # Which campus the page was written for. The reader has to see this on
        # the card as well as on the page: a student pass in Malaysia is not the
        # Australian subclass 500 visa, and OSHC does not exist there.
        "applies_to": page.applies_to,
        "tags": list(page.tags or []),
        "summary": tr.field("summary", page.summary),
        "translation": tr.meta(),
        "url": page.canonical_url,
        "status": page.status,
        "last_checked": _iso(page.last_checked),
        "last_changed": _iso(page.last_changed),
    }


def official_detail(page: OfficialPage, tr: Translation = NO_TRANSLATION) -> dict[str, Any]:
    blocks = translate_blocks(page.blocks or [], tr)
    return {
        **official_brief(page, tr),
        # Rebuilt from the translated blocks rather than from the stored
        # outline, so the contents list and the headings it points at cannot
        # end up in two different languages.
        "headings": translated_headings(blocks) if tr.strings else (page.headings or []),
        # ``blocks`` is what the page renders; ``clean_text`` is kept as the
        # fallback for a page crawled before the structured extractor existed.
        "blocks": blocks,
        "clean_text": page.clean_text,
        "source_name": page.source.name if page.source else None,
        "refresh_tier": page.refresh_tier,
    }


def faq_brief(entry: FaqEntry, tr: Translation = NO_TRANSLATION) -> dict[str, Any]:
    return {
        "slug": entry.slug,
        "question": tr.field("question", entry.question),
        "answer": tr.field("answer", entry.answer),
        "category": entry.category,
        "tags": list(entry.tags or []),
        "official_url": entry.official_url
        or (entry.official_page.canonical_url if entry.official_page else None),
        "official_title": entry.official_page.title if entry.official_page else None,
        "last_checked": _iso(entry.official_page.last_checked) if entry.official_page else None,
    }


def post_brief(post: CommunityPost) -> dict[str, Any]:
    return {
        "id": post.id,
        "title": post.title,
        "category": post.category,
        "unit_code": post.unit_code,
        "author": post.author.nickname if post.author else None,
        "tags": [pt.tag.slug for pt in post.post_tags if pt.tag],
        "answer_count": post.answer_count,
        "vote_count": post.vote_count,
        "is_solved": post.is_solved,
        "is_pinned": post.is_pinned,
        "created_at": _iso(post.created_at),
        "updated_at": _iso(post.updated_at),
    }


def post_detail(post: CommunityPost) -> dict[str, Any]:
    return {
        **post_brief(post),
        "body": post.body,
        "answers": [answer_brief(a) for a in post.answers if not a.is_hidden],
    }


def answer_brief(answer: CommunityAnswer) -> dict[str, Any]:
    return {
        "id": answer.id,
        "body": answer.body,
        "author": answer.author.nickname if answer.author else None,
        "is_accepted": answer.is_accepted,
        "vote_count": answer.vote_count,
        "created_at": _iso(answer.created_at),
    }
