"""Shared response checks: HTTP 200 alone does not establish usable content."""
from __future__ import annotations

import math
import re
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup


def retry_after(header: str | None, *, now: datetime | None = None) -> float | None:
    """Retry-After may be seconds or an HTTP date (RFC 9110)."""
    if not header:
        return None
    try:
        seconds = float(header.strip())
        return max(0.0, seconds) if math.isfinite(seconds) else None
    except ValueError:
        try:
            date = parsedate_to_datetime(header)
            if date.tzinfo is None:
                date = date.replace(tzinfo=UTC)
            return max(0.0, (date - (now or datetime.now(UTC))).total_seconds())
        except (TypeError, ValueError, OverflowError):
            return None


SOFT_404 = re.compile(r"(?:404\b|page not found\b|page cannot be found\b)")


def html_error(html: str) -> str | None:
    """Recognise error shells without matching policy prose about access/login."""
    soup = BeautifulSoup(html, "lxml")
    title = soup.title.get_text(" ", strip=True).casefold() if soup.title else ""
    if soup.select_one("#challenge-form, #cf-challenge-running, #challenge-running"):
        return "upstream challenge page"
    if title in {"just a moment...", "just a moment…", "请稍候…",
                 "attention required! | cloudflare"}:
        return "upstream challenge page"
    if title.startswith(("error: the request could not be satisfied", "access denied")):
        return "upstream access error page"
    # "Page Not Found | Monash University Malaysia" is served with a 200 at
    # /page-not-found and wherever Malaysia's CMS has lost a page.
    if SOFT_404.match(title):
        return "upstream soft 404"
    if soup.select_one('input[type="password"]') and any(
        word in title for word in ("sign in", "log in", "login")
    ):
        return "upstream sign-in page"
    return None


def is_html(content_type: str) -> bool:
    return content_type.split(";", 1)[0].strip().lower() in {
        "text/html", "application/xhtml+xml",
    }
