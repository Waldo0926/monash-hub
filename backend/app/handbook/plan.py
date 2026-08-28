"""Check a course plan against the Handbook.

A plan is a list of (unit, year, teaching period). Checking it is the whole
point of building one: a student can write down twelve units in four semesters
without help, and what they cannot do by hand is verify that every one of them
is actually taught at their campus in the semester they put it in, and that
everything each one requires sits somewhere earlier.

Four things are checked, and the second is the one no other Monash planner
does:

* the unit exists in this Handbook year;
* it is taught at this campus in that teaching period. A plan built from
  Clayton's offerings is a plan a Malaysia student cannot enrol in, and the
  failure is invisible until enrolment opens;
* its prerequisites are satisfied by units placed strictly earlier, with the
  Handbook's own AND/OR grouping honoured - an OR group needs one of its
  members, an AND group needs all of them;
* no two units in the plan prohibit each other.

Corequisites are checked as "at or before", because that is what a corequisite
means, and getting that wrong in the strict direction would report an error on
a plan the Handbook allows.

Nothing here rejects a plan. Every finding is returned with a severity and the
student decides: the Handbook is not always complete, permission is sometimes
granted, and a planner that refuses to hold a plan it disapproves of is a
planner people stop using.
"""
from __future__ import annotations

from collections.abc import Iterable
from contextlib import suppress
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.handbook import Unit, UnitRequisiteGroup

# Teaching periods in the order a year runs, so "earlier" means something. A
# period the Handbook publishes but this list does not know sorts last within
# its year rather than being dropped: an unknown period is a reason to check
# nothing about order, not a reason to hide the unit.
PERIOD_ORDER = (
    "Summer semester A",
    "Summer semester B",
    "First semester",
    "Winter semester",
    "Second semester",
    "October intake teaching period, Malaysia campus",
)

# A full-year unit occupies both semesters, so anything it requires has to be
# finished before the year starts, and it satisfies requirements only after the
# year ends. Treating it as a first-semester unit would let a student place its
# dependants in second semester.
FULL_YEAR = ("Full year", "Full year extended")

MAX_ENTRIES = 80


def period_index(period: str | None) -> int:
    if not period:
        return len(PERIOD_ORDER)
    try:
        return PERIOD_ORDER.index(period)
    except ValueError:
        return len(PERIOD_ORDER)


@dataclass(frozen=True)
class Slot:
    """Where in a plan a unit sits."""

    year: int
    period: str

    def key(self) -> tuple[int, int]:
        return (self.year, period_index(self.period))

    def is_full_year(self) -> bool:
        return self.period in FULL_YEAR

    def finishes_before(self, other: Slot) -> bool:
        """Whether this slot has finished by the time ``other`` starts."""
        if self.year != other.year:
            return self.year < other.year
        if self.is_full_year():
            return False
        if other.is_full_year():
            return True
        return period_index(self.period) < period_index(other.period)

    def finishes_by(self, other: Slot) -> bool:
        """"At or before" - what a corequisite asks for."""
        return self.finishes_before(other) or self == other


@dataclass
class Entry:
    unit_code: str
    slot: Slot


@dataclass
class Issue:
    unit_code: str
    year: int
    period: str
    # "error" is a rule the Handbook states; "warning" is something worth
    # looking at that a permission or a Handbook gap could explain.
    severity: str
    kind: str
    detail: dict = field(default_factory=dict)


def _entries(raw: Iterable[dict]) -> list[Entry]:
    out: list[Entry] = []
    for item in list(raw)[:MAX_ENTRIES]:
        code = (item.get("unit_code") or "").strip().upper()
        period = (item.get("teaching_period") or "").strip()
        try:
            year = int(item.get("year"))
        except (TypeError, ValueError):
            continue
        if code and period:
            out.append(Entry(code, Slot(year, period)))
    return out


def _load(db: Session, codes: list[str], academic_year: int) -> dict[str, Unit]:
    if not codes:
        return {}
    units = db.scalars(
        select(Unit)
        .where(Unit.unit_code.in_(codes), Unit.academic_year == academic_year)
        .options(
            selectinload(Unit.offerings),
            # Three levels is as deep as the Handbook goes; the loader is
            # explicit rather than lazy so a plan check stays one round trip.
            selectinload(Unit.requisite_groups).selectinload(UnitRequisiteGroup.items),
            selectinload(Unit.requisite_groups)
            .selectinload(UnitRequisiteGroup.children)
            .selectinload(UnitRequisiteGroup.items),
            selectinload(Unit.requisite_groups)
            .selectinload(UnitRequisiteGroup.children)
            .selectinload(UnitRequisiteGroup.children)
            .selectinload(UnitRequisiteGroup.items),
        )
    )
    return {unit.unit_code: unit for unit in units}


@dataclass
class Unmet:
    """Why a rule is not satisfied, in the shape the rule itself has."""

    connector: str
    codes: list[str] = field(default_factory=list)
    groups: list[Unmet] = field(default_factory=list)

    def flatten(self) -> list[str]:
        """Every code named anywhere in this rule, for a one-line message."""
        found = list(self.codes)
        for child in self.groups:
            found += child.flatten()
        return list(dict.fromkeys(found))


