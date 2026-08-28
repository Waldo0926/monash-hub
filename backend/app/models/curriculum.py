"""Course and area-of-study tables.

A unit is a leaf; a course is the tree that says which leaves you need. The
Handbook publishes that tree as nested requirement containers - C2001's Part A
to Part E, each holding units or pointing at a specialisation - and the shape is
identical on an area-of-study page one level down.

So the containers are one pair of tables serving both parents, with exactly one
of ``course_id`` and ``area_of_study_id`` set. Two parallel container tables
would mean two copies of every walk over them, and the walks are the part worth
getting right.

The nesting is kept rather than flattened. "You must complete one of the
following options" is a claim about a group, and the same units listed without
their group read as "all of the following" - a different degree, and one the
student cannot finish.
"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Course(Base):
    """A degree: C2001, Bachelor of Computer Science."""

    __tablename__ = "courses"
    __table_args__ = (
        UniqueConstraint("course_code", "academic_year", name="uq_courses_code_year"),
        Index("ix_courses_campuses", "campuses", postgresql_using="gin"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    course_code: Mapped[str] = mapped_column(String(16), index=True)
    academic_year: Mapped[int] = mapped_column(Integer, index=True)
    title: Mapped[str] = mapped_column(String(300))
    abbreviated_name: Mapped[str | None] = mapped_column(String(64))
    credit_points: Mapped[int | None] = mapped_column(Integer)
    cricos_code: Mapped[str | None] = mapped_column(String(32))
    # Two levels concatenated on a double degree: "Level 9 - Master's Degree
    # (Coursework) / Level 9 - Master's Degree (Coursework)" is 79 characters.
    aqf_level: Mapped[str | None] = mapped_column(String(200))
    course_type: Mapped[str | None] = mapped_column(String(64), index=True)
    faculty: Mapped[str | None] = mapped_column(String(200), index=True)
    school: Mapped[str | None] = mapped_column(String(200))

    # Which campuses teach it. A Malaysia student filtering the course list on
    # this is the difference between a menu and a menu they can order from.
    campuses: Mapped[list[str]] = mapped_column(ARRAY(String(64)), default=list)
    duration_years: Mapped[int | None] = mapped_column(Integer)

    overview: Mapped[str | None] = mapped_column(Text)
    structure_text: Mapped[str | None] = mapped_column(Text)
    requirements_text: Mapped[str | None] = mapped_column(Text)

    handbook_version: Mapped[str | None] = mapped_column(String(32))
    source_url: Mapped[str] = mapped_column(String(500))
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_crawled: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    containers: Mapped[list["CurriculumContainer"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="CurriculumContainer.order_index",
        primaryjoin=(
            "and_(Course.id == CurriculumContainer.course_id, "
            "CurriculumContainer.parent_id.is_(None))"
        ),
    )


class AreaOfStudy(Base):
    """A major, minor or specialisation: DATASCI11, Data science."""

    __tablename__ = "areas_of_study"
    __table_args__ = (
        UniqueConstraint("aos_code", "academic_year", name="uq_aos_code_year"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    aos_code: Mapped[str] = mapped_column(String(24), index=True)
    academic_year: Mapped[int] = mapped_column(Integer, index=True)
    title: Mapped[str] = mapped_column(String(300))
    aos_type: Mapped[str | None] = mapped_column(String(64), index=True)
    study_level: Mapped[str | None] = mapped_column(String(64))
    credit_points: Mapped[int | None] = mapped_column(Integer)
    faculty: Mapped[str | None] = mapped_column(String(200), index=True)
    school: Mapped[str | None] = mapped_column(String(200))
    overview: Mapped[str | None] = mapped_column(Text)

    handbook_version: Mapped[str | None] = mapped_column(String(32))
    source_url: Mapped[str] = mapped_column(String(500))
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_crawled: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    containers: Mapped[list["CurriculumContainer"]] = relationship(
        back_populates="area_of_study",
        cascade="all, delete-orphan",
        order_by="CurriculumContainer.order_index",
        primaryjoin=(
            "and_(AreaOfStudy.id == CurriculumContainer.area_of_study_id, "
            "CurriculumContainer.parent_id.is_(None))"
        ),
    )


class CurriculumContainer(Base):
    """One requirement group - "Part A. Foundation studies", 42 points."""

    __tablename__ = "curriculum_containers"
    __table_args__ = (
        # Exactly one parent. A container belonging to both, or to neither,
        # would be reachable from a tree it does not describe.
        CheckConstraint(
            "(course_id IS NULL) <> (area_of_study_id IS NULL)",
            name="ck_curriculum_containers_one_parent",
        ),
        Index("ix_curriculum_containers_parent", "parent_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int | None] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), index=True
    )
    area_of_study_id: Mapped[int | None] = mapped_column(
        ForeignKey("areas_of_study.id", ondelete="CASCADE"), index=True
    )
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("curriculum_containers.id", ondelete="CASCADE")
    )

    title: Mapped[str | None] = mapped_column(String(300))
    description: Mapped[str | None] = mapped_column(Text)
    footnote: Mapped[str | None] = mapped_column(Text)
    credit_points: Mapped[int | None] = mapped_column(Integer)
    credit_points_max: Mapped[int | None] = mapped_column(Integer)
    connector: Mapped[str | None] = mapped_column(String(8))
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    course: Mapped["Course | None"] = relationship(
        back_populates="containers", foreign_keys=[course_id]
    )
    area_of_study: Mapped["AreaOfStudy | None"] = relationship(
        back_populates="containers", foreign_keys=[area_of_study_id]
    )
    children: Mapped[list["CurriculumContainer"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
        order_by="CurriculumContainer.order_index",
    )
    parent: Mapped["CurriculumContainer | None"] = relationship(
        back_populates="children", remote_side=[id]
    )
    items: Mapped[list["CurriculumItem"]] = relationship(
        back_populates="container",
        cascade="all, delete-orphan",
        order_by="CurriculumItem.order_index",
    )


class CurriculumItem(Base):
    """One thing a requirement group points at - a unit, or another structure."""

    __tablename__ = "curriculum_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    container_id: Mapped[int] = mapped_column(
        ForeignKey("curriculum_containers.id", ondelete="CASCADE"), index=True
    )

    item_code: Mapped[str] = mapped_column(String(24), index=True)
    item_name: Mapped[str | None] = mapped_column(String(300))
    # "unit", "minor", "specialisation" - what to resolve the code against.
    item_type: Mapped[str | None] = mapped_column(String(32), index=True)
    item_url: Mapped[str | None] = mapped_column(String(500))
    credit_points: Mapped[int | None] = mapped_column(Integer)
    connector: Mapped[str | None] = mapped_column(String(8))
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    container: Mapped[CurriculumContainer] = relationship(back_populates="items")
