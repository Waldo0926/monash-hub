"""The question router against the real seed data, in both languages.

Every official page the crawler indexes and every curated FAQ is loaded here
exactly as a deploy loads them, then asked the questions that went wrong on the
live site. The page bodies are not loaded - they are Monash's text, not ours -
so what these tests pin down is routing on titles, tags and the curated FAQ,
which is where every one of those wrong answers came from.
"""
from __future__ import annotations

from datetime import UTC, datetime

import pytest
from app.handbook.parser import parse_unit_page, unit_url
from app.handbook.repository import upsert_unit
from app.knowledge.faq_seed import FAQ_SEEDS
from app.knowledge.repository import get_or_create_source, upsert_seed_page
from app.knowledge.translations_seed import TRANSLATION_SEEDS
from app.models.community import CommunityPost
from app.models.curriculum import Course
from app.models.knowledge import FaqEntry
from app.models.translation import HUMAN, PUBLISHED, ContentTranslation
from app.models.user import User
from crawler.official.seeds import SEEDS


@pytest.fixture
def seeded(db, handbook_html):
    source = get_or_create_source(db, "monash", "Monash University", "https://www.monash.edu")
    pages = {}
    for seed in SEEDS:
        page = upsert_seed_page(
            db, source=source, slug=seed.slug, url=seed.url, title=seed.title,
            category=seed.category, tags=list(seed.tags), refresh_tier=seed.tier,
            applies_to=seed.applies_to,
        )
        page.status = "ok"
        page.content_hash = f"hash-{seed.slug}"
        page.last_checked = datetime.now(UTC)
        pages[seed.slug] = page
    for item in FAQ_SEEDS:
        page = pages.get(item.page_slug)
        db.add(FaqEntry(
            slug=item.slug, question=item.question, answer=item.answer,
            category=item.category, tags=list(item.tags), keywords=list(item.keywords),
            priority=item.priority, official_page_id=page.id if page else None,
            official_url=page.canonical_url if page else None,
        ))
    for item in TRANSLATION_SEEDS:
        if item.target_type not in ("faq_entry", "official_page") \
                or item.field not in ("question", "answer", "title"):
            continue
        db.add(ContentTranslation(
            locale=item.locale, target_type=item.target_type, target_key=item.target_key,
            field=item.field, text=item.text,
            data={"strings": item.strings} if item.strings else None,
            status=PUBLISHED, provenance=HUMAN, translator=item.translator,
        ))
    upsert_unit(db, parse_unit_page(handbook_html("FIT2102"), unit_url("FIT2102", 2026)))
    db.commit()
    return db


def ask(client, query: str, locale: str = "en") -> dict:
    response = client.post(f"/api/v1/ask?locale={locale}", json={"query": query})
    assert response.status_code == 200
    return response.json()


def page_slugs(body: dict) -> list[str]:
    return [item["slug"] for block in body["blocks"] if block["type"] == "page_list"
            for item in block["items"]]


# --- the reported bug and its family -----------------------------------------

@pytest.mark.parametrize("locale", ["en", "zh"])
@pytest.mark.parametrize("query", ["学生签证续签", "student visa renewal", "签证延期", "怎么续签"])
def test_renewing_a_visa_is_answered_with_visa_pages(client, seeded, query, locale):
    body = ask(client, query, locale)
    assert body["answer_type"] == "official_search"
    slugs = page_slugs(body)
    assert "student-visa" in slugs
    assert "add-or-withdraw-units" not in slugs
    assert "special-consideration" not in slugs


@pytest.mark.parametrize(
    "query,slug",
    [
        ("学术诚信", "academic-integrity"),
        ("抄袭", "academic-integrity"),
        ("plagiarism", "academic-integrity"),
        ("被劝退", "academic-progress"),
        ("医保", "oshc"),
        ("学费", "fees"),
        ("转专业", "changing-your-enrolment"),
        ("学分转换", "credit-and-enrolment"),
    ],
)
def test_a_topic_reaches_its_official_page_in_either_language(client, seeded, query, slug):
    body = ask(client, query, "zh")
    assert body["answer_type"] == "official_search"
    assert page_slugs(body)[0] == slug


@pytest.mark.parametrize(
    "query,slug",
    [
        ("成绩单", "how-to-get-a-transcript"),
        ("休学", "apply-for-intermission"),
        ("延期考试", "defer-a-final-assessment"),
        ("怎么申请 SC", "how-to-apply-special-consideration"),
        ("how do I withdraw from a unit", "how-to-withdraw-from-a-unit"),
    ],
)
def test_a_covered_question_gets_its_curated_answer(client, seeded, query, slug):
    body = ask(client, query)
    assert body["answer_type"] == "official_faq"
    assert body["faq_slug"] == slug


@pytest.mark.parametrize("query", ["scholarship", "奖学金", "accounting", "会计", "图书馆"])
def test_no_curated_or_official_answer_is_invented(client, seeded, query):
    """Nothing indexed is about these. The card says so rather than listing
    pages that happen to use the word ("your Monash account")."""
    body = ask(client, query)
    assert body["answer_type"] == "community_fallback"


# --- language ------------------------------------------------------------------

def test_the_faq_answer_is_in_the_readers_language(client, seeded):
    body = ask(client, "我想退课", "zh")
    assert body["answer_type"] == "official_faq"
    assert body["title"] == "怎么退选一门课？"
    assert "WES" in body["blocks"][0]["text"] and "退选" in body["blocks"][0]["text"]
    assert body["translation"]["unofficial"] is True
    assert body["caveat_key"] == "answer.caveat.official"

    english = ask(client, "我想退课", "en")
    assert english["title"] == "How do I withdraw from a unit?"
    assert english["translation"] is None


