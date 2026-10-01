"""Which campus an official page is labelled for - crawler/official/scope.py."""
from __future__ import annotations

import pytest

from crawler.official.coverage import build, category, clean_title
from crawler.official.scope import ALL, AUSTRALIA, MALAYSIA, scope

AU = "https://www.monash.edu/students/admin"
MY = "https://www.monash.edu.my/student-services"


@pytest.mark.parametrize(
    "url,title,text,expected",
    [
        # The Malaysia site is Malaysia, whatever it says.
        (f"{MY}/student-admin/fees", "Fees", "All campuses pay by JomPAY.", MALAYSIA),
        # monash.edu carries the Malaysian ceremonies too.
        (f"{AU}/graduations/upcoming/april-malaysia", "April graduations", "", MALAYSIA),
        # Anything only Australia has makes the page Australian, even beside Malaysia.
        (f"{AU}/fees/loans", "Loans", "HECS-HELP is available. Monash Malaysia differs.",
         AUSTRALIA),
        (f"{AU}/fees/oshc", "Health cover", "You must hold OSHC for your visa.", AUSTRALIA),
        (f"{AU}/assessments/on-campus", "On-campus eExams (Australia)", "Bring your ID.",
         AUSTRALIA),
        # Says it covers every campus, or speaks to Malaysia alongside.
        (f"{AU}/assessments/special", "Special consideration",
         "This applies to students at all Monash University campuses and locations.", ALL),
        (f"{AU}/graduations/all-dates", "All graduation dates",
         "Ceremonies in Australia, Malaysia and Indonesia.", ALL),
        # ... unless it mentions Malaysia to send those students elsewhere.
        (f"{AU}/enrolments/re-enrol", "Re-enrol",
         "Students at Monash Malaysia should refer to monash.edu.my for re-enrolment.",
         AUSTRALIA),
        # A University-wide rule binds every campus.
        ("https://www.monash.edu/students/study-success/academic-integrity",
         "Academic integrity", "Plagiarism and collusion are misconduct.", ALL),
        (f"{AU}/policies/student-conduct", "Student Code of Conduct", "Be respectful.", ALL),
        # Otherwise, the site it is on.
        (f"{AU}/timetables/allocate", "Allocate+", "Choose your classes.", AUSTRALIA),
    ],
)
def test_campus_comes_from_what_the_page_says(url, title, text, expected):
    assert scope(url, title, text)[0] == expected


def test_a_university_rule_with_australian_content_is_australian():
    applies_to, reason = scope(
        "https://www.monash.edu/students/support/complaints/fees",
        "Fee complaints", "Complaints about FEE-HELP go to the Ombudsman.")
    assert applies_to == AUSTRALIA
    assert "FEE-HELP" in reason


def _page(url, length=1000, digest=None, **extra):
    return {"url": url, "status": 200, "title": "A page - Current Students", "len": length,
            "hash": digest or url, "depth": 1, **extra}


def test_coverage_leaves_out_what_the_hub_does_not_index():
    pages = [
        _page(f"{MY}/student-admin/fees"),
        _page(f"{MY}/student-admin/landing", length=200),  # only links elsewhere
        _page("https://www.monash.edu/study-abroad/outbound/program-search/university-of-vienna"),
        _page("https://www.monash.edu/study-abroad/outbound/program-search/summer-in-prato"),
        _page("https://www.monash.edu.my/study/apply/monash-malaysia-agents/china"),
        _page(f"{AU}/fees/contact-us"),
        {"url": f"{AU}/gone", "status": 404},
    ]
    urls = {row["url"] for row in build(pages, {}, [])}
    assert urls == {
        f"{MY}/student-admin/fees",
        "https://www.monash.edu/study-abroad/outbound/program-search/summer-in-prato",
    }


def test_coverage_keeps_one_address_per_text_and_puts_malaysia_first():
    pages = [
        _page("https://www.monash.edu/study-abroad/overseas/safety", digest="same"),
        _page("https://www.monash.edu/study-abroad/outbound/safety", digest="same"),
        _page(f"{AU}/enrolments/re-enrol"),
        _page(f"{MY}/student-admin/enrol"),
    ]
    rows = build(pages, {}, [])
    assert [r["url"] for r in rows if "safety" in r["url"]] == \
        ["https://www.monash.edu/study-abroad/outbound/safety"]
    assert rows[0]["applies_to"] == MALAYSIA


def test_a_page_without_stored_text_is_not_claimed_for_every_campus():
    """"all" needs the page's text; until it is crawled the site decides."""
    url = "https://www.monash.edu/students/study-success/academic-integrity/more"
    without = build([_page(url)], {}, [])
    with_text = build([_page(url)], {url: {"text": "Applies at all campuses."}}, [])
    assert without[0]["applies_to"] == AUSTRALIA
    assert with_text[0]["applies_to"] == ALL


def test_titles_and_categories():
    assert clean_title("Fee payment methods - Monash University Malaysia",
                       f"{MY}/fees") == "Fee payment methods (Monash Malaysia)"
    assert category(f"{AU}/graduations/apply") == "graduation"
    # An undergraduate page is not about graduating.
    assert category("https://www.monash.edu.my/sass/current/undergraduate/faq") == "enrolment"
    assert category("https://www.monash.edu/study-abroad/outbound/exchange") == "exchange"
