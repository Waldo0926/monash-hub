"""A crawl that goes wrong is stopped early, recorded, and reported.

A Handbook outage used to run until systemd killed it, leave the job marked
"running" for good, and show up nowhere but journalctl.
"""
from __future__ import annotations

import os
import signal
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from app.models.crawl import CrawlJob
from sqlalchemy import select

from crawler.official.fetch import OfficialFetcher
from crawler.sync import alert
from crawler.sync.pipeline import UpstreamDown, crawl_job, record


def _fail(db, job, key):
    record(db, job, target_type="handbook_unit", target_key=key, url=f"https://x/{key}",
           outcome="failed", http_status=503, message="HTTP 503")


def _ok(db, job, key):
    record(db, job, target_type="handbook_unit", target_key=key, url=f"https://x/{key}",
           outcome="unchanged", http_status=200)


# -- stopping early -------------------------------------------------------------


def test_a_run_of_failures_stops_the_crawl_and_says_why(db):
    with pytest.raises(UpstreamDown), crawl_job(db, "handbook", targets=100,
                                                 stop_after_failures=3) as job:
        for n in range(100):
            _fail(db, job, f"FIT{n}")
    job = db.scalar(select(CrawlJob))
    assert job.status == "failed"
    assert job.failed == 3
    assert "3 targets failed in a row" in job.notes


def test_a_success_in_between_resets_the_count(db):
    with crawl_job(db, "handbook", targets=6, stop_after_failures=3) as job:
        for n in range(3):
            _fail(db, job, f"A{n}")
            _fail(db, job, f"B{n}")
            _ok(db, job, f"C{n}")
    assert db.scalar(select(CrawlJob)).status == "partial"


def test_the_official_run_does_not_stop_on_one_site_refusing(db):
    # No limit: the next seed may be on a host that answers.
    with crawl_job(db, "official", targets=50) as job:
        for n in range(50):
            _fail(db, job, f"page-{n}")
    assert db.scalar(select(CrawlJob)).failed == 50


def test_the_handbook_crawl_gives_up_on_a_handbook_that_is_down(db, engine, monkeypatch):
    from sqlalchemy.orm import sessionmaker

    from crawler.handbook import run
    from crawler.handbook.fetch import FetchResult

    class Down:
        def __init__(self, throttle):
            self.asked = 0

        def __enter__(self):
            return self

        def __exit__(self, *exc_info):
            pass

        def fetch(self, url):
            return FetchResult(url=url, status=503, html=None, error="HTTP 503")

    monkeypatch.setattr(run, "SessionLocal", sessionmaker(bind=engine, expire_on_commit=False))
    monkeypatch.setattr(run, "HandbookFetcher", Down)
    with pytest.raises(UpstreamDown):
        run.crawl([f"FIT{n}" for n in range(1000, 1100)], 2026, min_interval=0)
    assert db.scalar(select(CrawlJob)).failed == run.MAX_FAILED_IN_A_ROW


# -- never left "running" ---------------------------------------------------------


def test_systemd_stopping_a_run_marks_it_failed(db):
    before = signal.getsignal(signal.SIGTERM)
    with pytest.raises(SystemExit), crawl_job(db, "handbook", targets=1):
        os.kill(os.getpid(), signal.SIGTERM)
    job = db.scalar(select(CrawlJob))
    assert job.status == "failed" and job.notes.startswith("SystemExit")
    assert signal.getsignal(signal.SIGTERM) is before


def test_a_job_left_running_by_an_older_run_is_closed(db):
    db.add_all([
        CrawlJob(job_type="handbook", status="running",
                 started_at=datetime.now(UTC) - timedelta(days=7)),
        CrawlJob(job_type="official", status="running",
                 started_at=datetime.now(UTC) - timedelta(days=7)),
    ])
    db.commit()
    with crawl_job(db, "handbook", targets=0):
        pass
    statuses = dict(db.execute(
        select(CrawlJob.id, CrawlJob.status).order_by(CrawlJob.id)).all())
    # Only its own kind: the official row is the official run's business.
    assert statuses == {1: "failed", 2: "running", 3: "ok"}


# -- reporting -------------------------------------------------------------------


def _job(**kwargs):
    defaults = {"id": 7, "status": "ok", "targets": 200, "failed": 0, "notes": None,
                "started_at": datetime(2026, 10, 25, 2, 10, tzinfo=UTC)}
    job = defaults | kwargs
    # By default the run asked about every target on its list.
    job.setdefault("fetched", job["targets"] - job["failed"])
    return SimpleNamespace(**job)


