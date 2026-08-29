"""End-to-end checks against a real PostgreSQL.

These cover the paths the MVP acceptance list names: a unit page with its
source, an official search that hits the right seed page, the zero-AI answers,
and a community post that a second account can answer and search for.
"""
from __future__ import annotations

import pytest
from app.handbook.parser import parse_unit_page, unit_url
from app.handbook.repository import upsert_unit
from app.knowledge.cleaner import clean_page
from app.knowledge.repository import get_or_create_source, record_fetch, upsert_seed_page
from app.models.handbook import Unit, UnitOffering
from app.models.knowledge import FaqEntry


@pytest.fixture
def loaded(db, handbook_html, official_html):
    """One unit, one official page and one FAQ entry - enough to exercise search."""
    for code in ("FIT2102", "BFF2140"):
        upsert_unit(db, parse_unit_page(handbook_html(code), unit_url(code, 2026)))

    source = get_or_create_source(db, "monash-students", "Monash University",
                                  "https://www.monash.edu")
    page = upsert_seed_page(
        db,
        source=source,
        slug="special-consideration",
        url="https://www.monash.edu/students/admin/assessments/sc",
        title="Extensions and special consideration",
        category="assessment",
        tags=["special consideration", "sc"],
        refresh_tier="medium",
    )
    record_fetch(db, page, clean_page(official_html("sample-guide"), url=page.canonical_url))

    db.add(
        FaqEntry(
            slug="how-to-apply-sc",
            question="How do I apply for special consideration?",
            answer="Apply through the online form within two working days.",
            category="assessment",
            tags=["sc"],
            keywords=["sc", "special consideration"],
            official_page_id=page.id,
            official_url=page.canonical_url,
            priority=100,
        )
    )
    db.commit()
    return db


def test_health_reports_data_counts(client, loaded):
    body = client.get("/api/health").json()
    assert body["status"] == "ok"
    assert body["data"]["units"] == 2
    assert body["data"]["official_pages_ok"] == 1


def test_unit_detail_carries_source_and_structure(client, loaded):
    body = client.get("/api/v1/units/FIT2102").json()
    assert body["title"] == "Programming paradigms"
    assert body["has_exam"] is False
    assert len(body["assessments"]) == 4
    assert body["source_url"].endswith("/2026/units/FIT2102")
    assert body["last_checked"] is not None
    assert {o["campus"] for o in body["offerings"]} == {"Clayton", "Malaysia"}


def test_unknown_unit_is_a_404_not_an_empty_page(client, loaded):
    assert client.get("/api/v1/units/ZZZ9999").status_code == 404


def test_unit_search_by_code_and_keyword(client, loaded):
    by_code = client.get("/api/v1/units", params={"q": "FIT2102"}).json()
    assert by_code["results"][0]["unit_code"] == "FIT2102"

    by_word = client.get("/api/v1/units", params={"q": "finance"}).json()
    assert "BFF2140" in {r["unit_code"] for r in by_word["results"]}


def test_unit_filter_by_exam(client, loaded):
    body = client.get("/api/v1/units", params={"has_exam": "false"}).json()
    codes = {r["unit_code"] for r in body["results"]}
    assert "FIT2102" in codes and "BFF2140" not in codes


def test_unit_filter_by_campus(client, loaded):
    body = client.get("/api/v1/units", params={"campus": "Malaysia"}).json()
    assert "FIT2102" in {r["unit_code"] for r in body["results"]}


def test_campus_and_teaching_period_must_be_the_same_offering(client, db):
    """A unit taught at two campuses is not taught in every combination of them.

    BPS3062 runs at Malaysia over the full year *extended* and at Parkville over
    the full year, and answered a search for "Malaysia, full year" - a
    combination it is not offered in anywhere. Asked as two separate EXISTS
    clauses, any pair of offerings could satisfy the pair of filters.
    """
    unit = Unit(
        unit_code="BPS3062",
        title="Professional experience",
        academic_year=2026,
        source_url="https://handbook.monash.edu/2026/units/BPS3062",
        content_hash="bps3062-test",
        is_active=True,
        offerings=[
            UnitOffering(campus="Malaysia", teaching_period="Full year extended"),
            UnitOffering(campus="Parkville", teaching_period="Full year"),
        ],
    )
    db.add(unit)
    db.commit()

    both = client.get(
        "/api/v1/units",
        params={"campus": "Malaysia", "teaching_period": "Full year"},
    ).json()
    assert both["total"] == 0

    # Each filter on its own still finds it, and so does the pair it does run in.
    for params in (
        {"campus": "Malaysia"},
        {"teaching_period": "Full year"},
        {"campus": "Malaysia", "teaching_period": "Full year extended"},
    ):
        body = client.get("/api/v1/units", params=params).json()
        assert "BPS3062" in {r["unit_code"] for r in body["results"]}, params


