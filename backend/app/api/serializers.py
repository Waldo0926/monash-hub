"""ORM row -> JSON shapes.

Kept in one place so that "official" and "community" payloads always carry the
fields the UI needs to label them differently: a source, and when we last
checked it.
"""
from __future__ import annotations

from typing import Any

from app.models.community import CommunityAnswer, CommunityPost
from app.models.handbook import Unit
from app.models.knowledge import FaqEntry, OfficialPage


def _iso(value) -> str | None:
    return value.isoformat() if value else None


def unit_brief(unit: Unit) -> dict[str, Any]:
    return {
        "unit_code": unit.unit_code,
        "title": unit.title,
        "academic_year": unit.academic_year,
        "credit_points": unit.credit_points,
        "level": unit.level,
        "faculty": unit.faculty,
        "has_exam": unit.has_exam,
        "assessment_count": len(unit.assessments),
        "offerings": [
            {
                "campus": o.campus,
                "teaching_period": o.teaching_period,
                "attendance_mode": o.attendance_mode,
            }
            for o in unit.offerings
            if o.offered
        ],
        "source_url": unit.source_url,
        "last_checked": _iso(unit.last_crawled),
    }


def unit_detail(unit: Unit) -> dict[str, Any]:
    return {
        **unit_brief(unit),
        "school": unit.school,
        "overview": unit.overview,
        "areas_of_study": unit.areas_of_study,
        "teaching_approach": unit.teaching_approach,
        "workload_requirements": unit.workload_requirements,
        "assessment_summary": unit.assessment_summary,
        "assessment_static_text": unit.assessment_static_text,
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
                "description": g.description,
                "items": [
                    {
                        "code": i.item_code,
                        "name": i.item_name,
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
            {"code": o.code, "number": o.number, "description": o.description}
            for o in unit.learning_outcomes
        ],
        "activities": [
            {"activity_type": a.activity_type, "name": a.name, "description": a.description}
            for a in unit.activities
        ],
    }


def official_brief(page: OfficialPage) -> dict[str, Any]:
    return {
        "slug": page.slug,
        "title": page.title,
        "category": page.category,
        "tags": list(page.tags or []),
        "summary": page.summary,
        "url": page.canonical_url,
        "status": page.status,
        "last_checked": _iso(page.last_checked),
        "last_changed": _iso(page.last_changed),
    }


def official_detail(page: OfficialPage) -> dict[str, Any]:
    return {
        **official_brief(page),
        "headings": page.headings or [],
        "clean_text": page.clean_text,
        "source_name": page.source.name if page.source else None,
        "refresh_tier": page.refresh_tier,
    }


def faq_brief(entry: FaqEntry) -> dict[str, Any]:
    return {
        "slug": entry.slug,
        "question": entry.question,
        "answer": entry.answer,
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
