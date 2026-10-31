"""Monash Malaysia tuition fees, read out of the two fee pages the index already holds.

Monash Malaysia publishes its fees on two pages, /ugfees and /pgfees, seeded as
``malaysia-ugfees`` and ``malaysia-pgfees``. Each school gets a heading and a
table under it. Nothing here fetches anything: this module reads the table
blocks the cleaner stored, so when Monash changes a fee the site follows on
the next refresh, and every amount shown keeps the page it came from and when
that page was last read.

What the tables look like:

- ``columns`` is the first header row. On /ugfees it says "Tuition fees per
  year (RM)", which is the only place the undergraduate page says per year.
- The first body row is the second header row, with "Malaysian" and
  "International" over the two fee columns. Their positions are read from it.
- /pgfees writes the basis into each fee cell: "57,600\\n(full course)" or
  "49,920\\n(per year)". Most coursework masters are a whole course price and
  the Master of Pharmaceutical Science is not, so the cell decides, never the
  table.
- The first cell can hold more than a title. "Bachelor of Arts and Social
  Sciences\\nMajors in: ..." lists majors, and Engineering's one row is
  "Bachelor of Engineering" followed by its eight honours degrees, one per
  line, all at the same fee. Every line that names a degree gets the row.
- A row with no title continues the one above (Monash English, 10 weeks).
- A cell can hold two prices with a label each: the DHES costs one amount for
  the non-science stream and another for the science stream.

An amount that does not read as a number is kept as written and flagged, not
guessed. In October 2026 /ugfees printed the Bachelor of Pharmacy (Honours)
international fee as "74,40". Showing 74,400 would be our guess, so the page
shows what Monash wrote and points at the source.

Each row also carries how it moved since last year. Last year's tables come
from the stored versions of the same two pages when the index has them, and
for 2026, which the index never saw, from Monash's printed 2026 fee tables in
``tuition_2026.py``.

Rows are matched to Handbook degrees on the English title. A title several
schools price (Doctor of Philosophy, Master of Philosophy) also needs the
school to agree with the degree's faculty, and a degree that matches nothing
gets no card rather than the fee of a different degree.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.knowledge import tuition_2026
from app.models.knowledge import OfficialPage, OfficialPageVersion

#: The indexed pages that carry the fee tables, undergraduate first.
SOURCES = ("malaysia-ugfees", "malaysia-pgfees")
LEVEL = {"malaysia-ugfees": "undergraduate", "malaysia-pgfees": "postgraduate"}

# School headings on the fee pages, matched in this order. Arts comes before
# Science because "School of Arts and Social Sciences" contains "Science".
SCHOOLS = (
    ("arts", "arts and social sciences"),
    ("business", "business"),
    ("engineering", "engineering"),
    ("it", "information technology"),
    ("medicine", "medicine"),
    ("pharmacy", "pharmacy"),
    ("science", "science"),
    ("other", "other courses"),
)

# Handbook faculty names for each school. The Handbook keeps the faculty's own
# name where Monash Malaysia says "School of".
FACULTIES: dict[str, tuple[str, ...]] = {
    "arts": ("Faculty of Arts",),
    "business": ("Faculty of Business and Economics", "Monash Business School"),
    "engineering": ("Faculty of Engineering",),
    "it": ("Faculty of Information Technology",),
    "medicine": ("Faculty of Medicine, Nursing and Health Sciences",
                 "Faculty of Medicine, Nursing and Health Science"),
    "pharmacy": ("Faculty of Pharmacy and Pharmaceutical Sciences",),
    "science": ("Faculty of Science",),
}

# Things the fee tables do not say and a student needs next to the number.
# Each one was checked against the official page named in its note on
# 2026-10-28. Keyed on the normalised title.
NOTES: dict[str, dict[str, str]] = {
    "bachelor of software engineering (honours)": {
        "en": "Monash Malaysia takes no new students into this degree from Semester 1, 2028.",
        "zh": "2028 年第 1 学期起不再招收新生。",
        "url": "https://www.monash.edu.my/study/undergraduate/engineering",
    },
    "bachelor of materials engineering (honours)": {
        "en": "The Malaysia fee covers the first two years. The last two are at Clayton and charged Australian fees.",
        "zh": "马来西亚学费只覆盖前两年，后两年在澳大利亚 Clayton 校区，按澳大利亚校区学费另计。",
        "url": "https://www.monash.edu.my/study/undergraduate/engineering/bachelor-of-materials-engineering-honours",
    },
    "bachelor of biomedical engineering (honours)": {
        "en": "The Malaysia fee covers the first two years. The last two are at Clayton and charged Australian fees.",
        "zh": "马来西亚学费只覆盖前两年，后两年在澳大利亚 Clayton 校区，按澳大利亚校区学费另计。",
        "url": "https://www.monash.edu.my/study/undergraduate/engineering/bachelor-of-biomedical-engineering-honours",
    },
}

# Malaysia degrees we know the fee pages leave out, so the card can say so
# instead of staying blank. Last year's fee is never shown in their place.
NOT_LISTED: dict[str, dict[str, str]] = {
    "master of professional counselling": {
        "en": "Not on the fee table, and the course page says applications are closed.",
        "zh": "官方收费表没有列出这门课程，课程页显示目前关闭申请。",
        "url": "https://www.monash.edu.my/study/postgraduate-and-research/medicine-health-sciences/master-of-professional-counselling",
    },
}

# Chinese names for the fees page, from the 2026-10-28 content handoff. A title
# missing here is shown in English, which is what the page says anyway.
TITLE_ZH: dict[str, str] = {
    "bachelor of arts and social sciences": "文学与社会科学学士",
    "bachelor of digital media and communication": "数字媒体与传播学士",
    "bachelor of arts (honours)": "文学荣誉学士",
    "bachelor of business and commerce": "商务与商业学士",
    "bachelor of digital business": "数字商务学士",
    "bachelor of actuarial analytics": "精算分析学士",
    "bachelor of business and commerce (honours)": "商务与商业荣誉学士",
    "bachelor of business and commerce and bachelor of computer science":
        "商务与商业 + 计算机科学双学士",
    "bachelor of business and commerce and bachelor of digital media and communication":
        "商务与商业 + 数字媒体与传播双学士",
    "bachelor of engineering": "工程学士",
    "bachelor of biomedical engineering (honours)": "生物医学工程学士（荣誉）",
    "bachelor of chemical engineering (honours)": "化学工程学士（荣誉）",
    "bachelor of civil engineering (honours)": "土木工程学士（荣誉）",
    "bachelor of electrical and computer systems engineering (honours)": "电气与计算机系统工程学士（荣誉）",
    "bachelor of materials engineering (honours)": "材料工程学士（荣誉）",
    "bachelor of mechanical engineering (honours)": "机械工程学士（荣誉）",
    "bachelor of robotics and mechatronics engineering (honours)": "机器人与机电工程学士（荣誉）",
    "bachelor of software engineering (honours)": "软件工程学士（荣誉）",
    "bachelor of computer science": "计算机科学学士",
    "bachelor of computer science in artificial intelligence": "人工智能计算机科学学士",
    "bachelor of computer science in data science": "数据科学计算机科学学士",
    "bachelor of computer science (honours)": "计算机科学荣誉学士",
    "bachelor of medical science and doctor of medicine": "医学学士及医学博士",
    "bachelor of psychology": "心理学学士",
    "bachelor of psychology and business": "心理学与商业学士",
    "bachelor of human nutrition": "人类营养学学士",
    "bachelor of health sciences (honours)": "健康科学荣誉学士",
    "bachelor of medical science (honours)": "医学科学荣誉学士",
    "bachelor of psychology (honours)": "心理学荣誉学士",
    "bachelor of pharmacy (honours)": "药剂学士（荣誉）",
    "bachelor of pharmaceutical science": "制药科学学士",
    "bachelor of pharmaceutical science (honours)": "制药科学荣誉学士",
    "bachelor of science": "理学学士",
    "bachelor of applied data science": "应用数据科学学士",
    "bachelor of food science and technology": "食品科学与技术学士",
    "bachelor of medical bioscience": "医学生物科学学士",
    "bachelor of science (honours)": "理学荣誉学士",
    "diploma of higher education studies": "高等教育文凭",
    "diploma of business": "商业文凭",
    "master of communications and media studies": "传播与媒体研究硕士",
    "doctor of philosophy": "哲学博士",
    "postgraduate diploma of business and commerce": "商务与商业研究生文凭",
    "master of international business": "国际商务硕士",
    "master of digital business": "数字商务硕士",
    "master of philosophy": "哲学硕士（研究型）",
    "postgraduate certificate of applied engineering": "应用工程研究生证书",
    "master of applied engineering": "应用工程硕士",
    "master of engineering science (research)": "工程科学硕士（研究型）",
    "master of artificial intelligence": "人工智能硕士",
    "master of business information systems": "商业信息系统硕士",
    "master of data science": "数据科学硕士",
    "master of biomedical science": "生物医学科学硕士",
    "master of biotechnology": "生物技术硕士",
    "master of clinical psychology": "临床心理学硕士",
    "master of pharmaceutical science": "制药科学硕士",
    "master of science": "理学硕士（研究型）",
}

_DEGREE = re.compile(
    r"^(?:Bachelor|Master|Doctor|Diploma|Postgraduate|Graduate|Monash English)\b", re.I)
_ABBREV = re.compile(r"\s*\((?:PhD|MPhil|DHES)\)\s*$", re.I)
_NUMBER = re.compile(r"\d[\d,.]*")
_GOOD = re.compile(r"^\d{1,3}(?:,\d{3})*$|^\d+$")
_LABEL = re.compile(r"^\s*\(([^)]*)\)")


@dataclass(frozen=True)
class Amount:
    value: int | None
    written: str
    label: str = ""

    @property
    def readable(self) -> bool:
        return self.value is not None


@dataclass
class Fee:
    titles: tuple[str, ...]
    school: str
    page: str
    duration: str = ""
    mode: str = ""
    variant: str = ""
    basis: str | None = None
    domestic: list[Amount] = field(default_factory=list)
    international: list[Amount] = field(default_factory=list)


def norm(text: str | None) -> str:
    """A title as matching sees it. "Bachelor in X" and "Bachelor of X" are one
    degree, and "&", dashes and spacing do not count."""
    text = (text or "").lower().replace("&", " and ")
    text = re.sub(r"[–—]", "-", text)
    text = re.sub(r"\s+", " ", text).strip()
    return re.sub(r"^(bachelor|master|diploma|doctor|postgraduate diploma|"
                  r"postgraduate certificate) in ", r"\1 of ", text)


def school_of(heading: str | None) -> str | None:
    low = norm(heading)
    for key, words in SCHOOLS:
        if words in low:
            return key
    return None


def _faculty_school(faculty: str | None) -> str | None:
    wanted = norm(faculty)
    for key, names in FACULTIES.items():
        if any(norm(n) == wanted for n in names):
            return key
    return None


def _clean(cell: str | None) -> str:
    return re.sub(r"[ \t]+", " ", (cell or "").strip())


def titles_in(cell: str) -> tuple[str, ...]:
    """Every degree a first cell names. The first line is the row's own title;
    later lines count only when they name a degree, so a list of majors does
    not turn into degrees."""
    lines = [_clean(line) for line in (cell or "").split("\n")]
    lines = [line for line in lines if line]
    if not lines:
        return ()
    first = _ABBREV.sub("", lines[0]).rstrip(":, ")
    found = [first]
    for line in lines[1:]:
        line = _ABBREV.sub("", line.lstrip("•-* ")).rstrip(",;. ")
        if _DEGREE.match(line) and line not in found:
            found.append(line)
    return tuple(found)


def amounts(cell: str) -> tuple[list[Amount], str | None]:
    """The prices in one cell and the basis it states, if it states one.

    "57,600\\n(full course)" is one amount for the whole course. "40,800
    (non-science stream) 46,560 (science stream)" is two amounts, each with a
    label. A number that does not read as a whole ringgit amount (a lost
    digit, a stray comma) is kept as written with no value.
    """
    text = cell or ""
    out: list[Amount] = []
    basis: str | None = None
    for m in _NUMBER.finditer(text):
        written = m.group().rstrip(".,")
        label = ""
        after = _LABEL.match(text[m.end():])
        if after:
            label = _clean(after.group(1))
        low = label.lower()
        if "full course" in low:
            basis, label = "full_course", ""
        elif "per year" in low or "per annum" in low:
            basis, label = "per_year", ""
        value = int(written.replace(",", "")) if _GOOD.match(written) else None
        out.append(Amount(value, written, label))
    return out, basis


def _columns(table: dict) -> dict | None:
    """Where the two fee columns, the duration and the type are, and which row
    the data starts on. None for a table that is not a fee table."""
    head = table.get("head") or []
    rows = table.get("rows") or []
    for i, row in enumerate([*head, *rows[:1]]):
        low = [_clean(c).lower() for c in row]
        if "malaysian" in low and "international" in low:
            cols = [_clean(c).lower() for c in table.get("columns") or []]
            return {
                "domestic": low.index("malaysian"),
                "international": low.index("international"),
                "duration": next((j for j, c in enumerate(cols) if c.startswith("duration")), 1),
                "mode": next((j for j, c in enumerate(cols) if c == "type"), None),
                # The labels are usually the first body row. When the cleaner
                # kept them as a second header row, data starts at row 0.
                "start": 0 if i < len(head) else 1,
                "per_year": any("per year" in c for c in cols),
            }
    return None


def _duration(cell: str) -> str:
    """The full-time length, which is what the fee is quoted against."""
    lines = [_clean(line).rstrip("*") for line in (cell or "").split("\n") if _clean(line)]
    full = next((line for line in lines if line.lower().startswith("full-time")), None)
    return (full or (lines[0] if lines else "")).strip()


def parse_blocks(blocks: list[dict], page: str) -> list[Fee]:
    """Every fee row on one page. Pure: blocks in, rows out."""
    out: list[Fee] = []
    school: str | None = None
    for block in blocks or []:
        kind = block.get("type")
        if kind == "heading":
            school = school_of(block.get("text")) or school
            continue
        if kind != "table" or school is None:
            continue
        cols = _columns(block)
        if cols is None:
            continue
        dom, intl = cols["domestic"], cols["international"]
        last: Fee | None = None
        for row in (block.get("rows") or [])[cols["start"]:]:
            width = max(dom, intl, cols["duration"], cols["mode"] or 0) + 1
            cells = [*row, *[""] * (width - len(row))]
            d, d_basis = amounts(cells[dom])
            i, i_basis = amounts(cells[intl])
            titles = titles_in(cells[0])
            if not d and not i:
                # A label row such as "Double degrees". What follows is not a
                # continuation of the row above it.
                last = None
                continue
            duration = _duration(cells[cols["duration"]])
            variant = ""
            if not titles:
                if last is None:
                    continue
                titles, variant = last.titles, duration
                if not last.variant:
                    last.variant = last.duration
            basis = d_basis or i_basis
            if basis is None and "week" in duration.lower():
                # Monash English is priced per course length, whatever the
                # table header says about years.
                basis = "full_course"
            if basis is None and cols["per_year"]:
                basis = "per_year"
            fee = Fee(
                titles=titles,
                school=school,
                page=page,
                duration=duration,
                mode=_clean(cells[cols["mode"]]) if cols["mode"] is not None else "",
                variant=variant,
                basis=basis,
                domestic=d,
                international=i,
            )
            if not variant:
                last = fee
            out.append(fee)
    return out


def general_fees(blocks: list[dict]) -> list[str]:
    """The charges listed under the page's "General fees" heading, as written,
    each with the subheading it sits under ("Once-only fees: Application - RM100").
    They are the last section on both pages, so everything after the heading
    counts."""
    out: list[str] = []
    inside = False
    sub = ""
    for block in blocks or []:
        kind = block.get("type")
        if kind == "heading":
            text = _clean(block.get("text"))
            if "general fees" in text.lower():
                inside, sub = True, ""
            elif inside:
                sub = text
            continue
        if inside and kind == "list":
            for item in block.get("items") or []:
                text = _item_text(item)
                line = f"{sub}: {text}" if sub and text else text
                if line and line not in out:
                    out.append(line)
    return out


def _item_text(item) -> str:
    if isinstance(item, dict):
        if "text" in item:
            return _clean(item["text"])
        return _clean("".join(s.get("text", "") for s in item.get("spans") or []))
    if isinstance(item, list):
        return _clean("".join(s.get("text", "") if isinstance(s, dict) else str(s) for s in item))
    return ""


# --- Reading the stored pages ----------------------------------------------

_cache: dict[tuple[str, str], tuple[list[Fee], list[str]]] = {}


def _parsed(page: OfficialPage) -> tuple[list[Fee], list[str]]:
    key = (page.slug, page.content_hash or "")
    if key not in _cache:
        if len(_cache) > 8:
            _cache.clear()
        _cache[key] = (parse_blocks(page.blocks or [], page.slug),
                       general_fees(page.blocks or []))
    return _cache[key]


def _pages(db: Session) -> list[OfficialPage]:
    rows = db.scalars(
        select(OfficialPage).where(OfficialPage.slug.in_(SOURCES), OfficialPage.status == "ok")
    ).all()
    return sorted(rows, key=lambda p: SOURCES.index(p.slug))


def _meta(page: OfficialPage) -> dict:
    return {
        "title": page.title,
        "url": page.canonical_url,
        "level": LEVEL[page.slug],
        "last_checked": page.last_checked.isoformat() if page.last_checked else None,
    }


def _amount(a: Amount) -> dict:
    return {"value": a.value, "written": a.written, "label": a.label or None}


def _row(fee: Fee, title: str | None = None, base: Baseline | None = None) -> dict:
    title = title or fee.titles[0]
    note = NOTES.get(norm(title))
    return {
        "title": title,
        "title_zh": TITLE_ZH.get(norm(title)),
        "covers": list(fee.titles[1:]) if title == fee.titles[0] else [],
        "school": fee.school,
        "source": fee.page,
        "duration": fee.duration or None,
        "mode": fee.mode or None,
        "variant": fee.variant or None,
        "basis": fee.basis,
        "domestic": [_amount(a) for a in fee.domestic],
        "international": [_amount(a) for a in fee.international],
        "unreadable": not all(a.readable for a in (*fee.domestic, *fee.international)),
        "note": note,
        "change": change(fee, title, base),
    }


def year_in(blocks: list[dict]) -> int | None:
    """The fee year a page states in its opening lines ("2027 tuition fees are...")."""
    for block in (blocks or [])[:4]:
        if block.get("type") != "paragraph":
            continue
        text = "".join(s.get("text", "") for s in block.get("spans") or [])
        m = re.search(r"\b(20\d\d)\b[^.]{0,20}\bfees\b", text, re.I)
        if m:
            return int(m.group(1))
    return None


def year_of(pages: list[OfficialPage]) -> int | None:
    for page in pages:
        year = year_in(page.blocks or [])
        if year:
            return year
    return None


# --- Last year's fees, for the change ----------------------------------------
#
# A row's change is worked out only when last year's row is the same thing:
# same title (and length, for Monash English), same basis, the same number of
# prices in the cell, and every amount readable on both sides. Anything else
# leaves the change blank, because a difference between a per year fee and a
# whole course fee, or between two different streams, is not a price rise.


@dataclass(frozen=True)
class Before:
    domestic: tuple[int | None, ...]
    international: tuple[int | None, ...]
    basis: str | None
    school: str | None
    source: str


@dataclass
class Baseline:
    year: int
    rows: dict[tuple[str, str], list[Before]]
    sources: dict[str, dict]
    # "versions" when last year's fee pages were stored, "printed" otherwise.
    kind: str = "versions"


def _variant_key(text: str | None) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def _from_versions(db: Session, year: int) -> Baseline | None:
    """Last year's tables, if the index kept a version of the fee pages from then."""
    rows: dict[tuple[str, str], list[Before]] = {}
    sources: dict[str, dict] = {}
    for page in _pages(db):
        versions = db.scalars(
            select(OfficialPageVersion)
            .where(OfficialPageVersion.page_id == page.id)
            .order_by(OfficialPageVersion.captured_at.desc())
        ).all()
        version = next((v for v in versions if year_in(v.blocks or []) == year), None)
        if version is None:
            continue
        key = f"{page.slug}@{version.captured_at.date().isoformat()}"
        sources[key] = {"title": f"{page.title} ({year})", "url": page.canonical_url,
                        "read_on": version.captured_at.date().isoformat()}
        for fee in parse_blocks(version.blocks or [], page.slug):
            before = Before(tuple(a.value for a in fee.domestic),
                            tuple(a.value for a in fee.international),
                            fee.basis, fee.school, key)
            for title in fee.titles:
                rows.setdefault((norm(title), _variant_key(fee.variant)), []).append(before)
    return Baseline(year, rows, sources) if rows else None


