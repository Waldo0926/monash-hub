"""What the coverage build keeps when discovery finds a page more than once."""
from __future__ import annotations

from crawler.official.coverage import build

MY = "https://www.monash.edu.my"
TEXT = 600


def page(url, digest, title="A page", status=200):
    return {"url": url, "status": status, "title": title, "len": TEXT, "hash": digest}


def urls(rows):
    return [row["url"] for row in rows]


def test_one_address_however_it_is_capitalised():
    rows = build([page(f"{MY}/study-abroad/outbound/Semester-in-Australia", "a"),
                  page(f"{MY}/study-abroad/outbound/semester-in-australia/", "b")], {}, [])
    assert urls(rows) == [f"{MY}/study-abroad/outbound/Semester-in-Australia"]


def test_the_same_text_is_kept_once_at_the_shortest_address():
    rows = build([page(f"{MY}/our-schools/school-of-information-technology", "it"),
                  page(f"{MY}/it/home", "it"),
                  page(f"{MY}/it", "it")], {}, [])
    assert urls(rows) == [f"{MY}/it"]


def test_an_address_already_in_the_coverage_list_keeps_its_place():
    known = {f"{MY}/it/home": "it-home"}
    rows = build([page(f"{MY}/it", "it"), page(f"{MY}/it/home", "it")], {}, [], known)
    assert urls(rows) == [f"{MY}/it/home"]
    assert rows[0]["slug"] == "it-home"


def test_a_page_titled_not_found_and_failures_are_left_out():
    rows = build([page(f"{MY}/old-page", "x", title="Page Not Found | Monash University Malaysia"),
                  page(f"{MY}/a.pdf-page", "y", status=None),
                  page(f"{MY}/search", "z"),
                  page(f"{MY}/student-services/student-admin", "w")], {}, [])
    assert urls(rows) == [f"{MY}/student-services/student-admin"]


def test_a_page_whose_text_was_the_cookie_banner_is_left_out():
    banner = {**page(f"{MY}/law/international-opportunities", "c"), "len": 320,
              "head": "We use cookies to improve your experience on our website."}
    assert build([banner], {}, []) == []
