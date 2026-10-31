"""What people search for, counted by day.

One row per term per day, holding only the term and how many times it was
searched that day. Nothing says who searched: no address, no account, no
session, no time finer than the day. The home page reads the rows to show
what people have been looking up lately instead of a list someone typed in.

A term gets a row only when the search found something (see
app/search/popular.py), so a mistyped code or a name does not end up here.
"""
from datetime import date

from sqlalchemy import Date, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class SearchTerm(Base):
    __tablename__ = "search_terms"
    __table_args__ = (UniqueConstraint("term", "day", name="uq_search_terms_term_day"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # The term in lower case with its spaces collapsed, which is what makes
    # "fit2004", "FIT2004" and "FIT2004 " one row.
    term: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    # How it is shown: a unit or course code in capitals, anything else as
    # the first person that day typed it.
    label: Mapped[str] = mapped_column(String(80), nullable=False)
    day: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    hits: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