def _printed(year: int) -> Baseline | None:
    if year != tuition_2026.YEAR:
        return None
    rows: dict[tuple[str, str], list[Before]] = {}
    for r in tuition_2026.ROWS:
        rows.setdefault((norm(r.title), _variant_key(r.variant)), []).append(
            Before(r.domestic, r.international, r.basis, r.school, r.source))
    sources = {k: {**v, "read_on": tuition_2026.READ_ON}
               for k, v in tuition_2026.SOURCES.items()}
    return Baseline(year, rows, sources, "printed")


def baseline(db: Session, year: int | None) -> Baseline | None:
    """Fees for the year before ``year``: stored page versions first, then the
    printed 2026 table."""
    if not year:
        return None
    return _from_versions(db, year - 1) or _printed(year - 1)


def _diff(now: list[Amount], before: tuple[int | None, ...]) -> list[dict] | None:
    if len(now) != len(before) or not now:
        return None
    out = []
    for a, b in zip(now, before, strict=True):
        if a.value is None or b is None:
            out.append(None)
            continue
        diff = a.value - b
        out.append({"previous": b, "diff": diff,
                    "pct": round(diff * 100 / b, 1) if b else None})
    return out if any(out) else None


def change(fee: Fee, title: str, base: Baseline | None) -> dict | None:
    """How this row moved since last year, or None when that is not known."""
    if base is None:
        return None
    found = base.rows.get((norm(title), _variant_key(fee.variant)), [])
    same_school = [b for b in found if b.school == fee.school]
    candidates = same_school or [b for b in found if b.school is None]
    before = next((b for b in candidates if b.basis == fee.basis), None)
    if before is None:
        return None
    domestic = _diff(fee.domestic, before.domestic)
    international = _diff(fee.international, before.international)
    if domestic is None and international is None:
        return None
    return {"year": base.year, "domestic": domestic, "international": international,
            "source": before.source}


