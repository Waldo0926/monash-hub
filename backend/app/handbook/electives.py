"""Conservative browsing hints from original English requirement text.

These never become curriculum items or planner eligibility rules. A level-only
search cannot establish approval, prerequisites or faculty restrictions.
"""
import re


def elective_browse(title: str | None, description: str | None) -> dict | None:
    text = f"{title or ''}\n{description or ''}"
    if not re.search(r"\belectives?\b", text, re.I):
        return None
    # Match both 'Level 4 or Level 5' and 'Level 4 or 5'. Avoid consuming
    # credit-point counts or the years mentioned elsewhere in the paragraph.
    levels: set[int] = set()
    for match in re.finditer(
        r"\blevels?\s+([1-6])((?:\s*(?:,|/|and|or|&|-)\s*(?:level\s*)?[1-6])*)",
        text, re.I,
    ):
        values = [int(v) for v in re.findall(r"[1-6]", match.group())]
        if "-" in match.group() and len(values) == 2:
            levels.update(range(min(values), max(values) + 1))
        else:
            levels.update(values)
    # Free electives can be browsed even when no explicit level is published.
    free = bool(re.search(r"\bfree\s+electives?\b|across the University", text, re.I))
    return {"levels": [f"Level {level}" for level in sorted(levels)], "free": free}
