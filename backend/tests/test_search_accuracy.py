"""Search answering what students actually type, in either language.

The cases come from a list of about 200 real-looking queries run against a
copy of the live data. Each one here was wrong on the live site before this
file existed: Traditional or full-width input found nothing, "supp exam"
listed the eExam pages, "comp sci" found no degree, double degrees came first
for "computer science", and an admin question like "how to enroll" listed
hundreds of units whose overviews say "enrol". The rows below are made up,
small copies of the real titles.
"""
from __future__ import annotations

import pytest
from app.models.curriculum import Course
from app.models.handbook import Unit
from app.models.knowledge import OfficialPage, OfficialSource
from app.search import english, service
from app.search.chinese import concept_runs
from app.search.normalise import fold

# --- input folding ----------------------------------------------------------

@pytest.mark.parametrize(
    "typed,folded",
    [
        ("ＦＩＴ２１０２", "FIT2102"),        # full-width IME
        ("簽證續簽", "签证续签"),            # Traditional
        ("怎麼申請特殊考慮", "怎么申请特殊考虑"),
        ("  supp   exam ", "supp exam"),
        ("FIT2004 Algorithms", "FIT2004 Algorithms"),  # case is left alone
    ],
)
def test_fold(typed, folded):
    assert fold(typed) == folded


def test_traditional_reaches_the_same_concepts():
    assert concept_runs("學生簽證") == concept_runs("学生签证")


# --- English the way students write it ----------------------------------------

@pytest.mark.parametrize(
    "typed,monash",
    [
        ("supp exam", "supplementary assessment"),
        ("resit", "supplementary assessment"),
        ("how to drop a unit", "how to withdraw a unit"),
        ("comp sci", "computer science"),
        ("master of IT", "master of information technology"),
        ("honors", "honours"),
        ("RPL", "recognition of prior learning"),
        ("how to enroll", "how to enrol"),
    ],
)
def test_slang_is_rewritten(typed, monash):
    assert monash in english.variants(typed)


@pytest.mark.parametrize(
    "typed",
    [
        "how do I get it done before census",   # "it" is a pronoun here
        "dropbox",                              # "drop" only as a whole word
        "accounting",
        "mathematical",
    ],
)
def test_no_rewrite_inside_a_word_or_a_sentence(typed):
    phrases = [phrase for phrase, _ in english.phrase_runs(typed)]
    assert "it" not in phrases
    assert "drop" not in phrases
    assert "math" not in phrases


def test_the_query_as_typed_is_never_lost():
    """Variants are ORed with the query, never in place of it."""
    assert "supp exam" not in english.variants("supp exam")
    assert english.variants("census date") == []


# --- fixtures -----------------------------------------------------------------

def _unit(db, code, title, overview=""):
    db.add(Unit(
        unit_code=code, academic_year=2026, title=title, is_active=True,
        overview=overview, source_url=f"https://handbook.monash.edu/2026/units/{code}",
        content_hash=f"hash-{code}",
    ))


def _course(db, code, title, course_type="UG specialist", abbreviation=None):
    db.add(Course(
        course_code=code, academic_year=2026, title=title, is_active=True,
        course_type=course_type, abbreviated_name=abbreviation, campuses=["Clayton"],
        source_url=f"https://handbook.monash.edu/2026/courses/{code}",
        content_hash=f"hash-{code}",
    ))


def _pages(db, *rows):
    source = OfficialSource(key="monash-students", name="Monash", base_url="https://x.invalid")
    db.add(source)
    db.flush()
    for slug, title, summary in rows:
        db.add(OfficialPage(
            source_id=source.id, slug=slug, canonical_url=f"https://x.invalid/{slug}",
            title=title, summary=summary, category="general", status="ok", tags=[],
        ))
    db.commit()


def _unit_codes(db, query):
    found, _ = service.search_units(db, query, year=2026)
    return [unit.unit_code for unit in found]


def _course_codes(db, query):
    found, _ = service.search_courses(db, query, year=2026)
    return [course.course_code for course in found]


def _titles(db, query):
    found, _ = service.search_official(db, query, strong_only=True)
    return [page.title for page in found]


# --- units --------------------------------------------------------------------

def test_first_year_before_honours_and_research(db):
    """"psychology" led with three PSY4xxx honours units."""
    _unit(db, "PSY4111", "Psychology foundations: The individual")
    _unit(db, "MRU0022", "Postgraduate research in psychology")
    _unit(db, "PSY1011", "Foundations in psychology")
    db.commit()
    assert _unit_codes(db, "psychology") == ["PSY1011", "PSY4111", "MRU0022"]


def test_a_unit_called_it_beats_one_that_mentions_it(db):
    _unit(db, "FIT3163", "Data science project 1",
          overview="A project in data science. Data science teams, data science tools.")
    _unit(db, "FIT1043", "Introduction to data science")
    _unit(db, "FIT2004", "Algorithms and data structures",
          overview="Some data science background helps.")
    db.commit()
    assert _unit_codes(db, "data science")[:2] == ["FIT1043", "FIT3163"]


