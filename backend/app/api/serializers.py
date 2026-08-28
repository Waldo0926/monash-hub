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
from app.models.curriculum import AreaOfStudy, Course
from app.models.handbook import Unit
from app.models.knowledge import FaqEntry, OfficialPage

# A translation that has nothing in it: every serialiser can take one, so the
# untranslated path is the same code as the translated one.
NO_TRANSLATION = Translation("")


def _iso(value) -> str | None:
    return value.isoformat() if value else None


def requisite_group(group, tr: Translation = NO_TRANSLATION) -> dict[str, Any]:
    """One requisite rule, with the groups nested inside it.

    The nesting carries the meaning: FIT2099 asks for one of six programming
    units *or* an engineering pair, and rendered as a flat list of groups that
    reads as "all of the above".
    """
    return {
        "requisite_type": group.requisite_type,
        "connector": group.connector,
        "title": group.title,
        "description": tr.string(group.description),
        "items": [
            {
                "code": i.item_code,
                # The Handbook's own wording, translated - not the unit's
                # current title. A requisite record is a snapshot: FIT2102
                # names FIT1008 as "Introduction to computer science", which
                # is what it was called in 2019, and replacing that with
                # today's title would put words in the Handbook's mouth.
                "name": tr.string(i.item_name),
                "type": i.item_type,
                "url": i.item_url,
                "credit_points": i.credit_points,
            }
            for i in group.items
        ],
        "groups": [requisite_group(child, tr) for child in group.children],
    }


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
        "requisites": [requisite_group(g, tr) for g in unit.requisite_groups],
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
        # Taken from the page the answer is traceable to rather than stored
        # again here: an answer about the 48-hour work limit is Australian
        # because the page it cites is, and the two must never disagree.
        "applies_to": entry.official_page.applies_to if entry.official_page else None,
        "last_checked": _iso(entry.official_page.last_checked) if entry.official_page else None,
    }


# What a reader is told about who wrote something. Anonymity is decided when
# the post is written and never re-decided here: the author_id is still on the
# row, because a post nobody owns cannot be edited, moderated or answered by
# its own writer, and this is the one place that has to refuse to say the name.
def _writer(row, viewer_id: int | None) -> dict[str, Any]:
    if row.is_anonymous:
        return {
            "author": None,
            "anonymous": True,
            # So the writer can recognise their own anonymous post in a list.
            # It says nothing to anyone else.
            "is_mine": viewer_id is not None and row.author_id == viewer_id,
        }
    return {
        "author": row.author.nickname if row.author else None,
        "anonymous": False,
        "is_mine": viewer_id is not None and row.author_id == viewer_id,
    }


def post_brief(
    post: CommunityPost, viewer_id: int | None = None, voted: set[int] | None = None
) -> dict[str, Any]:
    return {
        "id": post.id,
        "title": post.title,
        "category": post.category,
        "unit_code": post.unit_code,
        **_writer(post, viewer_id),
        "tags": [pt.tag.slug for pt in post.post_tags if pt.tag],
        "answer_count": post.answer_count,
        "vote_count": post.vote_count,
        "viewer_voted": post.id in (voted or set()),
        "is_solved": post.is_solved,
        "is_pinned": post.is_pinned,
        "created_at": _iso(post.created_at),
        "updated_at": _iso(post.updated_at),
    }


def post_detail(
    post: CommunityPost,
    viewer_id: int | None = None,
    voted_posts: set[int] | None = None,
    voted_answers: set[int] | None = None,
) -> dict[str, Any]:
    return {
        **post_brief(post, viewer_id, voted_posts),
        "body": post.body,
        "answers": [
            answer_brief(a, viewer_id, voted_answers)
            for a in post.answers
            if not a.is_hidden
        ],
    }


def answer_brief(
    answer: CommunityAnswer, viewer_id: int | None = None, voted: set[int] | None = None
) -> dict[str, Any]:
    """One reply, and the replies to it.

    Nested, because a thread is a thread: on Ed you answer a question and then
    argue about the answer, and a flat list cannot say which remark is about
    which.
    """
    return {
        "id": answer.id,
        "parent_id": answer.parent_id,
        "body": answer.body,
        **_writer(answer, viewer_id),
        "is_accepted": answer.is_accepted,
        "vote_count": answer.vote_count,
        "viewer_voted": answer.id in (voted or set()),
        "created_at": _iso(answer.created_at),
        "replies": [
            answer_brief(child, viewer_id, voted)
            for child in answer.children
            if not child.is_hidden
        ],
    }


# The graph draws one chip per teaching period, so the long Handbook names have
# to survive as something that fits in a 150px card. Anything unrecognised keeps
# its full name rather than being squeezed into a wrong abbreviation.
_PERIOD_SHORT = (
    ("first semester", "S1"),
    ("second semester", "S2"),
    ("summer semester a", "SA"),
    ("summer semester b", "SB"),
    ("winter semester", "W"),
    ("full year", "FY"),
    # Malaysia's own intake. It has no Clayton equivalent, and spelled out it is
    # longer than the card it sits on.
    ("october intake", "OCT"),
    ("monash indonesia", "IDN"),
    ("trimester ", "TM"),
    ("teaching period ", "TP"),
    ("research quarter ", "RQ"),
    ("term ", "T"),
)

