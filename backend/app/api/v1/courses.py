"""Handbook course and area-of-study endpoints."""
from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import requested_locale
from app.api.serializers import (
    NO_TRANSLATION,
    area_of_study_detail,
    course_brief,
    course_detail,
    period_rank,
    short_period,
)
from app.core.config import get_settings
from app.core.db import get_db
from app.knowledge import translations
from app.knowledge.translations import Translation
from app.models.curriculum import AreaOfStudy, Course, CurriculumContainer
from app.models.handbook import Unit
from app.models.translation import AREA_OF_STUDY, COURSE, UNIT

router = APIRouter(prefix="/courses", tags=["courses"])


def _year(year: int | None) -> int:
    return year or get_settings().current_academic_year


# A part of a degree that any unit can count towards, as opposed to one that
# lists what counts. The planner has to tell them apart: a *specified* or
# *discipline* elective part is satisfied only by the units it names, but a free
# elective part is satisfied by whatever is left over, which is exactly what the
# words "free elective" mean and why "Part E. Free elective studies" read 0/48
# for a student who had planned twelve units it did not happen to list.
#
# Two signals, both taken from the English source so the answer does not depend
# on which language the page is being read in:
#
#   * the title says "free elective" - 24 parts across the catalogue, and
#   * the description says "across the University", which is the Handbook's own
#     phrase for a part with no list - another 31, mostly titled plainly
#     "Part D. Elective studies".
#
# The title must mention electives either way. Without that clause the
# description test also matches "Rules", "Course requirements" and even "Part A.
# Foundation studies", all of which mention the University in passing.
_ELECTIVE = re.compile(r"\belectives?\b", re.IGNORECASE)
_FREE_ELECTIVE = re.compile(r"\bfree\s+electives?\b", re.IGNORECASE)
_NO_LIST = re.compile(r"across the University", re.IGNORECASE)


def _is_free_elective(title: str | None, description: str | None) -> bool:
    if not title or not _ELECTIVE.search(title):
        return False
    return bool(_FREE_ELECTIVE.search(title) or _NO_LIST.search(description or ""))


@router.get("")
def list_courses(
    q: str | None = None,
    campus: str | None = None,
    course_type: str | None = None,
    faculty: str | None = None,
    year: int | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    locale: str | None = Depends(requested_locale),
    db: Session = Depends(get_db),
) -> dict:
    """The course picker.

    ``campus`` filters here rather than marking, unlike the unit graph: a
    degree Malaysia does not teach is not a degree a Malaysia student can pick,
    and there is no partial version of that to show them.
    """
    academic_year = _year(year)
    stmt = select(Course).where(Course.academic_year == academic_year, Course.is_active)

    if q:
        term = q.strip()
        stmt = stmt.where(
            or_(
                Course.course_code.ilike(f"{term}%"),
                Course.title.ilike(f"%{term}%"),
                Course.abbreviated_name.ilike(f"{term}%"),
            )
        )
    if campus:
        stmt = stmt.where(Course.campuses.any(campus))
    if course_type:
        stmt = stmt.where(Course.course_type == course_type)
    if faculty:
        stmt = stmt.where(Course.faculty == faculty)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(
        stmt.order_by(Course.title).limit(limit).offset(offset)
    ).all()
    tr = translations.load_many(
        db, locale, COURSE, [c.course_code for c in rows],
        source_hashes={c.course_code: c.content_hash for c in rows},
    )
    return {
        "total": total,
        "academic_year": academic_year,
        "results": [course_brief(course, tr[course.course_code]) for course in rows],
    }


@router.get("/filters")
def course_filters(year: int | None = None, db: Session = Depends(get_db)) -> dict:
    academic_year = _year(year)
    live = (Course.academic_year == academic_year, Course.is_active)

    def distinct(column):
        return db.scalars(select(column).where(*live).distinct()).all()

    campuses = distinct(func.unnest(Course.campuses))
    types = distinct(Course.course_type)
    faculties = distinct(Course.faculty)
    return {
        "campuses": sorted(c for c in campuses if c),
        "course_types": sorted(t for t in types if t),
        "faculties": sorted(f for f in faculties if f),
    }


