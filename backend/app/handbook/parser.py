"""Turn a Handbook unit page into normalised records.

The Handbook is a Next.js app, so the authoritative content is the JSON in the
``__NEXT_DATA__`` script tag rather than the rendered HTML. Parsing that instead
of scraping the DOM means a visual redesign does not break us, and it keeps the
parser a pure function: HTML string in, plain dicts out, no database and no
network. That is what makes ``backend/tests/test_handbook_parser.py`` able to
run against saved fixtures.

Nothing here invents a value. If the Handbook does not state something, the
field stays ``None`` and the UI says so - "not listed" is a different claim from
"does not exist", and only the first one is ours to make.
"""
from __future__ import annotations

import hashlib
import json
import re
from html import unescape
from typing import Any

NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(?P<json>.*?)</script>',
    re.DOTALL,
)
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"[ \t\r\f\v ]+")
UNIT_CODE_RE = re.compile(r"\b[A-Z]{2,5}\d{4}\b")
RULE_LABEL_RE = re.compile(
    r"\b(?P<label>(?:ADDITIONAL\s+)?PREREQUISITES?|COREQUISITES?|PROHIBITIONS?)\s*:",
    re.IGNORECASE,
)

# Assessment types and names that mean "there is a final exam". Kept explicit
# rather than a fuzzy match so a new Handbook label fails visibly instead of
# silently flipping a filter students rely on.
EXAM_MARKERS = ("examination", "exam")
NON_EXAM_MARKERS = ("no exam", "non-exam")


class ParseError(ValueError):
    """The page was fetched but did not contain a usable unit record."""


def extract_next_data(html: str) -> dict[str, Any]:
    match = NEXT_DATA_RE.search(html)
    if not match:
        raise ParseError("no __NEXT_DATA__ payload in page")
    try:
        return json.loads(match.group("json"))
    except json.JSONDecodeError as exc:  # pragma: no cover - malformed upstream
        raise ParseError(f"__NEXT_DATA__ is not valid JSON: {exc}") from exc