def table(db: Session) -> dict:
    """Everything the fees page shows, grouped by page and then by school."""
    pages = _pages(db)
    year = year_of(pages)
    base = baseline(db, year)
    sections = []
    general: list[str] = []
    for page in pages:
        fees, extra = _parsed(page)
        general += [g for g in extra if g not in general]
        schools: dict[str, list[dict]] = {}
        for fee in fees:
            schools.setdefault(fee.school, []).append(_row(fee, base=base))
        sections.append({
            "source": page.slug,
            "level": LEVEL[page.slug],
            "schools": [{"school": k, "rows": v} for k, v in schools.items()],
        })
    return {
        "year": year,
        "currency": "MYR",
        "sections": sections,
        "general": general,
        "sources": {page.slug: _meta(page) for page in pages},
        "previous": {"year": base.year, "kind": base.kind, "sources": base.sources}
        if base else None,
    }


def match(fees: list[Fee], title: str | None, faculty: str | None = None) -> list[tuple[Fee, str]]:
    """The fee rows for one Handbook degree, with the title each matched on.

    Usually one. The DHES gives two (one per stream) and Monash English two
    (one per length). When several schools price the same title, only the row
    from the degree's own faculty counts, and an unknown faculty gets nothing.
    """
    wanted = norm(title)
    if not wanted:
        return []
    hits = [(f, t) for f in fees for t in f.titles if norm(t) == wanted]
    if len({f.school for f, _ in hits}) <= 1:
        return hits
    school = _faculty_school(faculty)
    return [(f, t) for f, t in hits if f.school == school] if school else []


def for_course(db: Session, title: str | None, faculty: str | None,
               campuses: list[str] | None) -> dict | None:
    """The fee card for a degree page, or None.

    These are Malaysia campus fees, so a degree Malaysia does not teach gets no
    card even when another campus has a degree with the same name.
    """
    if "Malaysia" not in (campuses or []):
        return None
    pages = _pages(db)
    if not pages:
        return None
    hits: list[tuple[Fee, str]] = []
    for page in pages:
        hits += match(_parsed(page)[0], title, faculty)
    missing = NOT_LISTED.get(norm(title))
    if not hits and not missing:
        return None
    used = {f.page for f, _ in hits} or {pages[-1].slug}
    year = year_of(pages)
    base = baseline(db, year)
    rows = [_row(f, t, base) for f, t in hits]
    cited = {r["change"]["source"] for r in rows if r["change"]}
    return {
        "year": year,
        "currency": "MYR",
        "rows": rows,
        "previous": {"year": base.year, "kind": base.kind,
                     "sources": {k: v for k, v in base.sources.items() if k in cited}}
        if base and cited else None,
        "not_listed": missing if not hits else None,
        "sources": {p.slug: _meta(p) for p in pages if p.slug in used},
    }
