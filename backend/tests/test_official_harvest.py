"""Pages read on a member's computer and stored on the server."""
from __future__ import annotations

import gzip
import json
from datetime import UTC, datetime, timedelta

from crawler.official import harvest
from crawler.official.fetch import PageResult
from crawler.official.seeds import Seed

MY = "https://www.monash.edu.my"
ARTICLE = "<html><head><title>Student pass</title></head><body><main><h1>Student pass</h1>" + (
    "<p>" + "Renew your student pass before it expires. " * 10 + "</p>"
) + "<table><tr><th>Item</th><th>Fee (RM)</th></tr><tr><td>Renewal</td><td>500</td></tr></table>"\
    "</main></body></html>"
SEEDS = (
    Seed("my-pass", f"{MY}/student-services/student-pass", "Student pass", "international", ()),
    Seed("my-gone", f"{MY}/student-services/old", "Old", "support", ()),
    Seed("my-login", f"{MY}/student-services/portal", "Portal", "support", (), sign_in="x"),
    Seed("au-page", "https://www.monash.edu/students/admin", "Admin", "enrolment", ()),
)


class Scripted:
    def __init__(self):
        self.asked = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def fetch(self, url):
        self.asked.append(url)
        if url.endswith("/old"):
            return PageResult(url, 404, None, "playwright", "HTTP 404")
        return PageResult(url, 200, ARTICLE, "playwright", final_url=url)


def test_only_the_hosts_public_pages_are_read_and_a_rerun_resumes(tmp_path, monkeypatch):
    monkeypatch.setattr(harvest, "SEEDS", SEEDS)
    out = str(tmp_path / "my.jsonl.gz")
    first = Scripted()
    assert harvest.harvest("www.monash.edu.my", out, min_interval=0, fetcher=first) == {
        "ok": 1, "failed": 1}
    assert first.asked == [SEEDS[0].url, SEEDS[1].url]
    again = Scripted()
    harvest.harvest("www.monash.edu.my", out, min_interval=0, fetcher=again)
    assert again.asked == []


def _write(path, records):
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")


def _record(url, when, status=200, html=ARTICLE):
    return {"url": url, "status": status, "html": html, "transport": "playwright",
            "error": None if status == 200 else f"HTTP {status}", "final_url": url,
            "fetched_at": when.isoformat()}


def test_a_stale_read_is_skipped_and_the_last_read_wins(tmp_path):
    now = datetime(2026, 10, 25, tzinfo=UTC)
    path = str(tmp_path / "h.jsonl.gz")
    _write(path, [
        _record(f"{MY}/a", now - timedelta(days=5)),
        _record(f"{MY}/b", now - timedelta(hours=2), status=403, html=None),
        _record(f"{MY}/b", now - timedelta(hours=1)),
    ])
    fetcher = harvest.HarvestedFetcher(path, now=now)
    assert fetcher.urls == {f"{MY}/b"}
    result = fetcher.fetch(f"{MY}/b")
    assert result.ok and result.transport == "relayed-playwright"


def test_a_torn_last_line_does_not_lose_the_rest(tmp_path):
    path = tmp_path / "h.jsonl"
    now = datetime.now(UTC)
    path.write_text(json.dumps(_record(f"{MY}/a", now)) + "\n" + '{"url": "torn', encoding="utf-8")
    assert harvest.HarvestedFetcher(str(path)).urls == {f"{MY}/a"}


def test_the_server_stores_a_harvested_page_with_its_own_cleaner(db, engine, tmp_path,
                                                                   monkeypatch):
    from app.models.knowledge import OfficialPage
    from sqlalchemy import select
    from sqlalchemy.orm import sessionmaker

    from crawler.official import run

    now = datetime.now(UTC)
    path = str(tmp_path / "h.jsonl.gz")
    _write(path, [_record(SEEDS[0].url, now), _record(SEEDS[1].url, now, status=404, html=None)])
    monkeypatch.setattr(run, "SessionLocal", sessionmaker(bind=engine))
    seeds = SEEDS[:2]
    run.register(seeds)
    summary = run.crawl(seeds, min_interval=0, transport="relayed",
                        fetcher=harvest.HarvestedFetcher(path))
    assert summary["new"] == 1 and summary["failed"] == 1
    pages = {p.slug: p for p in db.scalars(select(OfficialPage)).all()}
    stored = pages["my-pass"]
    assert stored.status == "ok"
    assert any(b["type"] == "table" for b in stored.blocks)
    assert pages["my-gone"].status == "error"


class Refused(Scripted):
    def fetch(self, url):
        self.asked.append(url)
        return PageResult(url, 403, None, "playwright", "HTTP 403")


def test_a_forced_run_that_cannot_read_a_page_keeps_its_last_good_date(db, engine, monkeypatch):
    """The --all run on 2026-10-25 cleared last_checked before fetching, and
    the 359 Malaysia pages it was refused on lost the date readers are shown."""
    from app.models.knowledge import OfficialPage
    from sqlalchemy import select
    from sqlalchemy.orm import sessionmaker

    from crawler.official import run

    monkeypatch.setattr(run, "SessionLocal", sessionmaker(bind=engine))
    seeds = SEEDS[:1]
    run.register(seeds)
    run.crawl(seeds, min_interval=0, transport="auto", fetcher=Scripted())
    page = db.scalar(select(OfficialPage).where(OfficialPage.slug == "my-pass"))
    read_at = page.last_checked
    refused = Refused()
    summary = run.crawl(seeds, min_interval=0, transport="auto", fetcher=refused, force=True)
    assert refused.asked == [seeds[0].url] and summary["failed"] == 1
    db.expire_all()
    page = db.scalar(select(OfficialPage).where(OfficialPage.slug == "my-pass"))
    assert page.last_checked == read_at and page.status == "ok"
