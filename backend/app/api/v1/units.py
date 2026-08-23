"""Handbook unit endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import distinct, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import requested_locale
from app.api.serializers import unit_brief, unit_detail
from app.core.config import get_settings
from app.core.db import get_db
from app.knowledge import translations
from app.models.handbook import Unit, UnitOffering
from app.models.translation import UNIT
from app.search import service

router = APIRouter(prefix="/units", tags=["units"])


def _year(year: int | None) -> int:
    return year or get_settings().current_academic_year


@router.get("")
def list_units(
    q: str = Query("", description="Unit code, title or keyword"),
    year: int | None = None,
    campus: str | None = None,
    teaching_period: str | None = None,
    level: str | None = None,
    prefix: str | None = Query(None, description="Subject prefix, e.g. FIT"),
    has_exam: bool | None = None,
    sort: str = Query("relevance", pattern="^(relevance|code|title)$"),
    limit: int = Query(20, le=100),
    offset: int = 0,
    locale: str | None = Depends(requested_locale),
    db: Session = Depends(get_db),
) -> dict:
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
        has_exam=has_exam,
        sort=sort,
    )
    # One query for the whole page of results, not one per card.
    unit_translations = translations.load_many(
        db, locale, UNIT, [u.unit_code for u in units],
        source_hashes={u.unit_code: u.content_hash for u in units},
    )
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "academic_year": _year(year),
        "results": [unit_brief(u, unit_translations[u.unit_code]) for u in units],
    }


@router.get("/filters")
def unit_filters(year: int | None = None, db: Session = Depends(get_db)) -> dict:
    """Facet values that actually exist, so the UI never offers a dead filter."""
    resolved = _year(year)
    campuses = db.scalars(
        select(distinct(UnitOffering.campus))
        .join(Unit, Unit.id == UnitOffering.unit_id)
        .where(Unit.academic_year == resolved, UnitOffering.campus.is_not(None))
        .order_by(UnitOffering.campus)
    ).all()
    periods = db.scalars(
        select(distinct(UnitOffering.teaching_period))
        .join(Unit, Unit.id == UnitOffering.unit_id)
        .where(Unit.academic_year == resolved, UnitOffering.teaching_period.is_not(None))
        .order_by(UnitOffering.teaching_period)
    ).all()
    levels = db.scalars(
        select(distinct(Unit.level))
        .where(Unit.academic_year == resolved, Unit.level.is_not(None))
        .order_by(Unit.level)
    ).all()
    prefixes = db.scalars(
        select(distinct(Unit.subject_prefix))
        .where(Unit.academic_year == resolved, Unit.subject_prefix.is_not(None))
        .order_by(Unit.subject_prefix)
    ).all()
    years = db.scalars(
        select(distinct(Unit.academic_year)).order_by(Unit.academic_year.desc())
    ).all()
    return {
        "academic_year": resolved,
        "years": list(years),
        "campuses": list(campuses),
        "teaching_periods": list(periods),
        "levels": list(levels),
        "prefixes": list(prefixes),
    }


def _load(db: Session, code: str, year: int) -> Unit:
    unit = db.scalar(
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
    if unit is None:
        raise HTTPException(404, f"{code.upper()} is not in the {year} Handbook index yet")
    return unit


@router.get("/{code}")
def get_unit(
    code: str,
    year: int | None = None,
    locale: str | None = Depends(requested_locale),
    db: Session = Depends(get_db),
) -> dict:
    unit = _load(db, code, _year(year))
    tr = translations.load(db, locale, UNIT, unit.unit_code, source_hash=unit.content_hash)
    return unit_detail(unit, tr)


@router.get("/{code}/assessment")
def get_assessment(code: str, year: int | None = None, db: Session = Depends(get_db)) -> dict:
    unit = _load(db, code, _year(year))
    detail = unit_detail(unit)
    return {
        "unit_code": unit.unit_code,
        "academic_year": unit.academic_year,
        "has_exam": unit.has_exam,
        "assessment_summary": unit.assessment_summary,
        "assessments": detail["assessments"],
        "source_url": unit.source_url,
        "last_checked": detail["last_checked"],
    }


@router.get("/{code}/requisites")
def get_requisites(code: str, year: int | None = None, db: Session = Depends(get_db)) -> dict:
    unit = _load(db, code, _year(year))
    return {
        "unit_code": unit.unit_code,
        "academic_year": unit.academic_year,
        "requisites": unit_detail(unit)["requisites"],
        "source_url": unit.source_url,
    }


@router.get("/{code}/offerings")
def get_offerings(code: str, year: int | None = None, db: Session = Depends(get_db)) -> dict:
    unit = _load(db, code, _year(year))
    return {
        "unit_code": unit.unit_code,
        "academic_year": unit.academic_year,
        "offerings": unit_brief(unit)["offerings"],
        "source_url": unit.source_url,
    }