def test_official_search_finds_the_seed_page(client, loaded):
    body = client.get("/api/v1/official/search", params={"q": "special consideration"}).json()
    assert body["total"] >= 1
    assert body["results"][0]["slug"] == "special-consideration"
    assert body["results"][0]["last_checked"] is not None


def test_guides_paginate(client, loaded):
    # The sitemap walks this endpoint a page at a time, so offset has to work.
    first = client.get("/api/v1/guides", params={"limit": 1, "offset": 0}).json()
    second = client.get("/api/v1/guides", params={"limit": 1, "offset": 1}).json()
    assert first["total"] == second["total"]
    assert first["offset"] == 0 and second["offset"] == 1
    assert len(first["results"]) == 1
    assert not second["results"], "only one page is indexed in this fixture"


def test_unified_search_groups_results_by_source(client, loaded):
    body = client.get("/api/v1/search", params={"q": "special consideration"}).json()
    kinds = {g["kind"]: g for g in body["groups"]}
    assert set(kinds) == {"handbook", "official", "faq", "community"}
    assert kinds["official"]["total"] >= 1
    assert kinds["official"]["badge"] != kinds["community"]["badge"]


def test_ask_assessment_question(client, loaded):
    body = client.post("/api/v1/ask", json={"query": "FIT2102 有没有考试？"}).json()
    assert body["answer_type"] == "handbook_assessment"
    assert body["unit_code"] == "FIT2102"
    assert "does not list a final examination" in body["blocks"][0]["text"]
    assert body["sources"][0]["url"].endswith("/2026/units/FIT2102")


def test_ask_requisite_question(client, loaded):
    body = client.post("/api/v1/ask", json={"query": "prerequisites for FIT2102"}).json()
    assert body["answer_type"] == "handbook_requisite"
    group = next(b for b in body["blocks"] if b["type"] == "requisite_group")
    assert group["requisite_type"] == "prerequisite"


def test_ask_offering_question_answers_the_campus_asked_about(client, loaded):
    body = client.post("/api/v1/ask", json={"query": "FIT2102 马来西亚开吗"}).json()
    assert body["answer_type"] == "handbook_offering"
    assert "Malaysia" in body["blocks"][0]["text"]


def test_ask_subjective_question_does_not_invent_a_verdict(client, loaded):
    body = client.post("/api/v1/ask", json={"query": "FIT2102 难不难"}).json()
    assert body["answer_type"] == "subjective"
    assert "matter of opinion" in body["blocks"][0]["text"]


def test_ask_policy_question_returns_the_curated_answer(client, loaded):
    body = client.post("/api/v1/ask", json={"query": "怎么申请 SC"}).json()
    assert body["answer_type"] == "official_faq"
    assert body["sources"][0]["url"].endswith("/assessments/sc")


def test_curated_keywords_do_not_fire_inside_longer_words(client, loaded):
    # The FAQ carries "sc" as a keyword because students type it. It must not
    # match "scooter", "science" or "schedule".
    body = client.post("/api/v1/ask", json={"query": "is there a science building map"}).json()
    assert body["answer_type"] != "official_faq"


def test_ask_unknown_question_falls_back_to_community(client, loaded):
    body = client.post("/api/v1/ask", json={"query": "where can I park a scooter"}).json()
    assert body["answer_type"] == "community_fallback"
    assert body["fallback"]["ask_community"] is True


PASSWORD = "Correct-Horse-9"


def _account(client, mailbox, email: str, nickname: str) -> str:
    """Register through the real flow: request a code, read it, then sign up."""
    sent = client.post(
        "/api/v1/auth/verification-code",
        json={"email": email, "purpose": "registration"},
    )
    assert sent.status_code == 200
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": email,
            "nickname": nickname,
            "password": PASSWORD,
            "verification_code": mailbox.code_for(email),
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["token"]


