"""The server says which pages a harvest on another machine should read."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from crawler.official.due import due_slugs
from crawler.official.seeds import Seed

NOW = datetime(2026, 10, 28, tzinfo=UTC)


def _seed(slug, host="www.monash.edu.my", **kwargs):
    return Seed(slug=slug, url=f"https://{host}/{slug}", title=slug, category="admin",
                tags=(), **kwargs)


def _page(**kwargs):
    defaults = {"status": "ok", "fetch_error": None, "refresh_tier": "stable",
                "last_checked": NOW - timedelta(days=1)}
    return SimpleNamespace(**(defaults | kwargs))


def test_only_due_pages_on_the_host_are_asked_for():
    seeds = [
        _seed("fresh"),
        _seed("old", tier="dynamic"),
        _seed("refused"),
        _seed("never-read"),
        _seed("behind-sign-in", sign_in="the student portal"),
        _seed("other-site", host="www.monash.edu"),
    ]
    pages = {
        "https://www.monash.edu.my/fresh": _page(),
        "https://www.monash.edu.my/old": _page(refresh_tier="dynamic",
                                               last_checked=NOW - timedelta(hours=13)),
        "https://www.monash.edu.my/refused": _page(fetch_error="robots.txt unavailable"),
        "https://www.monash.edu/other-site": _page(fetch_error="HTTP 403"),
    }
    assert due_slugs(seeds, pages, "www.monash.edu.my", now=NOW) == [
        "old", "refused", "never-read"]


def test_nothing_due_is_an_empty_list():
    # The relay skips the host then; an empty --slugs would read every page.
    seeds = [_seed("fresh")]
    pages = {"https://www.monash.edu.my/fresh": _page()}
    assert due_slugs(seeds, pages, "www.monash.edu.my", now=NOW) == []