def html_to_text(value: str | None) -> str | None:
    """Flatten Handbook rich text to readable plain text.

    Block boundaries become newlines first so that ``<li>`` items do not run
    into each other once the tags are gone.
    """
    if not value:
        return None
    text = re.sub(r"<(br|/p|/li|/h[1-6]|/div|/tr)[^>]*>", "\n", value, flags=re.I)
    text = re.sub(r"<li[^>]*>", "• ", text, flags=re.I)
    text = TAG_RE.sub("", text)
    text = unescape(text)
    text = WS_RE.sub(" ", text)
    text = re.sub(r"\n\s*\n\s*", "\n\n", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    return text.strip() or None


def _plain(node: Any, *keys: str) -> str | None:
    """Read a Handbook reference node, which is ``{"value": ...}`` or ``{"label": ...}``."""
    if node is None:
        return None
    if isinstance(node, str):
        return node.strip() or None
    if isinstance(node, dict):
        for key in keys or ("label", "value"):
            candidate = node.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
    return None


def _as_int(value: Any) -> int | None:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def compute_content_hash(payload: dict[str, Any]) -> str:
    """Hash the *content*, not the page.

    Handbook markup carries build ids and other churn that changes on every
    deploy; hashing the normalised record means an unchanged unit costs us no
    write and no reindex.
    """
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _parse_offerings(raw: list[dict] | None) -> list[dict[str, Any]]:
    offerings = []
    for item in raw or []:
        if str(item.get("publish", "true")).lower() == "false":
            continue
        offerings.append(
            {
                "offering_code": item.get("name") or None,
                "display_name": item.get("display_name") or None,
                "campus": _plain(item.get("location"), "value", "label"),
                "teaching_period": _plain(item.get("teaching_period"), "value", "label"),
                "attendance_mode": _plain(item.get("attendance_mode"), "value", "label"),
                "study_level": _plain(item.get("study_level"), "label", "value"),
                "offered": str(item.get("offered", "true")).lower() != "false",
            }
        )
    return offerings


def _parse_assessments(raw: list[dict] | None) -> list[dict[str, Any]]:
    assessments = []
    for item in raw or []:
        assessments.append(
            {
                "number": _as_int(item.get("number")),
                "name": item.get("name") or item.get("assessment_name") or None,
                "assessment_type": _plain(item.get("assessment_type"), "label", "value"),
                "weight": (str(item.get("weight")).strip() or None) if item.get("weight") else None,
                "hurdle": _plain(item.get("hurdle_type"), "label", "value"),
                "description": html_to_text(item.get("description")),
                "learning_outcomes": (item.get("learning_outcomes") or None),
                "offering_scope": html_to_text(item.get("offerings_formatted")),
            }
        )
    assessments.sort(key=lambda a: (a["number"] is None, a["number"] or 0))
    return assessments


def derive_has_exam(assessments: list[dict[str, Any]], summary: str | None) -> bool | None:
    """Whether the Handbook lists an examination for this unit.

    ``None`` means "we could not tell" - no assessment items were published -
    and the UI must not render that as "no exam".
    """
    if not assessments:
        return None
    for item in assessments:
        haystack = " ".join(
            part.lower() for part in (item.get("assessment_type"), item.get("name")) if part
        )
        if not haystack:
            continue
        if any(marker in haystack for marker in NON_EXAM_MARKERS):
            continue
        if any(marker in haystack for marker in EXAM_MARKERS):
            return True
    return False


# The Handbook has not nested requisites deeper than three, and an unbounded
# recursion over upstream data is a hang rather than a bug report.
MAX_REQUISITE_DEPTH = 6


def _canonical_requisite_type(value: str | None) -> str:
    """Collapse Handbook label variants to the three types the app understands.

    The upstream feed has emitted singular, plural, and "additional
    prerequisite" labels over time. Keeping those variants in the database made
    the tree fragile: its SQL matched ``prerequisite`` exactly while unit pages
    could still render ``prerequisites`` just fine.
    """
    value = re.sub(r"\s+", " ", (value or "").strip().lower())
    if "corequisite" in value:
        return "corequisite"
    if "prerequisite" in value:
        return "prerequisite"
    if "prohibition" in value:
        return "prohibition"
    return value or "unknown"


def _unit_codes(text: str | None) -> list[str]:
    """Unit-shaped references in source order, without guessing rule logic."""
    if not text:
        return []
    return list(dict.fromkeys(UNIT_CODE_RE.findall(text.upper())))


def _reference_items(text: str | None) -> list[dict[str, Any]]:
    """Turn prose references into linkable items while preserving uncertainty.

    These items only appear when the Handbook did not publish a structured
    requisite container. Their group connector is ``TEXT``: it deliberately
    does *not* claim that the references are ANDs or ORs. The source prose is
    kept as the group description and remains the authority.
    """
    return [
        {
            "item_code": code,
            "item_name": None,
            "item_type": "Unit",
            "item_url": None,
            "credit_points": None,
            "order_index": index,
        }
        for index, code in enumerate(_unit_codes(text))
    ]


def _walk_requisite_containers(containers: list[dict] | None, depth: int = 0) -> list[dict]:
    """One requisite container and everything under it, as a tree.

    This used to flatten: every container, at every level, appended to one
    list. That loses the only thing the nesting says. FIT2099 asks for one of
    six programming units *or* an engineering pair, and as a flat list of
    groups it reads as "all of the above".
    """
    if depth >= MAX_REQUISITE_DEPTH:
        return []
    out: list[dict] = []
    for order, container in enumerate(containers or []):
        items = []
        for index, rel in enumerate(container.get("relationships") or []):
            items.append(
                {
                    "item_code": rel.get("academic_item_code") or None,
                    "item_name": rel.get("academic_item_name") or None,
                    "item_type": _plain(rel.get("academic_item_type"), "label", "value"),
                    "item_url": rel.get("academic_item_url") or None,
                    "credit_points": rel.get("academic_item_credit_points") or None,
                    "order_index": _as_int(rel.get("order")) or index,
                }
            )
        children = _walk_requisite_containers(container.get("containers"), depth + 1)
        if not (items or children or container.get("description")):
            continue
        out.append(
            {
                "connector": _plain(container.get("parent_connector"), "value", "label"),
                "title": container.get("title") or None,
                "description": html_to_text(container.get("description")),
                "order_index": _as_int(container.get("order")) or order,
                "items": items,
                "groups": children,
            }
        )
    return out


def _stamp(nodes: list[dict], req_type: str, description: str | None) -> None:
    """Carry the block's type and wording down to every group inside it."""
    for node in nodes:
        node["requisite_type"] = req_type
        node["raw_text"] = description
        _stamp(node.get("groups") or [], req_type, description)


def _parse_requisites(raw: list[dict] | None) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    for block in raw or []:
        if str(block.get("active", "true")).lower() == "false":
            continue
        req_type = _canonical_requisite_type(
            _plain(block.get("requisite_type"), "value", "label")
        )
        found = _walk_requisite_containers(block.get("container"))
        description = html_to_text(block.get("description"))
        if not found and description:
            items = _reference_items(description)
            found = [
                {
                    "connector": "TEXT" if items else None,
                    "title": None,
                    "description": description,
                    "order_index": 0,
                    "items": items,
                    "groups": [],
                }
            ]

        _stamp(found, req_type, description)
        groups += found
    return groups


def _group_has_references(group: dict[str, Any]) -> bool:
    return bool(group.get("items")) or any(
        _group_has_references(child) for child in group.get("groups") or []
    )


def _flatten_rule_field(node: Any) -> str:
    """Flatten one rule-like JSON field, including rich-text span structures."""
    if isinstance(node, str):
        return html_to_text(node) or ""
    if isinstance(node, dict):
        parts = [_flatten_rule_field(value) for value in node.values()]
    elif isinstance(node, list):
        parts = [_flatten_rule_field(value) for value in node]
    else:
        return ""
    return "\n".join(part for part in parts if part)


def _rule_text_candidates(content: dict[str, Any]) -> list[str]:
    """Find enrolment-rule prose without depending on one CMS field name.

    Monash publishes some units' prerequisite logic only inside the Rules /
    Enrolment Rule prose, while other units get a structured ``requisites``
    tree. The exact CMS key has changed, so rule-like top-level fields are read
    by meaning rather than by one brittle spelling. Plain top-level strings are
    also checked, but only strings carrying an explicit labelled rule qualify.
    """
    candidates: list[str] = []
    for key, value in content.items():
        if key == "requisites":
            continue
        lowered = key.lower()
        text = ""
        if isinstance(value, str):
            text = html_to_text(value) or ""
        elif any(token in lowered for token in ("rule", "requisit", "enrol")):
            text = _flatten_rule_field(value)
        if text and RULE_LABEL_RE.search(text) and text not in candidates:
            candidates.append(text)
    return candidates


def _parse_rule_text_requisites(
    content: dict[str, Any], existing: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Recover unit references from labelled prose when structured data is absent.

    This is intentionally a reference extractor, not an English-language logic
    parser. A rule such as MTH2051's combines several "one unit from" clauses,
    a course-enrolment exception, and an alternative unit. Guessing that into a
    boolean expression would make the planner authoritative when the source did
    not give us a machine-readable expression. ``TEXT`` groups therefore power
    links and the dependency graph, while the exact prose remains visible and
    strict plan validation ignores that group.
    """
    covered = {
        group.get("requisite_type")
        for group in existing
        if _group_has_references(group)
    }
    buckets: dict[str, dict[str, list[str]]] = {}

    for text in _rule_text_candidates(content):
        markers = list(RULE_LABEL_RE.finditer(text))
        for index, marker in enumerate(markers):
            req_type = _canonical_requisite_type(marker.group("label"))
            if req_type in covered:
                continue
            end = markers[index + 1].start() if index + 1 < len(markers) else len(text)
            section = text[marker.start():end].strip()
            codes = _unit_codes(section)
            if not codes:
                continue
            bucket = buckets.setdefault(req_type, {"descriptions": [], "codes": []})
            if section not in bucket["descriptions"]:
                bucket["descriptions"].append(section)
            for code in codes:
                if code not in bucket["codes"]:
                    bucket["codes"].append(code)

    out: list[dict[str, Any]] = []
    for order, (req_type, bucket) in enumerate(buckets.items(), start=len(existing)):
        description = "\n\n".join(bucket["descriptions"])
        items = _reference_items(" ".join(bucket["codes"]))
        group = {
            "requisite_type": req_type,
            "connector": "TEXT",
            "title": None,
            "description": description,
            "raw_text": description,
            "order_index": order,
            "items": items,
            "groups": [],
        }
        out.append(group)
    return out


def _parse_learning_outcomes(raw: list[dict] | None) -> list[dict[str, Any]]:
    outcomes = []
    for item in raw or []:
        outcomes.append(
            {
                "code": item.get("code") or None,
                "number": _as_int(item.get("number")),
                "description": html_to_text(item.get("description")),
            }
        )
    outcomes.sort(key=lambda o: (o["number"] is None, o["number"] or 0))
    return outcomes


def _parse_activities(raw: list[dict] | None) -> list[dict[str, Any]]:
    activities = []
    for group in raw or []:
        group_type = group.get("activity_type")
        for item in group.get("activities") or []:
            activities.append(
                {
                    "activity_type": group_type
                    or _plain(item.get("activity_type"), "label", "value"),
                    "name": item.get("duration_display") or None,
                    "description": html_to_text(item.get("description"))
                    or html_to_text(item.get("offerings_formatted_teaching_activities")),
                }
            )
    return activities


def parse_unit_page(html: str, source_url: str) -> dict[str, Any]:
    """Parse one Handbook unit page into a normalised record."""
    data = extract_next_data(html)
    page_props = data.get("props", {}).get("pageProps", {})
    content = page_props.get("pageContent") or {}

    unit_code = (content.get("unit_code") or content.get("code") or "").strip().upper()
    if not unit_code:
        raise ParseError(f"no unit_code in payload for {source_url}")

    academic_year = _as_int(content.get("implementation_year"))
    if academic_year is None:
        raise ParseError(f"no implementation_year for {unit_code}")

    assessments = _parse_assessments(content.get("assessments"))
    assessment_summary = html_to_text(content.get("handbook_assessment_summary"))
    requisite_groups = _parse_requisites(content.get("requisites"))
    requisite_groups += _parse_rule_text_requisites(content, requisite_groups)

    record: dict[str, Any] = {
        "unit_code": unit_code,
        "academic_year": academic_year,
        "title": (content.get("title") or "").strip(),
        "credit_points": content.get("credit_points") or None,
        "level": _plain(content.get("level"), "label", "value"),
        "faculty": _plain(content.get("academic_org"), "value", "label"),
        "school": _plain(content.get("school"), "value", "label"),
        "subject_prefix": re.sub(r"[^A-Z]", "", unit_code)[:4] or None,
        "source_url": source_url,
        "overview": html_to_text(content.get("handbook_synopsis") or content.get("overview")),
        "areas_of_study": html_to_text(content.get("area_of_study_links")),
        "teaching_approach": "\n\n".join(
            filter(
                None,
                (
                    " - ".join(
                        filter(
                            None,
                            (
                                _plain(item.get("type"), "label", "value"),
                                html_to_text(item.get("description")),
                            ),
                        )
                    )
                    for item in content.get("teaching_approaches") or []
                ),
            )
        )
        or None,
        "workload_requirements": html_to_text(content.get("workload_requirements")),
        "assessment_summary": assessment_summary,
        "assessment_static_text": html_to_text(content.get("assessment_static_text")),
        "handbook_version": content.get("version_name") or None,
        "offerings": _parse_offerings(content.get("unit_offering")),
        "assessments": assessments,
        "requisite_groups": requisite_groups,
        "learning_outcomes": _parse_learning_outcomes(content.get("unit_learning_outcomes")),
        "activities": _parse_activities(content.get("learning_activities_grouped")),
    }
    record["has_exam"] = derive_has_exam(assessments, assessment_summary)
    record["content_hash"] = compute_content_hash(record)
    return record


def unit_url(unit_code: str, year: int) -> str:
    return f"https://handbook.monash.edu/{year}/units/{unit_code.upper()}"
