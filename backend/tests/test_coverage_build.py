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


def test_research_staff_alumni_and_microsites_are_not_for_students():
    left_out = [
        "/research/researchers-say/from-pollution-to-products",
        "/science/research/research-facilities/food-science/texture-analyzer",
        "/engineering/about-us/all-staff/mechatronics-engineering/dr-someone",
        "/IT/our-alumni/someone", "/study-abroad/testimonials/a-student",
        "/rhs2/rhs-modules/study/lets-talk2", "/paced/bcac", "/science/tbcg2026",
        "/it/mind-engine-expo-2026/agenda", "/science/icamr-2025", "/about/career/vacancies",
        "/sass/nested-content/block", "/education-excellence/designing-for-learning/x",
        "/student-services/feedback", "/engineering/x/34th-symposium-of-engineers2024/about",
        "/business/-/current-student-mockup/course-maps", "/event-attendance/thank-attendee",
        "/COVID19-updates/teaching", "/mdp/aep/about",
    ]
    rows = build([page(f"{MY}{path}", path) for path in left_out], {}, [])
    assert urls(rows) == []
    kept = ["/study/S3701", "/student-services/student-admin/fees-2027",
            "/mumgro/current-students/scholarships", "/study/postgraduate-and-research/apply",
            "/food-and-retail/vendors/a-cafe", "/research/support-and-scholarships",
            "/students/support/disability/services/research",
            "/students/admin/assessments/results/feedback"]
    assert len(build([page(f"{MY}{path}", path) for path in kept], {}, [])) == len(kept)


def test_a_page_already_listed_stays_when_discovery_was_refused_on_it():
    exam = f"{MY}/student-services/student-admin/examinations-results/remote-eexams"
    moved = f"{MY}/study/scholarships-and-study-loans/old"
    gone = f"{MY}/student-services/old-page"
    previous = (
        ("my-remote-eexams", exam, "Remote eExams", "assessment", ("考试",), "daily", "malaysia"),
        ("my-old-loans", moved, "Loans", "fees-dates", ("贷款",), "weekly", "malaysia"),
        ("my-old-page", gone, "Old", "support", (), "weekly", "malaysia"),
    )
    pages = [
        {"url": exam, "status": 403, "error": "HTTP 403"},
        {"url": moved, "status": None, "http": 200, "error": "redirect outside approved pages"},
        {"url": gone, "status": 404, "error": "HTTP 404"},
    ]
    rows = build(pages, {}, [], {row[1]: row[0] for row in previous}, previous)
    assert [(row["url"], row["slug"]) for row in rows] == [(exam, "my-remote-eexams")]


def test_a_listed_page_no_sitemap_names_stays_while_production_has_its_text():
    exam = f"{MY}/student-services/student-admin/examinations-results/remote-eexams"
    empty = f"{MY}/student-services/empty"
    previous = (
        ("my-remote-eexams", exam, "Remote eExams", "assessment", ("考试",), "daily", "malaysia"),
        ("my-empty", empty, "Empty", "support", (), "weekly", "malaysia"),
    )
    texts = {exam: {"text": "x" * 2000}, empty: {"text": "short"}}
    rows = build([page(f"{MY}/student-services/student-admin", "w")], texts, [],
                 {row[1]: row[0] for row in previous}, previous)
    assert sorted(urls(rows)) == sorted([f"{MY}/student-services/student-admin", exam])


def test_a_listed_page_now_at_another_address_is_kept_once():
    old = f"{MY}/it/current-students/Course-Offered/postgraduates/transfers"
    new = f"{MY}/it/current-students/postgraduate/postgraduates/transfers"
    previous = (("my-old-transfers", old, "Transfers", "enrolment", (), "medium", "malaysia"),)
    text = "Students who wish to transfer to another course must apply. " * 30
    texts = {old: {"text": text, "hash": "made by an older extractor"}}
    moved = {**page(new, "new hash"), "len": len(text) + 4, "head": text[:300]}
    rows = build([moved], texts, [], {old: "my-old-transfers"}, previous)
    assert urls(rows) == [new]


def test_of_two_addresses_with_the_same_text_the_central_one_is_kept():
    central = f"{MY}/student-services/student-admin/re-enrol"
    copy = f"{MY}/science/current/current/re-enrol"
    previous = (("malaysia-re-enrol", central, "Re-enrol", "enrolment", (), "medium", "malaysia"),)
    text = "Re-enrolment for next year opens in October for continuing students. " * 20
    texts = {central: {"text": text}}
    twin = {**page(copy, "h"), "len": len(text), "head": text[:300]}
    rows = build([twin], texts, [], {central: "malaysia-re-enrol"}, previous)
    assert [(row["url"], row["slug"]) for row in rows] == [(central, "malaysia-re-enrol")]
