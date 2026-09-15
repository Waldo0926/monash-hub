"""The prerequisite graph around one unit.

A unit page states its requisites as a list of rules. That is the truthful
rendering of one unit, and it is useless for the question students actually
ask, which is "what do I have to pass before I can take this, and how many
semesters does that take". Answering it means walking the rules transitively,
and a walk needs a graph.

Two properties of this graph are worth stating because they shape the code:

* It is not a tree. FIT2004 and FIT2014 share FIT1008 as a parent, and a
  diamond is the normal case, not a corner case. Nodes are deduplicated by
  code and the deepest depth wins, so a unit sits at the level where it is
  actually needed.
* It is not guaranteed acyclic. The Handbook contains at least one pair that
  lists each other, and a naive walk on that hangs. ``seen`` is checked before
  descending, never after.

Campus is the whole point of the Malaysia build. A graph that shows Clayton's
offerings to a Malaysia student is a plan they cannot enrol in, so every node
carries whether it is taught at the campus asked for, and the caller can grey
out the rest rather than being quietly misled.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.handbook import Unit, UnitRequisiteGroup, UnitRequisiteItem

MAX_DEPTH = 4
MAX_NODES = 220


@dataclass
class Edge:
    source: str
    target: str
    requisite_type: str
    connector: str | None
    group_id: int

    def key(self) -> tuple[str, str, int]:
        return (self.source, self.target, self.group_id)


@dataclass
class Walk:
    """One traversal's result, before it is serialised."""

    depth_of: dict[str, int] = field(default_factory=dict)
    edges: dict[tuple[str, str, int], Edge] = field(default_factory=dict)
    truncated: bool = False

    def codes(self) -> list[str]:
        return sorted(self.depth_of, key=lambda c: (self.depth_of[c], c))


def _edge_type_clause():
    """Match every upstream spelling that means prerequisite/corequisite.

    New crawls canonicalise the labels, but production rows written before that
    fix may still say ``prerequisites`` or ``corequisites``. The graph must work
    immediately after deploy rather than waiting for a several-hour recrawl.
    """
    lowered = func.lower(UnitRequisiteGroup.requisite_type)
    return or_(
        lowered.like("prereq%"),
        lowered.like("additional prereq%"),
        lowered.like("coreq%"),
    )


def _canonical_edge_type(value: str | None) -> str:
    value = (value or "").strip().lower()
    return "corequisite" if "corequisite" in value else "prerequisite"


def _requisite_rows(db: Session, codes: list[str], year: int) -> list[tuple]:
    """The requisite rules of every unit in ``codes``, one query."""
    if not codes:
        return []
    stmt = (
        select(
            Unit.unit_code,
            UnitRequisiteGroup.id,
            UnitRequisiteGroup.requisite_type,
            UnitRequisiteGroup.connector,
            UnitRequisiteItem.item_code,
        )
        .join(UnitRequisiteGroup, UnitRequisiteGroup.unit_id == Unit.id)
        .join(UnitRequisiteItem, UnitRequisiteItem.group_id == UnitRequisiteGroup.id)
        .where(
            Unit.unit_code.in_(codes),
            Unit.academic_year == year,
            _edge_type_clause(),
            UnitRequisiteItem.item_code.is_not(None),
        )
    )
    return list(db.execute(stmt))


def _dependent_rows(db: Session, codes: list[str], year: int) -> list[tuple]:
    """The units that name any of ``codes`` as a requisite - the other way up."""
    if not codes:
        return []
    stmt = (
        select(
            Unit.unit_code,
            UnitRequisiteGroup.id,
            UnitRequisiteGroup.requisite_type,
            UnitRequisiteGroup.connector,
            UnitRequisiteItem.item_code,
        )
        .join(UnitRequisiteGroup, UnitRequisiteGroup.unit_id == Unit.id)
        .join(UnitRequisiteItem, UnitRequisiteItem.group_id == UnitRequisiteGroup.id)
        .where(
            UnitRequisiteItem.item_code.in_(codes),
            Unit.academic_year == year,
            _edge_type_clause(),
        )
    )
    return list(db.execute(stmt))


def walk(db: Session, seed: str, year: int, direction: str, depth: int) -> Walk:
    """Breadth-first from ``seed``, at most ``depth`` levels each way.

    Depth is signed: a prerequisite sits at -1, a unit the seed unlocks at +1,
    and the seed at 0. "Both" is the two walks laid side by side, which is why
    the sign has to survive into the result - without it the renderer cannot
    tell which side of the seed a node belongs on.
    """
    depth = max(1, min(depth, MAX_DEPTH))
    result = Walk(depth_of={seed: 0})

    for sign, rows_for in ((-1, _requisite_rows), (1, _dependent_rows)):
        if direction == "upstream" and sign > 0:
            continue
        if direction == "downstream" and sign < 0:
            continue

        frontier = deque([seed])
        for level in range(1, depth + 1):
            if not frontier:
                break
            batch = list(frontier)
            frontier.clear()
            for holder, group_id, req_type, connector, item_code in rows_for(db, batch, year):
                # Both queries return the same shape: the item is always the
                # requisite and the holder is always the unit that requires it.
                # Direction changes which end is the new one, never the arrow.
                parent, child = item_code, holder
                if not parent or not child:
                    continue
                found = parent if sign < 0 else child
                edge = Edge(
                    parent,
                    child,
                    _canonical_edge_type(req_type),
                    connector,
                    group_id,
                )
                result.edges.setdefault(edge.key(), edge)
                if found in result.depth_of:
                    continue
                if len(result.depth_of) >= MAX_NODES:
                    result.truncated = True
                    continue
                result.depth_of[found] = sign * level
                frontier.append(found)

    # An edge whose other end was never reached would be drawn into empty space.
    result.edges = {
        key: edge
        for key, edge in result.edges.items()
        if edge.source in result.depth_of and edge.target in result.depth_of
    }
    return result


def load_units(db: Session, codes: list[str], year: int) -> dict[str, Unit]:
    if not codes:
        return {}
    units = db.scalars(
        select(Unit)
        .where(Unit.unit_code.in_(codes), Unit.academic_year == year)
        .options(selectinload(Unit.offerings), selectinload(Unit.requisite_groups))
    )
    return {unit.unit_code: unit for unit in units}