# Chips read as a timeline, so they are ordered like one rather than by the row
# order the Handbook happened to publish.
_PERIOD_ORDER = {short: rank for rank, short in enumerate(
    ("S1", "S2", "SA", "SB", "W", "OCT", "FY")
)}


def period_rank(short: str | None) -> tuple[int, str]:
    return (_PERIOD_ORDER.get(short or "", len(_PERIOD_ORDER)), short or "")


def short_period(name: str | None) -> str | None:
    """"First semester (extended)" -> "S1". Numbered periods keep their number."""
    if not name:
        return None
    lowered = name.strip().lower()
    for prefix, short in _PERIOD_SHORT:
        if lowered.startswith(prefix):
            tail = lowered[len(prefix):].strip()
            return f"{short}{tail}" if prefix.endswith(" ") and tail[:1].isdigit() else short
    return name


def tree_node(
    unit: Unit | None,
    code: str,
    depth: int,
    campus: str | None,
    tr: Translation = NO_TRANSLATION,
) -> dict[str, Any]:
    """One card in the unit tree.

    ``unit`` is None for a code the Handbook names as a requisite but does not
    publish for this year. Those are drawn greyed rather than dropped: a
    prerequisite that no longer exists is something a student planning a degree
    needs to see, and silently deleting the node makes the rule look satisfiable.
    """
    if unit is None:
        return {
            "unit_code": code,
            "title": None,
            "depth": depth,
            "in_year": False,
            "offered_at_campus": False,
            "periods": [],
            "offerings": [],
            "prefix": code[:3],
        }

    offerings = [o for o in unit.offerings if o.offered]
    here = [o for o in offerings if not campus or o.campus == campus]
    periods: list[str] = []
    for offering in here or offerings:
        label = short_period(offering.teaching_period)
        if label and label not in periods:
            periods.append(label)
    periods.sort(key=period_rank)
    return {
        "unit_code": unit.unit_code,
        "title": tr.field("title", unit.title),
        "credit_points": unit.credit_points,
        "level": tr.string(unit.level),
        "prefix": unit.subject_prefix or unit.unit_code[:3],
        "depth": depth,
        "in_year": True,
        "offered_at_campus": bool(here) if campus else True,
        "periods": periods,
        "offerings": [
            {
                "campus": tr.string(o.campus),
                "campus_raw": o.campus,
                "teaching_period": tr.string(o.teaching_period),
                "short": short_period(o.teaching_period),
            }
            for o in offerings
        ],
        "source_url": unit.source_url,
        "translation": tr.meta(),
    }


def course_brief(course: Course, tr: Translation = NO_TRANSLATION) -> dict[str, Any]:
    """The row in the course picker.

    It takes a translation for the same reason ``unit_brief`` does: a list of
    English degree names under a Chinese heading is the version of "partially
    translated" that just looks broken.
    """
    return {
        "course_code": course.course_code,
        "title": tr.field("title", course.title),
        # An abbreviation is a mark, not a sentence: BCompSci stays BCompSci.
        "abbreviated_name": course.abbreviated_name,
        "credit_points": course.credit_points,
        "course_type": tr.string(course.course_type),
        "faculty": tr.string(course.faculty),
        "campuses": [tr.string(c) for c in course.campuses or []],
        "campuses_raw": list(course.campuses or []),
        "duration_years": course.duration_years,
        "academic_year": course.academic_year,
    }


def course_detail(course: Course, tr: Translation = NO_TRANSLATION) -> dict[str, Any]:
    """The header of a degree page. The structure is assembled by the router."""
    return {
        **course_brief(course, tr),
        "aqf_level": tr.string(course.aqf_level),
        "cricos_code": course.cricos_code,
        "school": tr.string(course.school),
        "overview": tr.field("overview", course.overview),
        # structure_text and requirements_text stay in the database and out of
        # this payload. They are five thousand characters that nothing renders,
        # and shipping them untranslated on a Chinese page would be worse than
        # not shipping them at all.
        "source_url": course.source_url,
        "last_checked": _iso(course.last_crawled),
        "translation": tr.meta(),
    }


def area_of_study_detail(aos: AreaOfStudy, tr: Translation = NO_TRANSLATION) -> dict[str, Any]:
    return {
        "aos_code": aos.aos_code,
        "title": tr.field("title", aos.title),
        "aos_type": tr.string(aos.aos_type),
        "study_level": tr.string(aos.study_level),
        "credit_points": aos.credit_points,
        "faculty": tr.string(aos.faculty),
        "overview": tr.field("overview", aos.overview),
        "academic_year": aos.academic_year,
        "source_url": aos.source_url,
        "last_checked": _iso(aos.last_crawled),
        "translation": tr.meta(),
    }
