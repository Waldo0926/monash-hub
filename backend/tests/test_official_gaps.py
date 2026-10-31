"""Linked official pages that the index does not hold yet."""
from __future__ import annotations

from crawler.official.gaps import gaps, links

MY = "https://www.monash.edu.my"
AU = "https://www.monash.edu"


def para(*urls):
    return {"type": "paragraph", "spans": [{"text": "see", "url": url} for url in urls]}


def test_links_are_found_however_deep_a_block_nests_them():
    blocks = [para(f"{MY}/a"),
              {"type": "list", "items": [{"spans": [{"text": "x", "url": f"{MY}/b"}],
                                          "children": [{"spans": [{"url": f"{MY}/c"}]}]}]}]
    assert list(links(blocks)) == [f"{MY}/a", f"{MY}/b", f"{MY}/c"]


def test_a_page_linked_from_two_pages_and_not_seeded_is_listed_first():
    pages = [
        ("my-new", [para(f"{MY}/student-services/new-to-monash/lets-begin/enrolment2",
                         f"{MY}/student-services/student-admin/enrol-and-re-enrol/re-enrol/")]),
        ("my-admin", [para(f"{MY}/student-services/new-to-monash/lets-begin/enrolment2#top")]),
    ]
    known = [f"{MY}/student-services/student-admin/enrol-and-re-enrol/re-enrol"]
    assert gaps(pages, known) == [{
        "url": f"{MY}/student-services/new-to-monash/lets-begin/enrolment2",
        "links": 2, "from": ["my-admin", "my-new"],
    }]


def test_files_logins_old_years_and_other_sites_are_not_gaps():
    pages = [("p", [para(
        f"{MY}/student-services/form.pdf",
        f"{MY}/student-services/login",
        f"{AU}/students/admin/dates/principal-dates-2019",
        "https://www.example.com/students/help",
        f"{AU}/news/some-story",
        f"{AU}/medicine/research/a-lab",
    )])]
    assert gaps(pages, []) == []


def test_capitalisation_and_a_trailing_slash_do_not_make_a_new_page():
    pages = [("p", [para(f"{MY}/student-services/Student-Pass/")])]
    assert gaps(pages, [f"{MY}/student-services/student-pass"]) == []
