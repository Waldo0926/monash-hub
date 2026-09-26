"""Handbook tables.

Every row is scoped by ``academic_year`` from day one: the MVP only loads 2026,
but backfilling 2025 later must not mean a schema change. ``content_hash`` is
what the sync pipeline compares, so an unchanged page costs no parse and no
write.
"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Computed,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Unit(Base):
    __tablename__ = "units"
    __table_args__ = (
        UniqueConstraint("unit_code", "academic_year", name="uq_units_code_year"),
        Index("ix_units_search_vector", "search_vector", postgresql_using="gin"),
        Index(
            "ix_units_title_trgm",
            "title",
            postgresql_using="gin",
            postgresql_ops={"title": "gin_trgm_ops"},
        ),
        Index(
            "ix_units_search_zh_trgm",
            "search_zh",
            postgresql_using="gin",
            postgresql_ops={"search_zh": "gin_trgm_ops"},
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Identity
    unit_code: Mapped[str] = mapped_column(String(16), index=True)
    academic_year: Mapped[int] = mapped_column(Integer, index=True)
    title: Mapped[str] = mapped_column(String(300))
    credit_points: Mapped[str | None] = mapped_column(String(16))
    level: Mapped[str | None] = mapped_column(String(64))
    faculty: Mapped[str | None] = mapped_column(String(200), index=True)
    school: Mapped[str | None] = mapped_column(String(200))
    subject_prefix: Mapped[str | None] = mapped_column(String(8), index=True)
    source_url: Mapped[str] = mapped_column(String(500))

    # Overview
    overview: Mapped[str | None] = mapped_column(Text)
    areas_of_study: Mapped[str | None] = mapped_column(Text)
    teaching_approach: Mapped[str | None] = mapped_column(Text)
    workload_requirements: Mapped[str | None] = mapped_column(Text)
    assessment_summary: Mapped[str | None] = mapped_column(Text)
    assessment_static_text: Mapped[str | None] = mapped_column(Text)

    # Derived flags the Unit Search filters use. ``has_exam`` stays nullable on
    # purpose: "the Handbook does not list one" is not the same claim as "there
    # is no exam", and the UI must be able to tell them apart.
    has_exam: Mapped[bool | None] = mapped_column(Boolean, index=True)

    # Versioning
    handbook_version: Mapped[str | None] = mapped_column(String(32))
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_crawled: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Maintained by PostgreSQL itself. A generated column cannot drift out of
    # sync with the row the way a trigger or an application-side update can.
    # Every Chinese string this row has, flattened out of content_translations
    # where an index can reach it. PostgreSQL cannot tokenise Chinese without a
    # server-side extension we cannot install, so this is matched with pg_trgm
    # rather than tsvector - which for a language with no word boundaries is the
    # right query anyway. Filled by `python -m app.search.reindex_zh`, never by
    # a generated column: the text it comes from lives in another table.
    search_zh: Mapped[str | None] = mapped_column(Text)

    search_vector: Mapped[str | None] = mapped_column(
        TSVECTOR,
        Computed(
            # Code and title A, areas of study B, overview D: "algorithms"
            # should put units called that above units whose prose uses it.
            "setweight(to_tsvector('english', coalesce(unit_code, '') || ' ' || "
            "coalesce(title, '')), 'A') || "
            "setweight(to_tsvector('english', coalesce(areas_of_study, '')), 'B') || "
            "setweight(to_tsvector('english', coalesce(overview, '')), 'D')",
            persisted=True,
        ),
    )

    offerings: Mapped[list["UnitOffering"]] = relationship(
        back_populates="unit", cascade="all, delete-orphan", order_by="UnitOffering.id")
    assessments: Mapped[list["UnitAssessment"]] = relationship(
        back_populates="unit", cascade="all, delete-orphan", order_by="UnitAssessment.number")
    requisite_groups: Mapped[list["UnitRequisiteGroup"]] = relationship(
        back_populates="unit",
        cascade="all, delete-orphan",
        order_by="UnitRequisiteGroup.order_index",
        primaryjoin=(
            "and_(Unit.id == UnitRequisiteGroup.unit_id, "
            "UnitRequisiteGroup.parent_id.is_(None))"
        ),
    )
    learning_outcomes: Mapped[list["UnitLearningOutcome"]] = relationship(
        back_populates="unit",
        cascade="all, delete-orphan",
        order_by="UnitLearningOutcome.number",
    )
    activities: Mapped[list["UnitActivity"]] = relationship(
        back_populates="unit", cascade="all, delete-orphan", order_by="UnitActivity.id")
    versions: Mapped[list["UnitVersion"]] = relationship(
        back_populates="unit", cascade="all, delete-orphan", order_by="UnitVersion.id")


class UnitVersion(Base):
    """One row per distinct ``content_hash`` we have ever seen for a unit."""

    __tablename__ = "unit_versions"
    __table_args__ = (
        UniqueConstraint("unit_id", "content_hash", name="uq_unit_versions_unit_hash"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id", ondelete="CASCADE"), index=True)
    version_name: Mapped[str | None] = mapped_column(String(32))
    content_hash: Mapped[str] = mapped_column(String(64))
    raw_payload: Mapped[dict] = mapped_column(JSONB)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    unit: Mapped[Unit] = relationship(back_populates="versions")


class UnitOffering(Base):
    __tablename__ = "unit_offerings"

    id: Mapped[int] = mapped_column(primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id", ondelete="CASCADE"), index=True)
    offering_code: Mapped[str | None] = mapped_column(String(120))
    display_name: Mapped[str | None] = mapped_column(String(200))
    campus: Mapped[str | None] = mapped_column(String(120), index=True)
    teaching_period: Mapped[str | None] = mapped_column(String(120), index=True)
    attendance_mode: Mapped[str | None] = mapped_column(String(120))
    study_level: Mapped[str | None] = mapped_column(String(120))
    offered: Mapped[bool] = mapped_column(Boolean, default=True)

    unit: Mapped[Unit] = relationship(back_populates="offerings")


class UnitAssessment(Base):
    __tablename__ = "unit_assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id", ondelete="CASCADE"), index=True)
    number: Mapped[int | None] = mapped_column(Integer)
    name: Mapped[str | None] = mapped_column(String(400))
    assessment_type: Mapped[str | None] = mapped_column(String(120), index=True)
    weight: Mapped[str | None] = mapped_column(String(64))
    hurdle: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    learning_outcomes: Mapped[str | None] = mapped_column(String(120))
    offering_scope: Mapped[str | None] = mapped_column(Text)

    unit: Mapped[Unit] = relationship(back_populates="assessments")


class UnitRequisiteGroup(Base):
    """A prerequisite/corequisite/prohibition block, and its nesting.

    The Handbook nests containers joined by AND/OR, and the nesting is the
    rule. FIT2099 asks for one of six programming units *or* an engineering
    pair, and flattened into siblings that reads as "all of the above": the
    planner told a student who had passed FIT1045 that they still needed two
    ENG units they will never take.

    So ``parent_id`` keeps the tree. A group with no parent is a top-level
    alternative; ``connector`` says how a group combines with its siblings.
    """

    __tablename__ = "unit_requisite_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id", ondelete="CASCADE"), index=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("unit_requisite_groups.id", ondelete="CASCADE"), index=True
    )
    requisite_type: Mapped[str] = mapped_column(String(40), index=True)
    connector: Mapped[str | None] = mapped_column(String(8))
    title: Mapped[str | None] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text)
    raw_text: Mapped[str | None] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    unit: Mapped[Unit] = relationship(back_populates="requisite_groups")
    items: Mapped[list["UnitRequisiteItem"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
        order_by="UnitRequisiteItem.order_index",
    )
    children: Mapped[list["UnitRequisiteGroup"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
        order_by="UnitRequisiteGroup.order_index",
    )
    parent: Mapped["UnitRequisiteGroup | None"] = relationship(
        back_populates="children", remote_side=[id]
    )


class UnitRequisiteItem(Base):
    __tablename__ = "unit_requisite_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("unit_requisite_groups.id", ondelete="CASCADE"), index=True)
    item_code: Mapped[str | None] = mapped_column(String(32), index=True)
    item_name: Mapped[str | None] = mapped_column(String(300))
    item_type: Mapped[str | None] = mapped_column(String(40))
    item_url: Mapped[str | None] = mapped_column(String(500))
    credit_points: Mapped[str | None] = mapped_column(String(16))
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    group: Mapped[UnitRequisiteGroup] = relationship(back_populates="items")


class UnitLearningOutcome(Base):
    __tablename__ = "unit_learning_outcomes"

    id: Mapped[int] = mapped_column(primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id", ondelete="CASCADE"), index=True)
    code: Mapped[str | None] = mapped_column(String(16))
    number: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)

    unit: Mapped[Unit] = relationship(back_populates="learning_outcomes")


class UnitActivity(Base):
    __tablename__ = "unit_activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id", ondelete="CASCADE"), index=True)
    activity_type: Mapped[str | None] = mapped_column(String(120))
    name: Mapped[str | None] = mapped_column(String(300))
    description: Mapped[str | None] = mapped_column(Text)

    unit: Mapped[Unit] = relationship(back_populates="activities")
