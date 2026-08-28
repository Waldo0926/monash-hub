"""Write parsed courses and areas of study to the database.

Same contract as the unit repository: hash first, and an unchanged page costs
no write. The one thing this does differently is the structure - a container
tree is replaced wholesale rather than diffed, because a requirement group has
no stable identity across Handbook versions. There is no id to match on, only
a position and a title, and matching on those would silently reparent a group
when the Handbook inserts a Part between two others.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.curriculum import (
    AreaOfStudy,
    Course,
    CurriculumContainer,
    CurriculumItem,
)

COURSE_FIELDS = (
    "title", "abbreviated_name", "credit_points", "cricos_code", "aqf_level",
    "course_type", "faculty", "school", "campuses", "duration_years", "overview",
    "structure_text", "requirements_text", "handbook_version", "source_url",
    "content_hash",
)

AOS_FIELDS = (
    "title", "aos_type", "study_level", "credit_points", "faculty", "school",
    "overview", "handbook_version", "source_url", "content_hash",
)


def get_course(db: Session, code: str, year: int) -> Course | None:
    return db.scalar(
        select(Course).where(Course.course_code == code.upper(), Course.academic_year == year)
    )


def get_area_of_study(db: Session, code: str, year: int) -> AreaOfStudy | None:
    return db.scalar(
        select(AreaOfStudy).where(
            AreaOfStudy.aos_code == code.upper(), AreaOfStudy.academic_year == year
        )
    )


def _write_containers(
    db: Session,
    nodes: list[dict[str, Any]],
    *,
    course_id: int | None = None,
    aos_id: int | None = None,
    parent_id: int | None = None,
) -> None:
    """Depth-first, so a child is written after the parent it points at."""
    for order, node in enumerate(nodes):
        container = CurriculumContainer(
            # Every node carries its owner, root or not. It costs one column
            # and buys "all containers of this course" as a single indexed
            # query; the roots are the ones with no parent, which is what the
            # ``containers`` relationship selects.
            course_id=course_id,
            area_of_study_id=aos_id,
            parent_id=parent_id,
            title=node.get("title"),
            description=node.get("description"),
            footnote=node.get("footnote"),
            credit_points=node.get("credit_points"),
            credit_points_max=node.get("credit_points_max"),
            connector=node.get("connector"),
            order_index=order,
        )
        db.add(container)
        db.flush()
        for index, item in enumerate(node.get("items") or []):
            db.add(
                CurriculumItem(
                    container_id=container.id,
                    item_code=item["item_code"],
                    item_name=item.get("item_name"),
                    item_type=item.get("item_type"),
                    item_url=item.get("item_url"),
                    credit_points=item.get("credit_points"),
                    connector=item.get("connector"),
                    order_index=index,
                )
            )
        _write_containers(
            db, node.get("containers") or [],
            course_id=course_id, aos_id=aos_id, parent_id=container.id,
        )


def _clear_containers(db: Session, *, course_id: int | None, aos_id: int | None) -> None:
    column = (
        CurriculumContainer.course_id == course_id
        if course_id is not None
        else CurriculumContainer.area_of_study_id == aos_id
    )
    for root in db.scalars(select(CurriculumContainer).where(column)):
        db.delete(root)  # cascades to children and items
    db.flush()


def upsert_course(db: Session, record: dict[str, Any]) -> tuple[Course, str]:
    """Insert or refresh one course. Returns ``(course, outcome)``."""
    now = datetime.now(UTC)
    course = get_course(db, record["course_code"], record["academic_year"])

    if course is not None and course.content_hash == record["content_hash"]:
        course.last_seen = now
        course.last_crawled = now
        course.is_active = True
        db.flush()
        return course, "unchanged"

    outcome = "changed" if course else "new"
    if course is None:
        course = Course(
            course_code=record["course_code"],
            academic_year=record["academic_year"],
            content_hash=record["content_hash"],
            first_seen=now,
        )
        db.add(course)

    for field in COURSE_FIELDS:
        setattr(course, field, record.get(field))
    course.last_seen = now
    course.last_crawled = now
    course.is_active = True
    db.flush()

    _clear_containers(db, course_id=course.id, aos_id=None)
    _write_containers(db, record.get("containers") or [], course_id=course.id)
    db.flush()
    return course, outcome


def upsert_area_of_study(db: Session, record: dict[str, Any]) -> tuple[AreaOfStudy, str]:
    """Insert or refresh one major, minor or specialisation."""
    now = datetime.now(UTC)
    aos = get_area_of_study(db, record["aos_code"], record["academic_year"])

    if aos is not None and aos.content_hash == record["content_hash"]:
        aos.last_seen = now
        aos.last_crawled = now
        aos.is_active = True
        db.flush()
        return aos, "unchanged"

    outcome = "changed" if aos else "new"
    if aos is None:
        aos = AreaOfStudy(
            aos_code=record["aos_code"],
            academic_year=record["academic_year"],
            content_hash=record["content_hash"],
            first_seen=now,
        )
        db.add(aos)

    for field in AOS_FIELDS:
        setattr(aos, field, record.get(field))
    aos.last_seen = now
    aos.last_crawled = now
    aos.is_active = True
    db.flush()

    _clear_containers(db, course_id=None, aos_id=aos.id)
    _write_containers(db, record.get("containers") or [], aos_id=aos.id)
    db.flush()
    return aos, outcome
