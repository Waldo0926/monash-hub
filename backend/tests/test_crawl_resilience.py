"""What a crawl does when the upstream misbehaves.

The Handbook index failing once, the Handbook answering 404 for everything,
a page redirected somewhere else, one failed fetch of a page that was fine.
Each of these used to cost more than the one request: a week's crawl, every
unit on the site, a page's text, or the page itself.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import httpx
import pytest
from app.knowledge.repository import record_failure

from crawler.handbook import discover
from crawler.handbook.withdrawn import withdrawal_cap
from crawler.official.fetch import (
    AUTO_TRANSPORT,
    BROWSER_TRANSPORT,
    HTTP_TRANSPORT,
    OfficialFetcher,
    PageResult,
    redirected_up,
)
from crawler.sync.refresh import is_due
from crawler.throttling.limiter import RateLimit, Throttle
from tests.test_official_fetch import Scripted


def _instant(max_attempts: int = 3) -> Throttle:
    """A throttle that never sleeps, and remembers the pauses it was asked for."""
    limit = RateLimit(min_interval=0, jitter=0, backoff_base=0, backoff_max=0,
                      max_attempts=max_attempts)
    throttle = Throttle(limit)
    throttle.pauses = []
    throttle.backoff = lambda attempt, at_least=0.0: throttle.pauses.append(at_least)
    return throttle


def _index(*answers):
    """A transport that answers the index requests in order."""
    queue = list(answers)
    seen: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(int(request.url.params["from"]))
        return queue.pop(0)

    return httpx.MockTransport(handler), seen


def _page(total: int, *codes: str) -> httpx.Response:
    results = [{"uri": f"/2026/units/{c}", "code": c} for c in codes]
    return httpx.Response(200, json={"data": {"total": total, "results": results}})


# -- Handbook index ------------------------------------------------------------


def test_one_failed_index_page_is_retried_not_the_end_of_the_crawl():
    transport, seen = _index(
        _page(2, "FIT1045"),
        httpx.Response(503, headers={"Retry-After": "30"}),
        _page(2, "FIT1008"),
    )
    throttle = _instant()
    codes = discover._discover(2026, "units", throttle, transport=transport)
    assert codes == ["FIT1045", "FIT1008"]
    assert seen == [0, 1, 1]
    assert throttle.pauses == [30.0]


def test_an_index_that_keeps_failing_still_stops_the_run():
    transport, seen = _index(*[httpx.Response(502)] * 3)
    with pytest.raises(discover.DiscoveryError, match="after 3 attempts"):
        discover._discover(2026, "units", _instant(), transport=transport)
    assert seen == [0, 0, 0]


def test_an_index_answer_that_is_not_json_is_retried_too():
    transport, _ = _index(httpx.Response(200, text="<html>busy</html>"), _page(1, "FIT2004"))
    assert discover._discover(2026, "units", _instant(), transport=transport) == ["FIT2004"]


# -- Handbook withdrawals ------------------------------------------------------


def test_the_withdrawal_cap_is_small_for_a_small_run_and_two_percent_of_a_big_one():
    assert withdrawal_cap(1) == 25
    assert withdrawal_cap(914) == 25
    assert withdrawal_cap(5228) == 104


def test_a_handbook_that_404s_everything_retires_only_up_to_the_cap(db, engine, monkeypatch):
    from app.models.handbook import Unit
    from sqlalchemy import select
    from sqlalchemy.orm import sessionmaker

    from crawler.handbook import run
    from crawler.handbook.fetch import FetchResult

    codes = [f"FIT{n}" for n in range(1000, 1040)]
    for code in codes:
        db.add(Unit(unit_code=code, academic_year=2026, title=code, is_active=True,
                    content_hash=f"hash-{code}",
                    source_url=f"https://handbook.monash.edu/2026/units/{code}"))
    db.commit()

    class Gone:
        def __init__(self, throttle):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *exc_info):
            pass

        def fetch(self, url):
            return FetchResult(url=url, status=404, html=None, error="not found")

    monkeypatch.setattr(run, "SessionLocal", sessionmaker(bind=engine, expire_on_commit=False))
    monkeypatch.setattr(run, "HandbookFetcher", Gone)
    summary = run.crawl(codes, 2026, min_interval=0)

    assert summary["withdrawn"] == 25 and summary["failed"] == 15
    active = db.scalars(select(Unit.unit_code).where(Unit.is_active.is_(True))).all()
    assert len(active) == 15


# -- Official pages: redirects and robots ---------------------------------------


SEED = "https://www.monash.edu/students/admin/enrolments/census"


@pytest.mark.parametrize("final", [
    None,
    SEED,
    SEED + "/",
    SEED + "/index.html",
    "https://monash.edu/Students/Admin/Enrolments/Census?utm=x",
    "https://www.monash.edu/students/admin/enrolment-dates",
    SEED + "/dates",
])
def test_a_page_that_moved_sideways_or_was_tidied_is_still_followed(final):
    assert not redirected_up(SEED, final)


@pytest.mark.parametrize("final", [
    "https://www.monash.edu/students/admin/enrolments",
    "https://www.monash.edu/students/",
    "https://www.monash.edu/",
])
def test_a_page_sent_to_the_section_above_it_is_not_a_page(final):
    assert redirected_up(SEED, final)


class Redirected(Scripted):
    def __init__(self, final_url, **kwargs):
        super().__init__([(200, None)] * 3, **kwargs)
        self.final_url = final_url

    def _fetch_once(self, url):
        result = super()._fetch_once(url)
        return PageResult(url, result.status, result.html, result.transport,
                          final_url=self.final_url)


def test_a_page_redirected_to_its_section_is_not_stored_or_retried():
    fetcher = Redirected("https://www.monash.edu/students/admin/enrolments")
    result = fetcher.fetch(SEED)
    assert not result.ok and result.html is None
    assert result.error == "redirected to https://www.monash.edu/students/admin/enrolments"
    assert len(fetcher.asked) == 1


def test_a_robots_file_the_waf_refuses_is_read_with_the_browser():
    class Browser(OfficialFetcher):
        def _robots_browser(self, url):
            self.browser_asked = url
            return 200, "User-agent: *\nDisallow: /private/\n"

    with Browser(_instant(), transport=AUTO_TRANSPORT) as fetcher:
        fetcher._client = httpx.Client(transport=httpx.MockTransport(
            lambda _: httpx.Response(403, text="<html>challenge</html>")))
        assert fetcher.robots.allowed("https://www.monash.edu.my/finance")
        assert not fetcher.robots.allowed("https://www.monash.edu.my/private/x")
        assert fetcher.browser_asked == "https://www.monash.edu.my/robots.txt"
        assert fetcher.transport == BROWSER_TRANSPORT


def test_a_robots_file_refused_with_an_explicit_transport_still_closes_the_host():
    with OfficialFetcher(_instant(), transport=HTTP_TRANSPORT) as fetcher:
        fetcher._client = httpx.Client(transport=httpx.MockTransport(
            lambda _: httpx.Response(403)))
        assert not fetcher.robots.allowed("https://www.monash.edu.my/finance")


# -- Official pages: one failure does not take a page down -----------------------


class _Db:
    def flush(self):
        pass


def _page_row(**kwargs):
    defaults = {
        "status": "ok",
        "content_hash": "abc",
        "fetch_error": None,
        "last_checked": datetime(2026, 10, 20, tzinfo=UTC),
        "refresh_tier": "stable",
    }
    return SimpleNamespace(**(defaults | kwargs))


def test_a_failed_fetch_keeps_a_good_page_on_the_site():
    page = _page_row()
    record_failure(_Db(), page, "HTTP 403")
    assert page.status == "ok"
    assert page.fetch_error == "HTTP 403"
    assert page.last_checked == datetime(2026, 10, 20, tzinfo=UTC)


def test_a_page_hidden_by_an_earlier_failure_comes_back():
    page = _page_row(status="error")
    record_failure(_Db(), page, "ReadTimeout")
    assert page.status == "ok"


def test_a_page_monash_removed_comes_down():
    page = _page_row()
    record_failure(_Db(), page, "HTTP 404", gone=True)
    assert page.status == "error"


def test_a_page_never_read_is_still_marked_as_an_error():
    page = _page_row(status="pending", content_hash=None, last_checked=None)
    record_failure(_Db(), page, "HTTP 503")
    assert page.status == "error"


def test_a_page_whose_last_attempt_failed_is_due_again():
    now = datetime(2026, 10, 21, tzinfo=UTC)
    assert not is_due(_page_row(), now=now)
    assert is_due(_page_row(fetch_error="HTTP 403"), now=now)
    assert is_due(_page_row(last_checked=now - timedelta(days=15)), now=now)


def test_a_redirect_off_the_approved_pages_is_not_asked_again():
    class Away(Scripted):
        def _fetch_once(self, url):
            self.asked.append((self._mode, url))
            return PageResult(url, 302, None, self._mode, "redirect outside approved public pages")

    fetcher = Away([])
    result = fetcher.fetch("https://www.monash.edu.my/student-services/redirects/career-fair-2017")
    assert result.status == 302 and len(fetcher.asked) == 1
