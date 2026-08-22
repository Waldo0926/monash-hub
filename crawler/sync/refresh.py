"""How often each kind of page is worth re-checking.

Important dates move; a policy explainer does not. Re-reading everything at the
same cadence would either hammer stable pages or let deadlines go stale, so the
tier lives on the page row and this table turns it into an interval.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.models.knowledge import OfficialPage

REFRESH_INTERVALS = {
    "dynamic": timedelta(hours=12),   # census dates, deadlines, important dates
    "medium": timedelta(days=2),      # admin how-tos, application steps
    "stable": timedelta(days=14),     # long-lived policy and explainer text
}
DEFAULT_INTERVAL = REFRESH_INTERVALS["medium"]


def is_due(page: OfficialPage, *, now: datetime | None = None) -> bool:
    if page.last_checked is None or page.status != "ok":
        return True
    now = now or datetime.now(UTC)
    interval = REFRESH_INTERVALS.get(page.refresh_tier, DEFAULT_INTERVAL)
    return now - page.last_checked >= interval
