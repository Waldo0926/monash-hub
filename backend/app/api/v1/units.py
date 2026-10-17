"""Handbook unit endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import requested_locale
from app.api.serializers import tree_node, unit_brief, unit_detail
from app.community import ratings
from app.core.config import get_settings
from app.core.db import get_db
from app.handbook import tree
from app.handbook.years import available_years, resolve_year
from app.knowledge import teach_out, translations
from app.knowledge.glossary import whole_value
from app.models.curriculum import AreaOfStudy, CurriculumContainer, CurriculumItem
from app.models.handbook import Unit, UnitOffering, UnitRequisiteGroup
from app.models.translation import AREA_OF_STUDY, UNIT
from app.search import service

router = APIRouter(prefix="/units", tags=["units"])


def _year(year: int | None) -> int:
    return year or get_settings().current_academic_year


@router.get("")
def list_units(
    q: str = Query("", max_length=300, description="Unit code, title or keyword"),
    year: int | None = None,
    campus: list[str] | None = Query(None),
    teaching_period: list[str] | None = Query(None),
    level: list[str] | None = Query(None),
    prefix: list[str] | None = Query(None, description="Subject prefix, e.g. FIT"),
    faculty: list[str] | None = Query(None),
    school: list[str] | None = Query(None, description="The Handbook's organisational unit"),
    has_exam: bool | None = None,
    sort: str = Query("relevance", pattern="^(relevance|code|title)$"),
    codes: str | None = Query(
        None, max_length=300, description="Comma-separated unit codes, returned in that order"
    ),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0, le=100_000),
    locale: str | None = Depends(requested_locale),
    db: Session = Depends(get_db),
) -> dict:
    if codes:
        # A hand-picked list (the home page shows one unit per faculty). Asked
        # through search it would come back in relevance order and could pick
        # up units that merely mention a code; this returns exactly these, in
        # the order given, and silently drops any the year does not list.
        units = _units_by_code(db, codes, _year(year))
        total = len(units)
    else:
        units, total = service.search_units(
            db,
            q,
            year=_year(year),
            limit=limit,
            offset=offset,
            campus=campus,
            teaching_period=teaching_period,
            level=level,
            prefix=prefix,
            faculty=faculty,
            school=school,
            has_exam=has_exam,
            sort=sort,
        )
    # One query for the whole page of results, not one per card.
    unit_translations = translations.load_many(
        db, locale, UNIT, [u.unit_code for u in units],
        source_hashes={u.unit_code: u.content_hash for u in units},
    )
    # Student ratings ride along so a card can show its stars without a
    # second request. Null when nobody has rated the unit yet.
    stars = ratings.summaries(db, [u.unit_code for u in units])
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "academic_year": _year(year),
        "results": [
            {**unit_brief(u, unit_translations[u.unit_code]), "rating": stars.get(u.unit_code)}
            for u in units
        ],
    }


def _units_by_code(db: Session, codes: str, year: int) -> list[Unit]:
    wanted = list(dict.fromkeys(c.strip().upper() for c in codes.split(",") if c.strip()))[:20]
    rows = db.scalars(
        select(Unit)
        .where(Unit.academic_year == year, Unit.is_active.is_(True), Unit.unit_code.in_(wanted))
        .options(selectinload(Unit.offerings), selectinload(Unit.assessments))
    ).all()
    by_code = {u.unit_code: u for u in rows}
    return [by_code[c] for c in wanted if c in by_code]


@router.get("/filters")
def unit_filters(
    year: int | None = None,
    locale: str | None = Depends(requested_locale),
    db: Session = Depends(get_db),
) -> dict:
    """Facet values that actually exist, so the UI never offers a dead filter.

    Most lists come back with the value most units have first, so a short list
    with "show more" opens on Clayton and Malaysia rather than Alfred Hospital.
    Levels stay in their own order.
    """
    resolved = _year(year)

    def by_count(column, *, offering: bool = False) -> list[str]:
        units = func.count(distinct(Unit.id))
        stmt = select(column).where(Unit.academic_year == resolved, column.is_not(None))
        if offering:
            stmt = stmt.select_from(UnitOffering).join(Unit, Unit.id == UnitOffering.unit_id)
        return list(db.scalars(stmt.group_by(column).order_by(units.desc(), column)).all())

    levels = db.scalars(
        select(distinct(Unit.level))
        .where(Unit.academic_year == resolved, Unit.level.is_not(None))
        .order_by(Unit.level)
    ).all()
    years = db.scalars(
        select(distinct(Unit.academic_year)).order_by(Unit.academic_year.desc())
    ).all()
    values = {
        "campuses": by_count(UnitOffering.campus, offering=True),
        "teaching_periods": by_count(UnitOffering.teaching_period, offering=True),
        "levels": list(levels),
        "prefixes": by_count(Unit.subject_prefix),
        "faculties": by_count(Unit.faculty),
        "schools": by_count(Unit.school),
    }
    # The values stay English because they are what the search matches on. The
    # labels are the glossary's wording for them, so the checkbox says the same
    # thing as the unit page it leads to, in every language and not only Chinese.
    labels = {}
    if locale and locale != "en":
        for name in ("campuses", "teaching_periods", "levels", "faculties", "schools"):
            for value in values[name]:
                if agreed := whole_value(value, locale):
                    labels[value] = agreed
    return {"academic_year": resolved, "years": list(years), **values, "labels": labels}


@router.get("/facets")
def unit_facet_counts(
    q: str = Query("", max_length=300),
    year: int | None = None,
    campus: list[str] | None = Query(None),
    teaching_period: list[str] | None = Query(None),
    level: list[str] | None = Query(None),
    prefix: list[str] | None = Query(None),
    faculty: list[str] | None = Query(None),
    school: list[str] | None = Query(None),
    has_exam: bool | None = None,
    db: Session = Depends(get_db),
) -> dict:
    """How many units each filter value would leave, for the numbers beside the checkboxes.

    Kept apart from ``/filters`` because these change with every tick and
    query, while the list of values only changes with the year.
    """
    resolved = _year(year)
    return {
        "academic_year": resolved,
        "counts": service.unit_facets(
            db,
            q,
            year=resolved,
            campus=campus,
            teaching_period=teaching_period,
            level=level,
            prefix=prefix,
            faculty=faculty,
            school=school,
            has_exam=has_exam,
        ),
    }


def _resolve(db: Session, code: str, year: int | None) -> tuple[int, int | None]:
    """See ``app.handbook.years``: an earlier Handbook when the current one dropped the unit."""
    return resolve_year(db, Unit.unit_code, Unit.academic_year, code, year)


def _load(db: Session, code: str, year: int) -> Unit:
    unit = db.scalar(
        select(Unit)
        .where(Unit.unit_code == code.upper(), Unit.academic_year == year)
        .options(
            selectinload(Unit.offerings),
            selectinload(Unit.assessments),
            # The whole rule tree in one read - the unit page renders the
            # nesting, and lazily loading it would be a query per branch.
            selectinload(Unit.requisite_groups).selectinload(UnitRequisiteGroup.items),
            selectinload(Unit.requisite_groups)
            .selectinload(UnitRequisiteGroup.children)
            .selectinload(UnitRequisiteGroup.items),
            selectinload(Unit.requisite_groups)
            .selectinload(UnitRequisiteGroup.children)
            .selectinload(UnitRequisiteGroup.children)
            .selectinload(UnitRequisiteGroup.items),
            selectinload(Unit.learning_outcomes),
            selectinload(Unit.activities),
        )
    )
    if unit is None:
        raise HTTPException(404, f"{code.upper()} is not in the {year} Handbook index yet")
    return unit


def _areas_including(db: Session, code: str, year: int, locale: str | None) -> list[dict]:
    """The majors, minors and specialisations whose curriculum lists this unit.

    The unit's own ``areas_of_study`` field is a line of prose from the
    Handbook. This reads the curriculum the other way round, so each one can
    be a link, and it says which part of the curriculum names the unit
    ("Core units", "Level 3 elective units"), because core and elective are
    very different reasons to take it.
    """
    rows = db.execute(
        select(
            AreaOfStudy.aos_code,
            AreaOfStudy.title,
            AreaOfStudy.aos_type,
            AreaOfStudy.content_hash,
            CurriculumContainer.title,
        )
        .join(CurriculumContainer, CurriculumContainer.area_of_study_id == AreaOfStudy.id)
        .join(CurriculumItem, CurriculumItem.container_id == CurriculumContainer.id)
        .where(
            CurriculumItem.item_code == code.upper(),
            AreaOfStudy.academic_year == year,
            AreaOfStudy.is_active.is_(True),
        )
        .order_by(AreaOfStudy.aos_type, AreaOfStudy.title, CurriculumContainer.order_index)
    ).all()

    found: dict[str, dict] = {}
    for aos_code, title, aos_type, content_hash, part in rows:
        entry = found.setdefault(aos_code, {
            "aos_code": aos_code, "title": title, "aos_type": aos_type,
            "parts": [], "_hash": content_hash,
        })
        if part and part not in entry["parts"]:
            entry["parts"].append(part)

    codes = list(found)
    tr = translations.load_many(
        db, locale, AREA_OF_STUDY, codes, source_hashes={c: found[c]["_hash"] for c in codes}
    )
    result = []
    for aos_code, entry in found.items():
        entry.pop("_hash")
        entry["title"] = tr[aos_code].field("title", entry["title"]) or entry["title"]
        entry["aos_type"] = tr[aos_code].value(entry["aos_type"])
        result.append(entry)
    return result


@router.get("/{code}")
def get_unit(
    code: str,
    year: int | None = None,
    locale: str | None = Depends(requested_locale),
    db: Session = Depends(get_db),
) -> dict:
    academic_year, not_in_year = _resolve(db, code, year)
    unit = _load(db, code, academic_year)
    tr = translations.load(db, locale, UNIT, unit.unit_code, source_hash=unit.content_hash)
    return {
        **unit_detail(unit, tr),
        "not_in_year": not_in_year,
        "available_years": available_years(db, Unit.unit_code, Unit.academic_year, code),
        "teach_out": teach_out.lookup(db, [unit.unit_code]).get(unit.unit_code),
        "areas": _areas_including(db, unit.unit_code, academic_year, locale),
    }


@router.get("/{code}/assessment")
def get_assessment(code: str, year: int | None = None, db: Session = Depends(get_db)) -> dict:
    academic_year, not_in_year = _resolve(db, code, year)
    unit = _load(db, code, academic_year)
    detail = unit_detail(unit)
    return {
        "unit_code": unit.unit_code,
        "academic_year": unit.academic_year,
        "not_in_year": not_in_year,
        "has_exam": unit.has_exam,
        "assessment_summary": unit.assessment_summary,
        "assessments": detail["assessments"],
        "source_url": unit.source_url,
        "last_checked": detail["last_checked"],
    }


@router.get("/{code}/requisites")
def get_requisites(code: str, year: int | None = None, db: Session = Depends(get_db)) -> dict:
    academic_year, not_in_year = _resolve(db, code, year)
    unit = _load(db, code, academic_year)
    return {
        "unit_code": unit.unit_code,
        "academic_year": unit.academic_year,
        "not_in_year": not_in_year,
        "requisites": unit_detail(unit)["requisites"],
        "source_url": unit.source_url,
    }


@router.get("/{code}/offerings")
def get_offerings(code: str, year: int | None = None, db: Session = Depends(get_db)) -> dict:
    academic_year, not_in_year = _resolve(db, code, year)
    unit = _load(db, code, academic_year)
    return {
        "unit_code": unit.unit_code,
        "academic_year": unit.academic_year,
        "not_in_year": not_in_year,
        "offerings": unit_brief(unit)["offerings"],
        "source_url": unit.source_url,
    }


@router.get("/{code}/unlocks")
def get_unlocks(
    code: str,
    campus: str | None = None,
    year: int | None = None,
    locale: str | None = Depends(requested_locale),
    db: Session = Depends(get_db),
) -> dict:
    """The units that need this one, as a list rather than a graph.

    The graph on /tree answers "how deep does this go"; this answers the
    simpler question on a unit page, "what can I take after it". Each row
    carries the same campus mark as a tree node.
    """
    academic_year, not_in_year = _resolve(db, code, year)
    seed = _load(db, code, academic_year)
    found = tree.unlocks(db, seed.unit_code, academic_year)

    codes = sorted(found.direct)
    units = tree.load_units(db, codes, academic_year)
    hashes = {c: u.content_hash for c, u in units.items()}
    tr = translations.load_many(db, locale, UNIT, codes, source_hashes=hashes)
    rows = [
        {**tree_node(units.get(c), c, 1, campus, tr[c]), "requisite_type": found.direct[c]}
        for c in codes
        if c in units
    ]
    return {
        "seed": seed.unit_code,
        "academic_year": academic_year,
        "not_in_year": not_in_year,
        "campus": campus,
        "count": len(rows),
        "total_downstream": found.total,
        "truncated": found.truncated,
        "units": rows,
    }


@router.get("/{code}/tree")
def get_tree(
    code: str,
    direction: str = Query("upstream", pattern="^(upstream|downstream|both)$"),
    depth: int = Query(3, ge=1, le=tree.MAX_DEPTH),
    campus: str | None = None,
    year: int | None = None,
    locale: str | None = Depends(requested_locale),
    db: Session = Depends(get_db),
) -> dict:
    """The prerequisite graph around one unit.

    ``campus`` does not filter the graph - a prerequisite you cannot take here
    is the single most important thing to show a Malaysia student, and hiding
    it would draw a path that looks walkable. It marks each node instead.
    """
    academic_year, not_in_year = _resolve(db, code, year)
    seed = _load(db, code, academic_year)
    found = tree.walk(db, seed.unit_code, academic_year, direction, depth)

    codes = found.codes()
    units = tree.load_units(db, codes, academic_year)
    hashes = {c: u.content_hash for c, u in units.items()}
    tr = translations.load_many(db, locale, UNIT, codes, source_hashes=hashes)

    return {
        "seed": seed.unit_code,
        "academic_year": academic_year,
        # The whole graph is read from the seed's year, so it stays one Handbook.
        "not_in_year": not_in_year,
        "available_years": available_years(db, Unit.unit_code, Unit.academic_year, code),
        "direction": direction,
        "depth": depth,
        "campus": campus,
        "truncated": found.truncated,
        "nodes": [
            tree_node(units.get(c), c, found.depth_of[c], campus, tr[c])
            for c in codes
        ],
        "edges": [
            {
                "source": e.source,
                "target": e.target,
                "type": e.requisite_type,
                "connector": e.connector,
                "group": e.group_id,
            }
            for e in found.edges.values()
        ],
    }