def test_community_post_answer_and_search(client, loaded, mailbox):
    asker = _account(client, mailbox, "asker@example.com", "asker")
    helper = _account(client, mailbox, "helper@example.com", "helper")

    created = client.post(
        "/api/v1/community/posts",
        json={
            "title": "FIT2102 workload in semester 2",
            "body": "How many hours a week did this actually take you?",
            "category": "units",
            "unit_code": "FIT2102",
            "tags": ["workload"],
        },
        headers={"Authorization": f"Bearer {asker}"},
    )
    assert created.status_code == 201
    post_id = created.json()["id"]

    answered = client.post(
        f"/api/v1/community/posts/{post_id}/answers",
        json={"body": "About twelve hours a week including the applied sessions."},
        headers={"Authorization": f"Bearer {helper}"},
    )
    assert answered.status_code == 201

    found = client.get("/api/v1/community/posts", params={"q": "workload"}).json()
    assert post_id in {p["id"] for p in found["results"]}

    detail = client.get(f"/api/v1/community/posts/{post_id}").json()
    assert detail["answer_count"] == 1
    assert detail["answers"][0]["author"] == "helper"


def test_posting_requires_an_account(client, loaded):
    response = client.post(
        "/api/v1/community/posts",
        json={"title": "A question about units", "body": "Body text here", "category": "units"},
    )
    assert response.status_code == 401


def test_anonymous_can_read_everything_public(client, loaded):
    assert client.get("/api/v1/community/posts").status_code == 200
    assert client.get("/api/v1/units").status_code == 200
    assert client.get("/api/v1/guides").status_code == 200


def test_reports_can_be_filed_and_only_admins_can_read_them(client, loaded, mailbox):
    filed = client.post(
        "/api/v1/community/reports",
        json={"target_type": "post", "target_id": 1, "reason": "spam"},
    )
    assert filed.status_code == 201

    token = _account(client, mailbox, "nosy@example.com", "nosy")
    assert client.get(
        "/api/v1/community/reports", headers={"Authorization": f"Bearer {token}"}
    ).status_code == 403


def test_a_requisite_name_is_translated_as_the_handbook_wrote_it(client, db, handbook_html):
    """FIT2102 lists FIT1008 as a prohibition, calling it what it was called then.

    The Handbook's requisite records are snapshots: this one names FIT1008
    "Introduction to computer science", the 2019 title, while FIT1008's own 2026
    page says "Fundamentals of algorithms". We translate the sentence the
    Handbook wrote. Substituting today's title would be putting words in its
    mouth.
    """
    from app.models.translation import MACHINE, PUBLISHED, UNIT, ContentTranslation

    for code in ("FIT2102", "FIT1008"):
        upsert_unit(db, parse_unit_page(handbook_html(code), unit_url(code, 2026)))
    db.add(
        ContentTranslation(
            locale="zh", target_type=UNIT, target_key="FIT2102", field="content",
            provenance=MACHINE, status=PUBLISHED,
            data={"strings": {"Introduction to computer science": "计算机科学导论"}},
        )
    )
    db.commit()

    body = client.get("/api/v1/units/FIT2102", params={"locale": "zh"}).json()
    names = {
        item["code"]: item["name"]
        for group in body["requisites"]
        for item in group["items"]
    }
    assert names["FIT1008"] == "计算机科学导论"


def test_an_untranslated_requisite_keeps_its_english_name(client, db, handbook_html):
    for code in ("FIT2102", "FIT1008"):
        upsert_unit(db, parse_unit_page(handbook_html(code), unit_url(code, 2026)))
    db.commit()

    body = client.get("/api/v1/units/FIT2102", params={"locale": "zh"}).json()
    names = {
        item["code"]: item["name"]
        for group in body["requisites"]
        for item in group["items"]
    }
    assert names["FIT1008"] == "Introduction to computer science"


