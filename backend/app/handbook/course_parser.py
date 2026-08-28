"""Turn a Handbook course or area-of-study page into normalised records.

Same contract as the unit parser: HTML string in, plain dicts out, no database
and no network, so the tests can run against saved fixtures.

Courses and areas of study are two different pages with one shape in common -
``pageContent.curriculumStructure.container``, a tree of requirement groups
holding units, majors, minors and specialisations. C2001 publishes Part A to
Part E that way; DATASCI11 publishes "Core units" and "Level 3 elective units"
the same way one level down. Parsing them with one function is not a shortcut,
it is the structure the Handbook actually has.

The tree is kept as a tree. Flattening it would lose the thing that makes it
answerable - "one of the following options" is a statement about a group, and
a list of units with the grouping removed reads as "all of the following",
which is a different degree.
"""
from __future__ import annotations

import re
from typing import Any

from app.handbook.parser import (
    ParseError,
    _as_int,
    _plain,
    compute_content_hash,
    extract_next_data,
    html_to_text,
)

# The Handbook's word for what a requirement points at, mapped to ours. Anything
# unlisted keeps the Handbook's own label rather than being forced into a bucket.
ITEM_TYPES = {
    "subject": "unit",
    "minor": "minor",
    "major": "major",
    "ug_specialisation": "specialisation",
    "pg_specialisation": "specialisation",
    "specialisation": "specialisation",
    "aos": "area_of_study",
    "course": "course",
}

# Guards against a structure that points back at itself. The Handbook has not
# done this, but an unbounded recursion over upstream data is a hang, not a bug
# report, and eight levels is far deeper than any published course.
MAX_CONTAINER_DEPTH = 8


def _campuses(content: dict[str, Any]) -> list[str]:
    """Where the degree is taught.

    This is the field that decides whether a Malaysia student can enrol at all,
    so it is read from ``modes[].locations``, which is already a list, rather
    than from the ``location`` string beside it. The string is the fallback for
    a page that publishes one and not the other.
    """
    found: list[str] = []
    for mode in content.get("modes") or []:
        for campus in mode.get("locations") or []:
            name = (campus or "").strip()
            if name and name not in found:
                found.append(name)
    if found:
        return found
    location = content.get("location")
    if not location:
        return []
    return [part.strip() for part in re.split(r"[,;/]", location) if part.strip()]


def _years(raw: list[dict] | None) -> int | None:
    """The full-time length of the degree, in years.

    Not ``maximum_duration``: that is 8 for a three-year bachelor, because it
    counts the longest a part-time student may take. Printed as the duration it
    would tell every reader their degree is eight years long.
    """
    for entry in raw or []:
        if _plain(entry.get("duration_period"), "value", "label") == "Years":
            return _as_int(entry.get("duration_number"))
    return None


def _parse_items(raw: list[dict] | None) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for index, node in enumerate(raw or []):
        code = (node.get("academic_item_code") or "").strip().upper()
        if not code:
            continue
        kind = _plain(node.get("academic_item_type"), "value", "label")
        items.append(
            {
                "item_code": code,
                "item_name": (node.get("academic_item_name") or "").strip() or None,
                "item_type": ITEM_TYPES.get((kind or "").lower(), kind),
                "item_url": (node.get("academic_item_url") or "").strip() or None,
                "credit_points": _as_int(node.get("academic_item_credit_points")),
                "connector": _plain(node.get("parent_connector"), "value", "label"),
                "order_index": _as_int(node.get("order")) if node.get("order") else index,
            }
        )
    return items


