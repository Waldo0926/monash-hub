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
    # The address Monash lists now, under the slug its translations hang on.
    assert [(row["url"], row["slug"]) for row in rows] == [(new, "my-old-transfers")]


def test_a_schools_copy_does_not_replace_the_central_page():
    central = f"{MY}/student-services/student-admin/re-enrol"
    copy = f"{MY}/science/current/current/re-enrol"
    previous = (("malaysia-re-enrol", central, "Re-enrol", "enrolment", (), "medium", "malaysia"),)
    text = "Re-enrolment for next year opens in October for continuing students. " * 20
    texts = {central: {"text": text}}
    twin = {**page(copy, "h"), "len": len(text), "head": text[:300]}
    rows = build([twin], texts, [], {central: "malaysia-re-enrol"}, previous)
    assert [(row["url"], row["slug"]) for row in rows] == [(central, "malaysia-re-enrol")]


def test_of_two_live_copies_the_student_services_one_is_kept():
    services = f"{MY}/student-services/financial-assistance/undergraduate-scholarships-and-bursaries/other-financial-support"
    fees = f"{MY}/study/undergraduate/fees/sibling-discount2"
    assert urls(build([page(fees, "same"), page(services, "same")], {}, [])) == [services]


def test_an_old_home_copy_is_the_last_choice():
    rows = build([page(f"{MY}/student-services/home-old/m-pass", "m"),
                  page(f"{MY}/m-pass", "m")], {}, [])
    assert urls(rows) == [f"{MY}/m-pass"]


def test_a_schools_about_pages_competitions_and_old_posts_are_not_guidance():
    """On the guides page under 选课 on 2026-10-25: leadership and staff lists,
    rankings, competitions, 2005 study-trip posts, lab pages, CMS listings."""
    left_out = [
        "/business/about-us/leadership-team", "/business/about-us/prof-staff",
        "/business/about-us/wip-accreditation-and-ranking/ranking-qs",
        "/pharmacy/about-us/academic-staff", "/science/about-us-new/program-coordinators",
        "/IT/welcome/about-us", "/sass/about/vision-and-mission",
        "/engineering/enhanced-learning/external-design-competitions/the-freescale-cup",
        "/IT/monash-ai-challenge-cup-maicc/photo-gallery",
        "/engineering/all-disciplines/chemical-engineering/unwaste-2022",
        "/sass/student-experience/extra-curricular-activities/study-trips/2005-bangkok-thailand",
        "/engineering/analytical-services/civil-department",
        "/engineering/all-disciplines/mechanical-engineering/our-research_3/thermofluidics",
        "/science/listing", "/business/asset-listing", "/sass/site-map",
        "/science/home/itex-2018-winners", "/science/MScienceCup2026",
    ]
    assert urls(build([page(f"{MY}{path}", path) for path in left_out], {}, [])) == []
    kept = [
        "/jcsmhs/about/accreditation",
        "/sass/student-experience/extra-curricular-activities/study-trips",
        "/business/current/course-map-planning-guide",
        "/it/industry-partnerships/industry-scholarship",
    ]
    assert len(build([page(f"{MY}{path}", path) for path in kept], {}, [])) == len(kept)
    # Course map listings are content, not a CMS listing page.
    au = "/business/current-students/course-advice-and-planning/helpful-links/course-maps/" \
         "assets/2022/ug/asset-listing"
    assert len(build([page(f"https://www.monash.edu{au}", au)], {}, [])) == 1


def test_pages_checked_by_hand_on_2026_10_25():
    """A consent form and the fee calculator's forwarding page are left out;
    the exam pages Monash Malaysia closed even to signed-in students are gone;
    the calculator itself is listed as a link."""
    from crawler.official.seeds import SEEDS

    left_out = ["/release-form", "/talent-release-form/subscribe", "/finance/fees/fees-calculator"]
    assert urls(build([page(f"{MY}{path}", path) for path in left_out], {}, [])) == []

    by_slug = {seed.slug: seed for seed in SEEDS}
    exams = f"{MY}/student-services/student-admin/examinations-results"
    assert not [seed.slug for seed in SEEDS if seed.url.startswith(f"{exams}/") and any(
        name in seed.url for name in ("exam-rules", "device-and-system-set-up", "eexams-with",
                                      "preparing-for-your-exams", "remote-eexams",
                                      "troubleshooting-and-tips"))]
    assert "malaysia-special-consideration" not in by_slug
    calculator = by_slug["malaysia-fees-fees-calculator"]
    assert calculator.url.startswith("https://fin-feescalc.monash.edu.my/")
    assert calculator.sign_in and calculator.title == "Fee calculator (Monash Malaysia)"
    # The public eExam guide answers instead.
    assert "malaysia-our-services-online-assessment-eexams" in by_slug


def test_a_page_about_a_year_that_is_over_is_left_out():
    """Next to this year's on the guides page on 2026-10-25: old OSHC price
    lists, re-enrolment, discontinuation dates, intakes and events."""
    au = "https://www.monash.edu"
    left_out = [
        (f"{au}/students/admin/fees/other-costs/overseas-health-cover/2017-oshc-price-list",
         "2017 Monash OSHC price list"),
        (f"{au}/students/admin/fees/other-costs/overseas-health-cover/oshc-price-list",
         "2024 Monash OSHC price list"),
        (f"{au}/law/current-students/re-enrolment-year/2020-re-enrolment", "2020 Re-enrolment"),
        (f"{MY}/study/apply/intake-periods/july-2024-intake", "July 2024 intake"),
        (f"{MY}/student-services/student-admin/semester-principal-dates/principal-dates-2025",
         "Principal dates 2025"),
        (f"{au}/it/current-students/courses/maps/2019",
         "Course maps for students commenced in 2019"),
    ]
    pages = [{**page(url, url, title=title)} for url, title in left_out]
    assert urls(build(pages, {}, [], year=2026)) == []
    kept = [
        (f"{au}/students/admin/fees/other-costs/overseas-health-cover/2026-oshc-price-list",
         "2026 Monash OSHC price list"),
        # Students who started in 2021 can still be in a double degree.
        (f"{au}/it/current-students/courses/maps/2021",
         "Course maps for students commenced in 2021"),
        # The year a rule starts from, and course codes, are not dates.
        (f"{au}/law/honours-weighted-average/students-who-commenced-from-2014",
         "Students who commenced from 2014"),
        (f"{MY}/it/current-students/undergraduates/bachelor-of-computer-science-c2001",
         "Bachelor of Computer Science (C2001)"),
        (f"{MY}/study/S2000", "Bachelor of Science"),
    ]
    pages = [{**page(url, url, title=title)} for url, title in kept]
    assert len(build(pages, {}, [], year=2026)) == len(kept)
    # A listed row goes too, without being read again.
    previous = (("my-pd-2025", left_out[4][0], "Principal dates 2025", "fees-dates", (), "stable",
                 "malaysia"),)
    assert build([], {left_out[4][0]: {"text": "x" * 2000}}, [], {}, previous, year=2026) == []