def test_related_questions_are_offered_in_the_readers_language(client, seeded):
    body = ask(client, "退课会影响签证吗", "zh")
    assert body["answer_type"] != "official_faq"
    assert "怎么退选一门课？" in body["suggestions"]


def test_every_sentence_of_ours_carries_a_translation_key(client, seeded):
    for query in ("FIT2102 exam", "FIT2102 prerequisites", "FIT2102 malaysia",
                  "FIT2102 workload", "FIT2102 learning outcomes", "FIT2102 难不难"):
        body = ask(client, query, "zh")
        assert body["title_key"].startswith("answer."), query
        for block in body["blocks"]:
            if block["type"] == "verdict":
                assert block["key"].startswith("answer."), (query, block)
            if block["type"] == "table":
                assert len(block["column_keys"]) == len(block["columns"])


@pytest.mark.parametrize("locale", ["en", "zh", "ja", "ko"])
def test_unit_suggestions_follow_the_language_and_still_route(client, seeded, locale):
    body = ask(client, "FIT2102", locale)
    for suggestion in body["suggestions"]:
        follow = ask(client, suggestion, locale)
        assert follow["answer_type"].startswith("handbook_"), suggestion
        assert follow["answer_type"] != "handbook_overview", suggestion


@pytest.mark.parametrize(
    "question,answer_type",
    [
        # The unit page's own chips, in every interface language.
        ("FIT2102 に期末試験はありますか？", "handbook_assessment"),
        ("FIT2102 の履修条件は何ですか？", "handbook_requisite"),
        ("FIT2102 はマレーシアで開講されますか？", "handbook_offering"),
        ("FIT2102에 기말시험이 있나요?", "handbook_assessment"),
        ("FIT2102의 선수과목은 무엇인가요?", "handbook_requisite"),
        ("FIT2102는 말레이시아에서 개설되나요?", "handbook_offering"),
    ],
)
def test_japanese_and_korean_questions_route(client, seeded, question, answer_type):
    assert ask(client, question)["answer_type"] == answer_type


# --- unit codes ------------------------------------------------------------------

def test_a_unit_named_in_a_policy_question_does_not_hide_the_policy(client, seeded):
    body = ask(client, "FIT2102 怎么退课", "zh")
    assert body["answer_type"] == "official_faq"
    assert body["faq_slug"] == "how-to-withdraw-from-a-unit"
    assert {"type": "link", "to": "/units/FIT2102", "label": "FIT2102"} in body["blocks"]


def test_a_code_that_does_not_exist_says_so(client, seeded):
    body = ask(client, "FIT9999 有考试吗")
    assert body["answer_type"] == "unit_not_found"
    assert body["title_params"]["code"] == "FIT9999"


def test_a_year_is_not_a_unit_code(client, seeded):
    assert ask(client, "year 2026 fees")["answer_type"] != "unit_not_found"


def test_the_handbook_year_is_the_units_year(client, seeded):
    body = ask(client, "does FIT2102 have an exam")
    assert body["blocks"][0]["params"]["year"] == 2026
    assert "2026 Handbook" in body["blocks"][0]["text"]


# --- search beyond the answer card ---------------------------------------------

def test_a_chinese_degree_search_finds_the_english_title(client, seeded):
    seeded.add(Course(course_code="B2001", academic_year=2026, title="Bachelor of Commerce",
                      is_active=True, campuses=["Clayton"],
                      source_url="https://handbook.monash.edu/2026/courses/B2001",
                      content_hash="b"))
    seeded.add(Course(course_code="C2001", academic_year=2026,
                      title="Bachelor of Computer Science", is_active=True, campuses=["Clayton"],
                      source_url="https://handbook.monash.edu/2026/courses/C2001",
                      content_hash="c"))
    seeded.commit()
    body = client.get("/api/v1/search", params={"q": "商科学士"}).json()
    degrees = next(g for g in body["groups"] if g["kind"] == "degrees")
    assert [c["course_code"] for c in degrees["results"]] == ["B2001"]


def test_community_search_crosses_languages(client, seeded):
    user = User(email="a@example.com", nickname="a", password_hash="x")
    seeded.add(user)
    seeded.flush()
    seeded.add(CommunityPost(author_id=user.id, title="退课之后学费还要交吗",
                             body="过了截止日期再退课会怎样", category="enrolment"))
    seeded.add(CommunityPost(author_id=user.id, title="How do I withdraw?",
                             body="Asking for a friend", category="enrolment"))
    seeded.commit()

    def titles(q):
        body = client.get("/api/v1/search", params={"q": q}).json()
        return {p["title"] for p in next(g for g in body["groups"]
                                         if g["kind"] == "community")["results"]}

    assert titles("withdraw") == {"退课之后学费还要交吗", "How do I withdraw?"}
    assert titles("退课") == {"退课之后学费还要交吗", "How do I withdraw?"}
    assert "退课之后学费还要交吗" in titles("退课截止日期")


def test_like_wildcards_in_a_query_are_literal(client, seeded):
    body = client.get("/api/v1/units", params={"q": "%"}).json()
    assert body["total"] == 0
    body = client.get("/api/v1/units", params={"q": "_IT2102"}).json()
    assert body["total"] == 0


def test_the_faq_group_lists_only_triggered_entries(client, seeded):
    body = client.get("/api/v1/search", params={"q": "学生签证续签"}).json()
    faq = next(g for g in body["groups"] if g["kind"] == "faq")
    assert "how-to-withdraw-from-a-unit" not in [f["slug"] for f in faq["results"]]