def test_a_stem_is_not_the_word(db):
    """"accounting" and "account" stem the same; the title has to say it."""
    _unit(db, "FIT9999", "IT account management")
    _unit(db, "ACC1100", "Accounting")
    db.commit()
    assert _unit_codes(db, "accounting")[0] == "ACC1100"


@pytest.mark.parametrize("query", ["how to enroll", "学费", "census date", "毕业"])
def test_an_admin_question_lists_no_units(db, query):
    _unit(db, "EDF5001", "Enrolment and fees in schools",
          overview="Enrol, fees, census date, graduation. All of it.")
    db.commit()
    assert _unit_codes(db, query) == []


@pytest.mark.parametrize("query", ["ＦＩＴ２００４", "演算法"])
def test_full_width_and_traditional_reach_units(db, query):
    _unit(db, "FIT2004", "Algorithms and data structures")
    db.commit()
    assert _unit_codes(db, query) == ["FIT2004"]


# --- degrees ------------------------------------------------------------------

def _degrees(db):
    _course(db, "B2025", "Bachelor of Business and Bachelor of Computer Science", "UG double")
    _course(db, "C6007", "Graduate Certificate of Computer Science", "PG Grad Cert / Grad Dip")
    _course(db, "C2001", "Bachelor of Computer Science", abbreviation="BCompSci")
    _course(db, "C3701", "Bachelor of Computer Science (Honours)", "UG honours")
    _course(db, "B2001", "Bachelor of Commerce", abbreviation="BCom")
    _course(db, "C6001", "Master of Information Technology", "PG Masters")
    _course(db, "A6001", "Master of Architecture", "PG Masters")
    _course(db, "B6001", "Master of Business Analytics", "PG Masters")
    _course(db, "B6005", "Master of Business Administration", "PG Masters")
    db.commit()


@pytest.mark.parametrize("query", ["computer science", "comp sci", "CS degree", "计算机科学"])
def test_the_single_bachelor_comes_first(db, query):
    _degrees(db)
    assert _course_codes(db, query)[0] == "C2001"


@pytest.mark.parametrize(
    "query,first",
    [
        ("master of IT", "C6001"),
        ("MBA", "B6005"),
        ("bcom", "B2001"),
    ],
)
def test_abbreviations_find_the_degree(db, query, first):
    _degrees(db)
    codes = _course_codes(db, query)
    assert codes[0] == first
    assert "A6001" not in codes  # "it" is not inside "Architecture"


@pytest.mark.parametrize("query,expected", [("double degree", "B2025"), ("honors", "C3701")])
def test_a_kind_of_degree_is_a_search(db, query, expected):
    """These two returned nothing: they read as a level, and a level alone is
    not a search."""
    _degrees(db)
    assert expected in _course_codes(db, query)


def test_a_level_alone_is_not_a_search(db):
    _degrees(db)
    assert _course_codes(db, "apply to graduate") == []


# --- official pages -------------------------------------------------------------

@pytest.mark.parametrize("query", ["毕业", "graduation", "畢業"])
def test_graduations(db, query):
    _pages(
        db,
        ("graduate-research", "Graduate research degrees", "Doing a PhD after you graduate."),
        ("graduations", "Graduations", "Graduation ceremonies and applying to graduate."),
    )
    assert _titles(db, query)[0] == "Graduations"


@pytest.mark.parametrize("query", ["supp exam", "resit", "补考"])
def test_supplementary_assessment_beats_the_exam_pages(db, query):
    _pages(
        db,
        ("eexams", "eExams", "Your exam is an eExam. Exam rules for every exam."),
        ("supplementary", "Supplementary assessments", "If you are offered a supp."),
    )
    assert _titles(db, query)[0] == "Supplementary assessments"


def test_whole_words_as_typed_before_prefixes(db):
    """"pay" is only the start of "payment" in the non-payment page."""
    _pages(
        db,
        ("non-payment", "Fees non-payment (encumbrance)", "What happens if you do not pay."),
        ("pay-your-fees", "Pay your fees", "How to pay your fees."),
    )
    assert _titles(db, "how to pay fees")[0] == "Pay your fees"


def test_visa_renewal_is_not_every_visa_page(db):
    _pages(
        db,
        ("visa", "Your student visa", "Conditions of your student visa."),
        ("extending", "Extending your stay (student visas)", "Renew or extend your visa."),
    )
    assert _titles(db, "學生簽證續簽")[0] == "Extending your stay (student visas)"


def test_a_subject_is_not_answered_by_an_admin_page(db):
    """毕业设计 is a final year project, not a graduation page."""
    _pages(db, ("graduations", "Graduations", "Graduation ceremonies."))
    assert _titles(db, "毕业设计") == []