def _evaluate(group: UnitRequisiteGroup, done: dict[str, Slot], at: Slot) -> Unmet | None:
    """None when the rule is satisfied; otherwise what is still missing.

    The nesting is the rule. FIT2099 asks for one of six programming units
    *or* an engineering pair, and read as a flat list of groups that becomes
    "all of the above" - which is what told a student holding FIT1045 that
    they still needed two ENG units.

    A group's ``connector`` says how its contents combine, where the contents
    are its items and the groups inside it. AND needs all of them, OR needs one.
    """
    corequisite = (group.requisite_type or "").startswith("coreq")
    connector = (group.connector or "AND").upper()

    met_codes: list[str] = []
    missing_codes: list[str] = []
    for item in group.items:
        code = (item.item_code or "").upper()
        if not code:
            continue
        placed = done.get(code)
        ok = placed is not None and (
            placed.finishes_by(at) if corequisite else placed.finishes_before(at)
        )
        (met_codes if ok else missing_codes).append(code)

    satisfied_children = 0
    unmet_children: list[Unmet] = []
    for child in group.children:
        result = _evaluate(child, done, at)
        if result is None:
            satisfied_children += 1
        else:
            unmet_children.append(result)

    if connector == "OR":
        # One operand is enough, and an empty group asks for nothing.
        if met_codes or satisfied_children:
            return None
        if not missing_codes and not unmet_children:
            return None
        return Unmet("OR", missing_codes, unmet_children)

    if not missing_codes and not unmet_children:
        return None
    return Unmet("AND", missing_codes, unmet_children)


def _as_rule(unmet: Unmet) -> dict:
    return {
        "connector": unmet.connector,
        "codes": unmet.codes,
        "groups": [_as_rule(child) for child in unmet.groups],
    }


def check(db: Session, raw_entries: Iterable[dict], *, academic_year: int,
          campus: str | None) -> dict:
    """Every finding about one plan, plus what it adds up to."""
    entries = _entries(raw_entries)
    units = _load(db, [e.unit_code for e in entries], academic_year)
    issues: list[Issue] = []

    seen: dict[str, Slot] = {}
    duplicates: set[str] = set()
    for entry in entries:
        if entry.unit_code in seen:
            duplicates.add(entry.unit_code)
        else:
            seen[entry.unit_code] = entry.slot

    credit_points = 0
    for entry in entries:
        unit = units.get(entry.unit_code)
        if unit is None:
            issues.append(Issue(entry.unit_code, entry.slot.year, entry.slot.period,
                                "error", "not_in_year"))
            continue

        # The Handbook publishes credit points as a string, and a handful of
        # units publish something that is not a number at all.
        with suppress(TypeError, ValueError):
            credit_points += int(unit.credit_points or 0)

        if entry.unit_code in duplicates and seen[entry.unit_code] != entry.slot:
            issues.append(Issue(entry.unit_code, entry.slot.year, entry.slot.period,
                                "warning", "duplicate"))

        offered = [o for o in unit.offerings if o.offered]
        at_campus = [o for o in offered if not campus or o.campus == campus]
        if campus and not at_campus:
            issues.append(Issue(entry.unit_code, entry.slot.year, entry.slot.period,
                                "error", "not_offered_at_campus",
                                {"campus": campus,
                                 "elsewhere": sorted({o.campus for o in offered if o.campus})}))
        elif not any(o.teaching_period == entry.slot.period for o in at_campus):
            issues.append(Issue(entry.unit_code, entry.slot.year, entry.slot.period,
                                "error", "not_offered_in_period",
                                {"campus": campus,
                                 "offered_in": sorted({o.teaching_period for o in at_campus
                                                       if o.teaching_period})}))

    # Requisites and prohibitions, once the whole plan is known.
    for entry in entries:
        unit = units.get(entry.unit_code)
        if unit is None:
            continue
        for group in unit.requisite_groups:
            kind = (group.requisite_type or "").lower()
            if kind.startswith("prohibit"):
                clash = [
                    (item.item_code or "").upper()
                    for item in group.items
                    if (item.item_code or "").upper() in seen
                ]
                if clash:
                    issues.append(Issue(entry.unit_code, entry.slot.year, entry.slot.period,
                                        "error", "prohibited_with", {"units": sorted(clash)}))
                continue
            if not (kind.startswith("prereq") or kind.startswith("coreq")):
                continue
            unmet = _evaluate(group, seen, entry.slot)
            if unmet:
                issues.append(Issue(
                    entry.unit_code, entry.slot.year, entry.slot.period, "error",
                    "missing_corequisite" if kind.startswith("coreq") else "missing_prerequisite",
                    {
                        "any_of": unmet.flatten() if unmet.connector == "OR" else [],
                        "all_of": [] if unmet.connector == "OR" else unmet.codes,
                        # The whole shape, for a reader who needs to see which
                        # branch of an OR they are closest to finishing.
                        "rule": _as_rule(unmet),
                    },
                ))

    return {
        "academic_year": academic_year,
        "campus": campus,
        "credit_points": credit_points,
        "units": len(entries),
        "issues": [
            {
                "unit_code": issue.unit_code,
                "year": issue.year,
                "teaching_period": issue.period,
                "severity": issue.severity,
                "kind": issue.kind,
                "detail": issue.detail,
            }
            for issue in issues
        ],
    }