def test_a_guide_says_which_campus_it_is_for(client, db):
    """An Australian page shown to a Malaysian reader is the wrong country's law.

    A student pass in Malaysia is issued by the Immigration Department through
    EMGS and is not the Australian subclass 500 visa; the work rights on the
    monash.edu pages do not carry over. So the campus travels with the page,
    onto the card as well as into the detail.
    """
    source = get_or_create_source(db, "monash-my", "Monash Malaysia",
                                  "https://www.monash.edu.my")
    page = upsert_seed_page(
        db,
        source=source,
        slug="malaysia-student-pass",
        url="https://www.monash.edu.my/student-services/international-students/student-pass",
        title="Student pass (Monash Malaysia)",
        category="malaysia",
        tags=["malaysia"],
        refresh_tier="stable",
        applies_to="malaysia",
    )
    record_fetch(db, page, clean_page("<h1>Student pass</h1><p>EMGS.</p>",
                                      url=page.canonical_url))
    db.commit()

    detail = client.get("/api/v1/guides/malaysia-student-pass").json()
    assert detail["applies_to"] == "malaysia"
    listing = client.get("/api/v1/guides").json()
    row = next(g for g in listing["results"] if g["slug"] == "malaysia-student-pass")
    assert row["applies_to"] == "malaysia"


def test_a_page_with_no_campus_stated_is_treated_as_australian():
    """39 of the 40 pages in the seed list are on monash.edu, so that is the
    safe default: a page that arrives without a campus is far likelier to be
    another Australian one than a Malaysian one."""
    from crawler.official.seeds import SEEDS

    assert {s.applies_to for s in SEEDS} <= {"australia", "malaysia", "all"}
    for seed in SEEDS:
        host = "malaysia" if "monash.edu.my" in seed.url else "australia"
        # "all" is only ever claimed by a page that says so in its own text.
        assert seed.applies_to in (host, "all"), seed.slug


def test_a_unit_is_found_by_part_of_its_code(client, loaded):
    """A student who half-remembers a code types the half they remember.

    "5215" is FIT5215 to them. Matching only from the start of the code answered
    "no official answer indexed for this yet" for a unit that is indexed.
    """
    body = client.get("/api/v1/units", params={"q": "2102"}).json()
    assert "FIT2102" in {r["unit_code"] for r in body["results"]}

    # The whole-site search reads the same function, so it agrees.
    search = client.get("/api/v1/search", params={"q": "2102"}).json()
    units = next(g for g in search["groups"] if g["kind"] == "handbook")
    assert "FIT2102" in {r["unit_code"] for r in units["results"]}


def test_a_code_match_outranks_a_title_that_merely_resembles_it(client, loaded):
    body = client.get("/api/v1/units", params={"q": "FIT"}).json()
    assert body["results"][0]["unit_code"].startswith("FIT")


def test_a_sentence_is_not_treated_as_a_code_fragment(client, loaded):
    """Only a short run of letters and digits is a code; a phrase is not."""
    body = client.get("/api/v1/units", params={"q": "programming paradigms"}).json()
    assert "FIT2102" in {r["unit_code"] for r in body["results"]}


def test_a_bare_unit_code_answers_with_the_way_in(client, loaded):
    """Typing a code is asking for the unit, not for an essay about it.

    This used to answer with the whole overview, which on a phone is the entire
    first screen - so a reader searching FIT2102 met a wall of prose and never
    scrolled to the unit itself. A table of facts was tried next and filled the
    screen too.
    """
    body = client.post("/api/v1/ask", json={"query": "FIT2102"}).json()
    assert [b["type"] for b in body["blocks"]] == ["link"]
    assert body["blocks"][0]["to"] == "/units/FIT2102"


def test_the_answer_title_is_in_the_readers_language(client, loaded, db):
    """It is the whole visible answer when somebody types a unit code."""
    from app.models.handbook import Unit
    from app.models.translation import HUMAN, PUBLISHED, UNIT, ContentTranslation

    unit = db.query(Unit).filter_by(unit_code="FIT2102").one()
    db.add(
        ContentTranslation(
            locale="zh", target_type=UNIT, target_key="FIT2102", field="content",
            data={"strings": {unit.title: "编程范式"}},
            source_hash=unit.content_hash, status=PUBLISHED, provenance=HUMAN,
        )
    )
    db.commit()

    body = client.post(
        "/api/v1/ask", json={"query": "FIT2102"}, params={"locale": "zh"}
    ).json()
    assert body["title"] == "FIT2102 · 编程范式"