@pytest.mark.parametrize("job, expected", [
    (_job(), None),
    (_job(status="partial", failed=4), None),
    (_job(status="partial", targets=40, failed=5), "5 of the 40 targets it tried failed"),
    (_job(status="partial", failed=9), None),
    (_job(status="partial", failed=11), "11 of the 200 targets it tried failed"),
    # The official refresh on 2026-10-27: every due page failed, and the mail
    # called it 194 of 2917.
    (_job(status="partial", targets=2917, fetched=0, failed=194),
     "194 of the 194 targets it tried failed (2917 on its list)"),
    # 8 of 2917 is under the share, 8 of the 28 pages that were due is not.
    (_job(status="partial", targets=2917, fetched=20, failed=8),
     "8 of the 28 targets it tried failed"),
    (_job(status="partial", targets=2917, fetched=180, failed=8), None),
    (_job(status="failed", notes="UpstreamDown: 30 targets failed in a row"), "UpstreamDown"),
    (_job(status="running"), "still marked running"),
    (None, "no run on record"),
])
def test_what_is_worth_an_email(job, expected):
    found = alert.problems(job, "official")
    if expected is None:
        assert found == []
    else:
        assert len(found) == 1 and expected in found[0]


def test_the_mail_says_what_went_wrong():
    reasons = [("HTTP 404", 6), ("TimeoutError: Page.goto: Timeout 45000ms exceeded.", 3),
               ("HTTP 500", 2), ("HTTP 502", 1)]
    found = alert.problems(_job(status="partial", failed=12), "official", reasons)
    assert found[1:] == ["  6 x HTTP 404",
                         "  3 x TimeoutError: Page.goto: Timeout 45000ms exceeded.",
                         "  2 x HTTP 500"]


def test_a_refused_server_is_told_to_harvest():
    reasons = [("robots.txt unavailable - crawl permission unknown", 190), ("HTTP 404", 4)]
    job = _job(status="partial", targets=2917, fetched=0, failed=194)
    assert "crawler.official.harvest" in alert.problems(job, "official", reasons)[-1]
    # The Handbook has no harvest, and a few refusals among other failures
    # are not the server being turned away.
    assert "harvest" not in "\n".join(alert.problems(job, "handbook", reasons))
    mixed = [("HTTP 404", 100), ("HTTP 403", 94)]
    assert "harvest" not in "\n".join(alert.problems(job, "official", mixed))


def test_a_harvest_that_stopped_coming_is_reported():
    # _job() started at 2026-10-25 02:10 UTC.
    limit = timedelta(hours=72)
    assert alert.too_old(_job(), "official", limit,
                         now=datetime(2026, 10, 28, 2, 0, tzinfo=UTC)) == []
    found = alert.too_old(_job(), "official", limit,
                          now=datetime(2026, 10, 29, 6, 10, tzinfo=UTC))
    assert len(found) == 1
    assert "#7 (2026-10-25 02:10 UTC), is 4d 4h old, past the 72 hours" in found[0]
    assert "official-harvest" in found[0]
    # No run at all is the other check's to say.
    assert alert.too_old(None, "official", limit) == []


@pytest.mark.parametrize("message, label", [
    (None, "no message"),
    ("", "no message"),
    ("HTTP 403", "HTTP 403"),
    ("redirected to https://www.monash.edu/students/x", "redirected to <url>"),
    ("Error: Page.goto: net::ERR_ABORTED at https://www.monash.edu.my/a\n"
     "Call log:\n  - navigating to ...", "Error: Page.goto: net::ERR_ABORTED at <url>"),
])
def test_failures_are_grouped_by_kind(message, label):
    assert alert.reason(message) == label


def test_health_shows_the_last_run_of_each_kind(client, db):
    week_ago = datetime.now(UTC) - timedelta(days=7)
    db.add_all([
        CrawlJob(job_type="handbook", status="failed", notes="UpstreamDown: down",
                 started_at=week_ago, finished_at=week_ago),
        CrawlJob(job_type="official", status="ok", finished_at=datetime.now(UTC)),
        CrawlJob(job_type="official", status="partial", failed=2,
                 finished_at=datetime.now(UTC)),
    ])
    db.commit()
    data = client.get("/api/health").json()["data"]
    assert data["last_crawl"]["type"] == "official"
    assert data["crawls"]["handbook"]["status"] == "failed"
    assert data["crawls"]["handbook"]["notes"] == "UpstreamDown: down"
    assert data["crawls"]["official"]["status"] == "partial"
    assert data["handbook_overdue"] is True


def test_health_does_not_call_a_fresh_install_overdue(client, db):
    assert client.get("/api/health").json()["data"]["handbook_overdue"] is None


# -- a crashed browser page ------------------------------------------------------


class _Page:
    def __init__(self, closed=False):
        self.closed = closed
        self.context = SimpleNamespace(close=lambda: None)

    def is_closed(self):
        return self.closed


def _fetcher(page):
    fetcher = OfficialFetcher()
    fetcher._page = page
    fetcher._browser = SimpleNamespace(is_connected=lambda: True)
    return fetcher


def test_a_timeout_keeps_the_page():
    fetcher = _fetcher(_Page())
    assert not fetcher._page_broken(TimeoutError("Timeout 45000ms exceeded"))


def test_a_crashed_page_is_replaced_but_not_forever():
    fetcher = _fetcher(_Page())
    for _ in range(2):
        assert fetcher._page_broken(RuntimeError("Page crashed"))
        fetcher._reset_browser_page()
        assert fetcher._page is None
        fetcher._page = _Page(closed=True)
    assert not fetcher._page_broken(RuntimeError("Page crashed"))
