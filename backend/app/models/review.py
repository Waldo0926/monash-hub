"""Student ratings of units.

A rating is community content, the same as a forum post: it is labelled as
such wherever it is shown and never mixed into the Handbook fields beside it.

One row per student per unit. Rating a unit again edits the row rather than
adding a second, so the average is "what the people who took it think", not
"what the most persistent person thinks".

Signing in is not needed to rate. A signed-out rating belongs to a browser
instead of an account: the browser makes up a random key once and sends it
with each rating, and the row keeps a keyed hash of it (``guest_key``). That
is what lets the same browser edit or remove its rating later, and what stops
it rating the same unit twice. It is weaker than an account, so signed-out
ratings are also limited per network; see app/api/v1/reviews.py.

The unit code is stored, not a foreign key to ``units``. A unit row belongs to
one Handbook year and is replaced every year; a rating is about the unit, and
must survive the next crawl.
"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

# Every score is 1 to 5. For teaching, content and assessment 5 is best; for
# difficulty and workload 5 is "hardest" and "heaviest", which is neither good
# nor bad, so those two are never folded into the overall average.
SCORES = ("overall", "teaching", "content", "assessment", "difficulty", "workload")


class UnitReview(Base):
    __tablename__ = "unit_reviews"
    __table_args__ = (
        UniqueConstraint("author_id", "unit_code", name="uq_unit_review_once"),
        UniqueConstraint("guest_key", "unit_code", name="uq_unit_review_guest_once"),
        # Every rating belongs to an account or to a browser, never to nobody,
        # or it could never be edited or removed by whoever wrote it.
        CheckConstraint(
            "author_id IS NOT NULL OR guest_key IS NOT NULL", name="ck_unit_review_owner"),
        # The unit page lists visible reviews newest first and averages them.
        Index("ix_unit_reviews_unit_feed", "unit_code", "is_hidden", "updated_at"),
        *(
            CheckConstraint(
                f"{name} BETWEEN 1 AND 5" if name == "overall"
                else f"{name} IS NULL OR {name} BETWEEN 1 AND 5",
                name=f"ck_unit_review_{name}",
            )
            for name in SCORES
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    unit_code: Mapped[str] = mapped_column(String(16))
    author_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True)
    guest_key: Mapped[str | None] = mapped_column(String(64))

    overall: Mapped[int] = mapped_column(SmallInteger)
    teaching: Mapped[int | None] = mapped_column(SmallInteger)
    content: Mapped[int | None] = mapped_column(SmallInteger)
    assessment: Mapped[int | None] = mapped_column(SmallInteger)
    difficulty: Mapped[int | None] = mapped_column(SmallInteger)
    workload: Mapped[int | None] = mapped_column(SmallInteger)

    body: Mapped[str | None] = mapped_column(Text)
    # When the student took it, as they say. Optional, and not checked against
    # the Handbook: a unit taken in 2023 is still worth hearing about.
    taken_year: Mapped[int | None] = mapped_column(Integer)
    taken_period: Mapped[str | None] = mapped_column(String(120))
    campus: Mapped[str | None] = mapped_column(String(64))

    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    author: Mapped["object"] = relationship("User", lazy="joined")