def _load_course(db: Session, code: str, year: int) -> Course:
    course = db.scalar(
        select(Course).where(
            Course.course_code == code.upper(), Course.academic_year == year
        )
    )
    if course is None:
        raise HTTPException(404, f"{code.upper()} is not in the {year} Handbook index yet")
    return course


def _tree(
    db: Session,
    *,
    course_id: int | None = None,
    aos_id: int | None = None,
    tr: Translation = NO_TRANSLATION,
) -> list[dict]:
    """Every container of one owner, in one query, reassembled into a tree.

    Each container carries its owner, so the whole structure is one indexed
    read rather than a walk that costs a query per level.
    """
    column = (
        CurriculumContainer.course_id == course_id
        if course_id is not None
        else CurriculumContainer.area_of_study_id == aos_id
    )
    rows = db.scalars(
        select(CurriculumContainer)
        .where(column)
        .options(selectinload(CurriculumContainer.items))
        .order_by(CurriculumContainer.order_index)
    ).all()

    nodes: dict[int, dict] = {}
    for row in rows:
        nodes[row.id] = {
            "id": row.id,
            # An outline of "Part A. Foundation studies" under a Chinese
            # heading is the failure this translation layer exists to avoid.
            "title": tr.string(row.title),
            "description": tr.field("description", row.description),
            "footnote": tr.field("footnote", row.footnote),
            "credit_points": row.credit_points,
            "credit_points_max": row.credit_points_max,
            "connector": row.connector,
            # From the English, before translation: what a part *is* does not
            # change with the reader's language.
            "free_elective": _is_free_elective(row.title, row.description),
            "items": [
                {
                    "code": item.item_code,
                    "name": tr.string(item.item_name),
                    "type": item.item_type,
                    "credit_points": item.credit_points,
                    "connector": item.connector,
                }
                for item in row.items
            ],
            "containers": [],
        }

    roots: list[dict] = []
    for row in rows:
        if row.parent_id and row.parent_id in nodes:
            nodes[row.parent_id]["containers"].append(nodes[row.id])
        else:
            roots.append(nodes[row.id])
    return roots


def _unit_facts(
    db: Session, codes: list[str], year: int, campus: str | None, locale: str | None
) -> dict[str, dict]:
    """Title, offerings and campus availability for every unit the tree names.

    Without this the degree view is a wall of codes; with it, and with campus
    set, it is a wall of codes with the ones Malaysia does not teach marked -
    which is the reason for building it here rather than linking out.
    """
    if not codes:
        return {}
    units = db.scalars(
        select(Unit)
        .where(Unit.unit_code.in_(codes), Unit.academic_year == year)
        .options(selectinload(Unit.offerings))
    ).all()
    found = {unit.unit_code: unit for unit in units}
    tr = translations.load_many(
        db, locale, UNIT, list(found),
        source_hashes={c: u.content_hash for c, u in found.items()},
    )

    facts: dict[str, dict] = {}
    for code in codes:
        unit = found.get(code)
        if unit is None:
            facts[code] = {"in_year": False, "offered_at_campus": False, "periods": []}
            continue
        offered = [o for o in unit.offerings if o.offered]
        here = [o for o in offered if not campus or o.campus == campus]
        periods: list[str] = []
        for offering in here or offered:
            label = short_period(offering.teaching_period)
            if label and label not in periods:
                periods.append(label)
        periods.sort(key=period_rank)
        facts[code] = {
            "in_year": True,
            "title": tr[code].field("title", unit.title),
            "credit_points": unit.credit_points,
            "offered_at_campus": bool(here) if campus else True,
            "periods": periods,
        }
    return facts


