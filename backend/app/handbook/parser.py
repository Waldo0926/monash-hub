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


def _walk_requisite_containers(containers: list[dict] | None, out: list[dict]) -> None:
    for container in containers or []:
        items = []
        for order, rel in enumerate(container.get("relationships") or []):
            items.append(
                {
                    "item_code": rel.get("academic_item_code") or None,
                    "item_name": rel.get("academic_item_name") or None,
                    "item_type": _plain(rel.get("academic_item_type"), "label", "value"),
                    "item_url": rel.get("academic_item_url") or None,
                    "credit_points": rel.get("academic_item_credit_points") or None,
                    "order_index": _as_int(rel.get("order")) or order,
                }
            )
        if items or container.get("description"):
            out.append(
                {
                    "connector": _plain(container.get("parent_connector"), "value", "label"),
                    "title": container.get("title") or None,
                    "description": html_to_text(container.get("description")),
                    "items": items,
                }
            )
        _walk_requisite_containers(container.get("containers"), out)


def _parse_requisites(raw: list[dict] | None) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    for block in raw or []:
        if str(block.get("active", "true")).lower() == "false":
            continue
        req_type = _plain(block.get("requisite_type"), "value", "label") or "unknown"
        found: list[dict] = []
        _walk_requisite_containers(block.get("container"), found)
        description = html_to_text(block.get("description"))
        if not found and description:
            found = [{"connector": None, "title": None, "description": description, "items": []}]
        for group in found:
            group["requisite_type"] = req_type.lower()
            group["raw_text"] = description
            groups.append(group)
    return groups


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
        "requisite_groups": _parse_requisites(content.get("requisites")),
        "learning_outcomes": _parse_learning_outcomes(content.get("unit_learning_outcomes")),
        "activities": _parse_activities(content.get("learning_activities_grouped")),
    }
    record["has_exam"] = derive_has_exam(assessments, assessment_summary)
    record["content_hash"] = compute_content_hash(record)
    return record


def unit_url(unit_code: str, year: int) -> str:
    return f"https://handbook.monash.edu/{year}/units/{unit_code.upper()}"
