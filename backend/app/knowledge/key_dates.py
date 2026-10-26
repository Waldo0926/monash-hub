"""Upcoming key dates, read out of official date pages the index already holds.

Nothing here fetches anything. The census-dates, final-assessment-dates and
the two principal-dates pages are already seeded on the ``dynamic`` refresh
tier; this module only reads the table blocks the cleaner stored for them and
turns the rows a student acts on into dated items.

What is read, and from where:

- census-dates: one row per teaching period, six cells -
  ``period | dates | census | first day Withdrawn shows | last day before
  Withdrawn Fail | last day to withdraw``. We take the census date, the last
  day a withdrawal stays a plain Withdrawn, and the last column, which is the
  day teaching ends.
- final-assessment-dates: one row per teaching period, five cells -
  ``period | swot vac | timetable release | final assessment period | results``.
- principal dates (Malaysia and Australia): ``Day | Date | Description`` rows
  under month headings. Only the "University closed" rows are taken - the
  public holidays - because every academic date in them is also in the two
  tables above, in a shape that does not need guessing.
- allocate-dates: one tab per campus, a card per teaching period ("Semester
  one 2027"), and a bold label over a date on each line - "Preference entry
  closes / Tuesday 19 January, 5pm". The year is usually only in the card
  title, so the printed weekday decides it.
- dates-wes-access: a list of "semester one (S1-01) 2027, you can enrol in
  units from 12 October 2026" - the day WES opens for a first enrolment. The
  page has no campus tabs and sits on monash.edu, so it is listed for
  Australia only.
- malaysia-re-enrol: a two-column table on monash.edu.my, "On-time
  re-enrolment: / 12 October - 27 November 2026" and "Late re-enrolment via
  WES: / 28 November - 11 December 2026" - when continuing Malaysia students
  pick next year's units in WES. Malaysia only.

The parsers are pure: rows in, items out. Anything that does not parse is
skipped rather than approximated; a date we are unsure of is worse than a
date we leave out, because a student plans around it.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge import OfficialPage

CENSUS = "census-dates"
FINALS = "final-assessment-dates"
ALLOCATE = "allocate-dates"
WES = "dates-wes-access"
REENROL_MY = "malaysia-re-enrol"
PRINCIPAL = {
    "malaysia": "malaysia-principal-dates-for-monash-university-malay",
    "australia": "principal-dates",
}
TIMEZONE = {
    "malaysia": ZoneInfo("Asia/Kuala_Lumpur"),
    "australia": ZoneInfo("Australia/Melbourne"),
}

# The teaching periods most students are enrolled in at each campus. The tables
# carry dozens more (Monash Online, Indonesia terms, research quarters); listing
# all of them would bury the two dates a first-year actually needs.
PERIODS = {
    "malaysia": ("S1-01", "S2-01", "OCT-MY-01"),
    "australia": ("S1-01", "S2-01"),
}

MONTHS = {m: i for i, m in enumerate(
    ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"), 1)}
WEEKDAYS = {d: i for i, d in enumerate(("mon", "tue", "wed", "thu", "fri", "sat", "sun"))}

_CODE = re.compile(r"\(([A-Z0-9]+(?:-[A-Z0-9]+)+)\)")
_DASH = re.compile(r"\s*[–—-]\s*")
_PAREN = re.compile(r"\([^)]*\)")
_WEEKDAY_WORD = re.compile(r"\b(?:mon|tue|wed|thu|fri|sat|sun)[a-z]*\b\.?", re.I)


@dataclass(frozen=True)
class KeyDate:
    start: date
    end: date | None
    # census | withdraw | teaching_end | swot_vac | exams | results | holiday |
    # allocate_pref_open | allocate_pref_close | allocate_adjust_open |
    # allocate_adjust_close | wes_open | reenrol | reenrol_late
    kind: str
    source: str
    period: str | None = None
    name: str | None = None
    time: str | None = None  # "17:00", only where the page prints a time

    def as_dict(self) -> dict:
        return {
            "date": self.start.isoformat(),
            "end": self.end.isoformat() if self.end else None,
            "kind": self.kind,
            "period": self.period,
            "name": self.name,
            "time": self.time,
            "source": self.source,
        }


def _month(word: str | None) -> int | None:
    return MONTHS.get((word or "")[:3].lower())


def parse_range(text: str) -> tuple[date, date | None] | None:
    """``31 Aug 2026``, ``Sat 28 Nov 2026``, ``2–18 Nov 2026``, ``30 Oct – 17 Nov 2028``.

    Returns ``(start, end)``; ``end`` is None for a single day. N/A, TBA,
    Varied and anything else unreadable return None.
    """
    s = _PAREN.sub("", text or "")
    s = _WEEKDAY_WORD.sub("", s)
    s = _DASH.sub("–", s.strip())
    s = re.sub(r"\s+", " ", s).replace(",", "")
    try:
        m = re.fullmatch(r"(\d{1,2}) ([A-Za-z]+) (\d{4})", s)
        if m and _month(m[2]):
            return date(int(m[3]), _month(m[2]), int(m[1])), None
        m = re.fullmatch(
            r"(\d{1,2})(?: ([A-Za-z]+))?(?: (\d{4}))?–(\d{1,2}) ([A-Za-z]+) (\d{4})", s)
        if m and _month(m[5]) and (m[2] is None or _month(m[2])):
            end = date(int(m[6]), _month(m[5]), int(m[4]))
            start_month = _month(m[2]) if m[2] else end.month
            start_year = int(m[3]) if m[3] else (
                end.year - 1 if start_month > end.month else end.year)
            return date(start_year, start_month, int(m[1])), end
    except ValueError:
        return None
    return None


def _period_code(cell: str) -> str | None:
    m = _CODE.search(cell or "")
    return m[1] if m else None


def parse_census(rows: list[list[str]], source: str = CENSUS) -> list[KeyDate]:
    out: list[KeyDate] = []
    for row in rows:
        if len(row) != 6:
            continue
        code = _period_code(row[0])
        census = parse_range(row[2])
        if not code or not census:
            continue
        out.append(KeyDate(census[0], None, "census", source, code))
        for kind, cell in (("withdraw", row[4]), ("teaching_end", row[5])):
            parsed = parse_range(cell)
            if parsed:
                out.append(KeyDate(parsed[0], None, kind, source, code))
    return out


def parse_finals(rows: list[list[str]], source: str = FINALS) -> list[KeyDate]:
    out: list[KeyDate] = []
    for row in rows:
        # The 2024 tables put the code in a column of its own; those years are
        # past, and a row whose second cell is a code is not this shape.
        if len(row) != 5 or _CODE.fullmatch(f"({row[1].strip()})"):
            continue
        code = _period_code(row[0])
        if not code:
            continue
        for kind, cell in (("swot_vac", row[1]), ("exams", row[3]), ("results", row[4])):
            parsed = parse_range(cell)
            if parsed:
                out.append(KeyDate(parsed[0], parsed[1], kind, source, code))
    return out


_ALLOCATE_KINDS = {
    "preference entry opens": "allocate_pref_open",
    "preference entry closes": "allocate_pref_close",
    # The OCT-MY-01 card says "open"; the others say "opens".
    "allocation adjustment opens": "allocate_adjust_open",
    "allocation adjustment open": "allocate_adjust_open",
    "allocation adjustment closes": "allocate_adjust_close",
    "allocation adjustment close": "allocate_adjust_close",
}
_SEMESTER = {"one": "S1-01", "two": "S2-01"}
_ALLOCATE_DATE = re.compile(
    r"(?:([A-Za-z]+)\s+)?(\d{1,2})\s+([A-Za-z]+)(?:\s+(\d{4}))?"
    r"(?:,\s*(\d{1,2})(?:[:.](\d{2}))?\s*([ap]m))?(?:\s*\([A-Z]{2,5}\))?\.?"
)


def _card_period(title: str) -> str | None:
    """``Semester one 2027`` is S1-01; a title with a code in brackets is that code."""
    code = _period_code(title)
    if code:
        return code
    m = re.match(r"\s*semester\s+(one|two)\b", title, re.I)
    return _SEMESTER[m[1].lower()] if m else None


def parse_allocate_line(text: str, years: list[int]) -> tuple[date, str | None] | None:
    """``Tuesday 19 January, 5pm`` or ``Monday 9 November 2026, 5pm (MYT)``.

    With no year printed, the year is one the card title names (or, for an
    October to December date, the one before it - a preference round that
    opens before the year starts) on which the printed weekday falls. A line
    that fits none of them, or more than one, is left out.
    """
    m = _ALLOCATE_DATE.fullmatch(" ".join((text or "").split()))
    if not m or not _month(m[3]):
        return None
    weekday = WEEKDAYS.get((m[1] or "")[:3].lower()) if m[1] else None
    if m[1] and weekday is None:
        return None
    month, day = _month(m[3]), int(m[2])
    if m[4]:
        candidates = [int(m[4])]
    elif weekday is not None and years:
        candidates = sorted(set(years) | ({min(years) - 1} if month >= 10 else set()))
    else:
        return None
    fits = []
    for year in candidates:
        try:
            d = date(year, month, day)
        except ValueError:
            continue
        if weekday is None or d.weekday() == weekday:
            fits.append(d)
    if len(fits) != 1:
        return None
    time = None
    if m[5]:
        hour = int(m[5]) % 12 + (12 if m[7].lower() == "pm" else 0)
        time = f"{hour:02d}:{m[6] or '00'}"
    return fits[0], time


def parse_allocate(blocks: list[dict], source: str = ALLOCATE) -> dict[str, list[KeyDate]]:
    """Allocate+ dates by campus tab: ``{"australia": [...], "malaysia": [...]}``."""
    out: dict[str, list[KeyDate]] = {}
    campus = period = None
    years: list[int] = []
    for block in blocks:
        if block.get("type") == "heading":
            text = (block.get("text") or "").strip()
            if block.get("variant") == "tab":
                campus = text.lower() if text.lower() in TIMEZONE else None
                period, years = None, []
            elif block.get("level", 2) >= 3:
                period = _card_period(text)
                years = [int(y) for y in re.findall(r"\b(20\d{2})\b", text)]
            continue
        spans = block.get("spans") or []
        if block.get("type") != "paragraph" or not campus or not period or not spans:
            continue
        if not spans[0].get("bold"):
            continue
        kind = _ALLOCATE_KINDS.get(" ".join(spans[0].get("text", "").split()).lower())
        if not kind:
            continue
        rest = "".join(sp.get("text", "") for sp in spans[1:]).strip()
        parsed = parse_allocate_line(rest, years)
        if parsed:
            out.setdefault(campus, []).append(
                KeyDate(parsed[0], None, kind, source, period, time=parsed[1]))
    return out


_WES_ITEM = re.compile(
    r"\(([A-Z0-9]+(?:-[A-Z0-9]+)*)\)\s*\d{4}(?:\s*[–—-]\s*\d{4})?\s*,"
    r".*?\bfrom\s+(\d{1,2}\s+[A-Za-z]+\s+\d{4})\.?\s*$",
    re.I,
)


def parse_wes(blocks: list[dict], source: str = WES) -> list[KeyDate]:
    """First-enrolment WES opening days from the list on dates-wes-access."""
    out: list[KeyDate] = []
    for block in blocks:
        if block.get("type") != "list":
            continue
        for item in block.get("items") or []:
            text = " ".join("".join(sp.get("text", "") for sp in item).split())
            m = _WES_ITEM.search(text)
            if not m:
                continue
            parsed = parse_range(m[2])
            if parsed and parsed[1] is None:
                out.append(KeyDate(parsed[0], None, "wes_open", source, m[1]))
    return out


_REENROL = (
    (re.compile(r"on-?time re-?enrol", re.I), "reenrol"),
    (re.compile(r"late re-?enrol", re.I), "reenrol_late"),
)


def parse_reenrol(rows: list[list[str]], source: str = REENROL_MY) -> list[KeyDate]:
    """``On-time re-enrolment:\n12 October - 27 November 2026`` and the late row.

    The label and the dates share the first cell. A row whose dates are not a
    plain range ("Friday 11 December 2026 (subject to school's approval)") is
    not a window and is left out.
    """
    out: list[KeyDate] = []
    for row in rows:
        if not row:
            continue
        label, _, rest = row[0].partition(":")
        kind = next((k for pattern, k in _REENROL if pattern.search(label)), None)
        parsed = parse_range(rest) if kind else None
        if kind and parsed and parsed[1]:
            out.append(KeyDate(parsed[0], parsed[1], kind, source))
    return out


def _calendar_rows(rows: list[list[str]]):
    """Yield ``("month", month, year|None)`` and ``("day", weekday, day, text)``.

    Two layouts exist: ``[Mon, 6, text]`` on monash.edu.my and ``[Mon 05, text]``
    on monash.edu. Month headings are a row whose first cell is a month name,
    with or without a year, and nothing else.
    """
    for row in rows:
        cells = [c.strip() for c in row]
        if not cells or not cells[0]:
            continue
        head = re.fullmatch(r"([A-Za-z]+)(?: (\d{4}))?", cells[0])
        if head and _month(head[1]) and not any(cells[1:]) and len(head[1]) >= 3:
            yield "month", _month(head[1]), int(head[2]) if head[2] else None
            continue
        if len(cells) >= 3 and cells[0][:3].lower() in WEEKDAYS and cells[1].isdigit():
            yield "day", WEEKDAYS[cells[0][:3].lower()], int(cells[1]), cells[2]
            continue
        m = re.fullmatch(r"([A-Za-z]{3})[a-z]* (\d{1,2})", cells[0])
        if m and m[1].lower() in WEEKDAYS and len(cells) >= 2:
            yield "day", WEEKDAYS[m[1].lower()], int(m[2]), cells[1]


def _walk(rows: list[list[str]], base_year: int):
    """Assign a year to every day row, starting from ``base_year``.

    A heading with a year resets it; a month earlier than the last one means
    the table crossed into January.
    """
    year, month = base_year, None
    for item in _calendar_rows(rows):
        if item[0] == "month":
            _, m, y = item
            if y is not None:
                year = y
            elif month is not None and m < month:
                year += 1
            month = m
            continue
        if month is None:
            continue
        _, weekday, day, text = item
        try:
            yield date(year, month, day), weekday, text
        except ValueError:
            continue


def _infer_year(rows: list[list[str]], around: int) -> int | None:
    """The base year under which the printed weekdays agree with the calendar.

    Most principal-dates tables head their months "October", not "October
    2026", and the year is only in a tab label the cleaner never sees. The
    weekday printed beside every date settles it: only one year in five puts
    them all on the right day.
    """
    best, best_score = None, 0.0
    for year in range(around - 2, around + 3):
        walked = list(_walk(rows, year))
        if not walked:
            return None
        score = sum(d.weekday() == wd for d, wd, _ in walked) / len(walked)
        if score > best_score:
            best, best_score = year, score
    return best if best_score >= 0.9 else None


def _holiday_name(text: str) -> str | None:
    m = re.match(r"\s*(?:University closed|Public holiday)\s*:\s*(.+)", text, re.I)
    if not m:
        return None
    name = re.sub(r"\s*\(University closed\)\s*", "", m[1]).strip().rstrip(".")
    # "University closed: Reopens Monday 4 January 2027" marks the start of the
    # Christmas closedown, not a holiday with a name.
    if not name or name.lower().startswith("reopen"):
        return None
    return name


_REPLACEMENT = re.compile(r"\s*\((?:[^)]*\s)?replacement(?: public)? holiday\)\s*$", re.I)


def parse_holidays(tables: list[list[list[str]]], source: str, around: int) -> list[KeyDate]:
    """Public holidays, with a replacement day folded into the holiday it replaces.

    "Deepavali" on a Sunday and "Deepavali (replacement holiday)" on the Monday
    are one holiday to a student - the Monday is the day off - so they come out
    as a single item spanning both days.
    """
    out: list[KeyDate] = []
    for rows in tables:
        year = _infer_year(rows, around)
        if year is None:
            continue
        for day, _, text in _walk(rows, year):
            name = _holiday_name(text)
            if not name:
                continue
            base = _REPLACEMENT.sub("", name)
            if base != name:
                for i in range(len(out) - 1, -1, -1):
                    prev = out[i]
                    if prev.name == base and 0 < (day - prev.start).days <= 3:
                        out[i] = KeyDate(prev.start, day, "holiday", source, name=base)
                        break
                else:
                    out.append(KeyDate(day, None, "holiday", source, name=base))
                continue
            out.append(KeyDate(day, None, "holiday", source, name=name))
    return out


def _blocks(page: OfficialPage | None) -> list[dict]:
    if page is None or page.status != "ok":
        return []
    return list(page.blocks or [])


def _tables(page: OfficialPage | None) -> list[list[list[str]]]:
    return [b.get("rows") or [] for b in _blocks(page) if b.get("type") == "table"]


def upcoming(
    pages: dict[str, OfficialPage | None], campus: str, today: date, limit: int
) -> list[KeyDate]:
    """Dates that have not finished yet, soonest first, at most ``limit``."""
    periods = PERIODS[campus]
    items: list[KeyDate] = []
    for rows in _tables(pages.get(CENSUS)):
        items += [k for k in parse_census(rows) if k.period in periods]
    for rows in _tables(pages.get(FINALS)):
        items += [k for k in parse_finals(rows) if k.period in periods]
    items += parse_holidays(_tables(pages.get(PRINCIPAL[campus])), PRINCIPAL[campus], today.year)
    allocate = parse_allocate(_blocks(pages.get(ALLOCATE))).get(campus, [])
    items += [k for k in allocate if k.period in periods]
    if campus == "australia":
        items += [k for k in parse_wes(_blocks(pages.get(WES))) if k.period in periods]
    else:
        for rows in _tables(pages.get(REENROL_MY)):
            items += parse_reenrol(rows)

    seen: set[tuple] = set()
    result: list[KeyDate] = []
    for k in sorted(items, key=lambda k: (k.start, k.kind, k.period or "", k.name or "")):
        key = (k.start, k.kind, k.period, k.name)
        if (k.end or k.start) < today or key in seen:
            continue
        seen.add(key)
        result.append(k)
    return result[:limit]


def collect(db: Session, campus: str, limit: int = 6, now: datetime | None = None) -> dict:
    slugs = (CENSUS, FINALS, PRINCIPAL[campus], ALLOCATE, WES, REENROL_MY)
    query = select(OfficialPage).where(OfficialPage.slug.in_(slugs))
    found = {p.slug: p for p in db.scalars(query)}
    pages = {slug: found.get(slug) for slug in slugs}
    today = (now or datetime.now(TIMEZONE[campus])).astimezone(TIMEZONE[campus]).date()
    items = upcoming(pages, campus, today, limit)
    used = {k.source for k in items}
    return {
        "campus": campus,
        "today": today.isoformat(),
        "items": [k.as_dict() for k in items],
        "sources": {
            slug: {
                "title": page.title,
                "url": page.canonical_url,
                "last_checked": page.last_checked.isoformat() if page.last_checked else None,
            }
            for slug, page in pages.items() if page is not None and slug in used
        },
    }