def _codes_in(containers: list[dict], kind: str) -> list[str]:
    found: list[str] = []
    for node in containers:
        found += [i["code"] for i in node["items"] if i["type"] == kind]
        found += _codes_in(node["containers"], kind)
    return list(dict.fromkeys(found))


@router.get("/{code}")
def get_course(
    code: str,
    campus: str | None = None,
    year: int | None = None,
    locale: str | None = Depends(requested_locale),
    db: Session = Depends(get_db),
) -> dict:
    """One degree and the whole structure under it."""
    academic_year = _year(year)
    course = _load_course(db, code, academic_year)
    tr = translations.load(db, locale, COURSE, course.course_code,
                           source_hash=course.content_hash)
    containers = _tree(db, course_id=course.id, tr=tr)
    units = _unit_facts(db, _codes_in(containers, "unit"), academic_year, campus, locale)

    payload = course_detail(course, tr)
    payload["campus"] = campus
    payload["containers"] = containers
    payload["units"] = units
    # Each area of study carries its own translation row, so the list of
    # specialisations needs its own load - the course's translation says
    # nothing about what its majors are called.
    offered = db.scalars(
        select(AreaOfStudy).where(
            AreaOfStudy.aos_code.in_(
                _codes_in(containers, "specialisation")
                + _codes_in(containers, "major")
                + _codes_in(containers, "minor")
            ),
            AreaOfStudy.academic_year == academic_year,
        ).order_by(AreaOfStudy.title)
    ).all()
    aos_tr = translations.load_many(
        db, locale, AREA_OF_STUDY, [row.aos_code for row in offered],
        source_hashes={row.aos_code: row.content_hash for row in offered},
    )
    # Each specialisation's own unit list, so a plan can be measured against a
    # part that asks for one.
    #
    # Without this "Part C. Specialist studies" reads 0/36 for a student who has
    # planned the whole specialisation, because Part C does not list units at
    # all - it lists the four specialisations on offer, and a plan holds unit
    # codes. Nothing downstream could match FIT2102 against ALGSFTWR01.
    aos_units: dict[str, list[str]] = {}
    for row in offered:
        aos_units[row.aos_code] = _codes_in(_tree(db, aos_id=row.id), "unit")

    # The facts map has to cover them too, or the credit points of a planned
    # specialisation unit are unknown and it counts as zero.
    extra = sorted({code for codes in aos_units.values() for code in codes} - set(units))
    if extra:
        units.update(_unit_facts(db, extra, academic_year, campus, locale))

    payload["areas_of_study"] = [
        {
            "code": row.aos_code,
            "title": aos_tr[row.aos_code].field("title", row.title),
            "aos_type": aos_tr[row.aos_code].string(row.aos_type),
            "credit_points": row.credit_points,
            "unit_codes": aos_units.get(row.aos_code, []),
        }
        for row in offered
    ]
    return payload


@router.get("/aos/{code}")
def get_area_of_study(
    code: str,
    campus: str | None = None,
    year: int | None = None,
    locale: str | None = Depends(requested_locale),
    db: Session = Depends(get_db),
) -> dict:
    """One major, minor or specialisation and the units in it."""
    academic_year = _year(year)
    aos = db.scalar(
        select(AreaOfStudy).where(
            AreaOfStudy.aos_code == code.upper(), AreaOfStudy.academic_year == academic_year
        )
    )
    if aos is None:
        raise HTTPException(404, f"{code.upper()} is not in the {academic_year} Handbook index yet")

    tr = translations.load(db, locale, AREA_OF_STUDY, aos.aos_code, source_hash=aos.content_hash)
    containers = _tree(db, aos_id=aos.id, tr=tr)
    payload = area_of_study_detail(aos, tr)
    payload["campus"] = campus
    payload["containers"] = containers
    payload["units"] = _unit_facts(
        db, _codes_in(containers, "unit"), academic_year, campus, locale
    )
    return payload
