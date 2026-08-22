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


def test_official_search_finds_the_seed_page(client, loaded):
    body = client.get("/api/v1/official/search", params={"q": "special consideration"}).json()
    assert body["total"] >= 1
    assert body["results"][0]["slug"] == "special-consideration"
    assert body["results"][0]["last_checked"] is not None


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


def _account(client, email: str, nickname: str) -> str:
    response = client.post(
        "/api/v1/auth/signup",
        json={"email": email, "nickname": nickname, "password": "correct-horse-battery"},
    )
    assert response.status_code == 201
    return response.json()["token"]


def test_community_post_answer_and_search(client, loaded):
    asker = _account(client, "asker@example.com", "asker")
    helper = _account(client, "helper@example.com", "helper")

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


def test_reports_can_be_filed_and_only_admins_can_read_them(client, loaded):
    filed = client.post(
        "/api/v1/community/reports",
        json={"target_type": "post", "target_id": 1, "reason": "spam"},
    )
    assert filed.status_code == 201

    token = _account(client, "nosy@example.com", "nosy")
    assert client.get(
        "/api/v1/community/reports", headers={"Authorization": f"Bearer {token}"}
    ).status_code == 403
