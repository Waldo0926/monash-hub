"""Pages that are short on Monash's site too, and pages sent off it."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from crawler.official import run
from crawler.official.fetch import PageResult
from crawler.official.seeds import Seed

MY = "https://www.monash.edu.my"
HUB = (
    "<html><head><title>Enrolment</title></head><body><main><h1>Enrolment</h1><ul>"
    + "".join(f'<li><a href="{MY}/student-services/student-admin/enrol-and-re-enrol/{p}">{label}</a></li>'
              for p, label in [("enrol-first-time", "Enrol for the first time"),
                               ("re-enrol", "Re-enrol"),
                               ("changing-your-enrolment", "Changing your enrolment"),
                               ("summer-and-winter", "Summer and winter semesters")])
    + "</ul></main></body></html>"
)
LONG = ("<html><head><title>Special consideration</title></head><body><main><h1>Special"
        " consideration</h1><p>" + "Apply within three working days of the due date. " * 20
        + "</p></main></body></html>")
EMPTIED = ("<html><head><title>Special consideration</title></head><body><main>"
           "<h1>Special consideration</h1></main></body></html>")


class Pages:
    def __init__(self, answers):
        self.answers = answers

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def fetch(self, url):
        return self.answers[url]


def _crawl(engine, monkeypatch, seed, answer):
    monkeypatch.setattr(run, "SessionLocal", sessionmaker(bind=engine))
    run.register((seed,))
    return run.crawl((seed,), min_interval=0, transport="auto",
                     fetcher=Pages({seed.url: answer}), force=True)


def _page(db, slug):
    from app.models.knowledge import OfficialPage

    db.expire_all()
    return db.scalar(select(OfficialPage).where(OfficialPage.slug == slug))


def test_a_hub_of_links_is_stored(db, engine, monkeypatch):
    seed = Seed("my-enrol", f"{MY}/student-services/student-admin/enrol-and-re-enrol",
                "Enrolment", "enrolment", ())
    ok = PageResult(seed.url, 200, HUB, "playwright", final_url=seed.url)
    assert _crawl(engine, monkeypatch, seed, ok)["new"] == 1
    page = _page(db, "my-enrol")
    assert page.status == "ok" and "Re-enrol" in page.clean_text


def test_a_long_page_that_reads_short_keeps_its_last_copy(db, engine, monkeypatch):
    seed = Seed("my-sc", f"{MY}/student-services/special-consideration2",
                "Special consideration", "assessment", ())
    _crawl(engine, monkeypatch, seed, PageResult(seed.url, 200, LONG, "playwright",
                                                 final_url=seed.url))
    kept = _page(db, "my-sc").clean_text
    summary = _crawl(engine, monkeypatch, seed, PageResult(seed.url, 200, EMPTIED, "playwright",
                                                           final_url=seed.url))
    assert summary["failed"] == 1
    page = _page(db, "my-sc")
    assert page.clean_text == kept and page.status == "ok"


def test_a_page_sent_to_a_sign_in_page_is_not_stored(db, engine, monkeypatch):
    seed = Seed("my-tool", f"{MY}/student-services/tool", "Tool", "support", ())
    okta = "https://monashuni.okta.com/app/x/sso/saml"
    summary = _crawl(engine, monkeypatch, seed, PageResult(seed.url, 200, HUB, "playwright",
                                                           final_url=okta))
    assert summary["failed"] == 1
    assert _page(db, "my-tool").content_hash is None