def _parse_containers(raw: list[dict] | None, depth: int = 0) -> list[dict[str, Any]]:
    """One requirement group and everything under it."""
    if depth >= MAX_CONTAINER_DEPTH:
        return []
    groups: list[dict[str, Any]] = []
    for index, node in enumerate(raw or []):
        groups.append(
            {
                "title": (node.get("title") or "").strip() or None,
                "description": html_to_text(node.get("description")),
                "footnote": html_to_text(node.get("footnote")),
                "credit_points": _as_int(node.get("credit_points")),
                "credit_points_max": _as_int(node.get("credit_points_max")),
                "connector": _plain(node.get("parent_connector"), "value", "label"),
                "order_index": _as_int(node.get("order")) if node.get("order") else index,
                "items": _parse_items(node.get("relationship")),
                "containers": _parse_containers(node.get("container"), depth + 1),
            }
        )
    # The Handbook's own order field is a sort key, not a position: C2001
    # publishes Part D at 300 and Part A at 100, and reading them in payload
    # order puts Part D first.
    groups.sort(key=lambda g: (g["order_index"] if g["order_index"] is not None else 0))
    return groups


def _structure(content: dict[str, Any]) -> list[dict[str, Any]]:
    structure = content.get("curriculumStructure") or {}
    return _parse_containers(structure.get("container"))


def parse_course_page(html: str, source_url: str) -> dict[str, Any]:
    """Parse one Handbook course page into a normalised record."""
    content = extract_next_data(html).get("props", {}).get("pageProps", {}).get("pageContent") or {}

    code = (content.get("course_code") or content.get("code") or "").strip().upper()
    if not code:
        raise ParseError(f"no course_code in payload for {source_url}")
    academic_year = _as_int(content.get("implementation_year"))
    if academic_year is None:
        raise ParseError(f"no implementation_year for {code}")

    record: dict[str, Any] = {
        "course_code": code,
        "academic_year": academic_year,
        "title": (content.get("title") or "").strip(),
        "abbreviated_name": (content.get("abbreviated_name") or "").strip() or None,
        "credit_points": _as_int(content.get("credit_points")),
        "cricos_code": (content.get("cricos_code") or "").strip() or None,
        "aqf_level": _plain(content.get("aqf_level"), "label", "value"),
        "course_type": _plain(content.get("type"), "label", "value"),
        # A course page leaves academic_org empty and names the faculty in
        # "school"; a unit page fills both. Same word, different slots.
        "faculty": (
            _plain(content.get("academic_org"), "value", "label")
            or _plain(content.get("school"), "value", "label")
        ),
        "school": _plain(content.get("school"), "value", "label"),
        "campuses": _campuses(content),
        "duration_years": _years(content.get("full_time_duration")),
        "overview": html_to_text(content.get("overview")),
        "structure_text": html_to_text(content.get("structure")),
        "requirements_text": html_to_text(content.get("requirements")),
        "handbook_version": content.get("version_name") or None,
        "source_url": source_url,
        "containers": _structure(content),
    }
    record["content_hash"] = compute_content_hash(record)
    return record


def parse_aos_page(html: str, source_url: str) -> dict[str, Any]:
    """Parse one Handbook area-of-study page - a major, minor or specialisation."""
    content = extract_next_data(html).get("props", {}).get("pageProps", {}).get("pageContent") or {}

    code = (content.get("code") or "").strip().upper()
    if not code:
        raise ParseError(f"no code in payload for {source_url}")
    academic_year = _as_int(content.get("implementation_year"))
    if academic_year is None:
        raise ParseError(f"no implementation_year for {code}")

    record: dict[str, Any] = {
        "aos_code": code,
        "academic_year": academic_year,
        "title": (content.get("title") or "").strip(),
        "aos_type": (content.get("academic_item_type") or "").strip() or None,
        "study_level": _plain(content.get("study_level"), "label", "value"),
        "credit_points": _as_int(content.get("credit_points")),
        "faculty": _plain(content.get("academic_org"), "value", "label"),
        "school": _plain(content.get("school"), "value", "label"),
        "overview": html_to_text(content.get("overview") or content.get("description")),
        "handbook_version": content.get("version_name") or None,
        "source_url": source_url,
        "containers": _structure(content),
    }
    record["content_hash"] = compute_content_hash(record)
    return record


def course_url(code: str, year: int) -> str:
    return f"https://handbook.monash.edu/{year}/courses/{code.upper()}"


def aos_url(code: str, year: int) -> str:
    return f"https://handbook.monash.edu/{year}/aos/{code.upper()}"
