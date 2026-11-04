"""Synthetic source joins: preserve identity without inferring admissions from fees."""

from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from app.knowledge import admissions as a
from app.knowledge import cleaner, tuition
from app.knowledge.programme_sources import programme_url

BASE = "https://www.monash.edu.my/study/postgraduate-and-research/"
ARTS = BASE + "arts-social-sciences/phd"
BUSINESS = BASE + "business/phd"
TITLE = "Doctor of Philosophy"
NOW = datetime.now(UTC)


def page(url, text, **changes):
    return SimpleNamespace(
        **(
            {
                "id": 1 if url == ARTS else 2,
                "source_title": TITLE,
                "canonical_url": url,
                "title": TITLE,
                "clean_text": text,
                "status": "ok",
                "fetch_error": None,
                "requires_sign_in": False,
                "last_checked": NOW,
                "content_hash": "synthetic",
                "blocks": [
                    {
                        "type": "paragraph",
                        "spans": [
                            {
                                "text": "Handbook",
                                "url": "https://handbook.monash.edu/2027/courses/A6001",
                            }
                        ],
                    }
                ],
            }
            | changes
        )
    )


def evaluate(title, record, **kwargs):
    return a.evidence(title, record, source_title=getattr(record, "source_title", None), **kwargs)


def database(pages):
    return SimpleNamespace(
        scalars=lambda _: SimpleNamespace(all=lambda: pages),
        execute=lambda _: SimpleNamespace(all=lambda: [(p.id, p.source_title) for p in pages]),
    )


def blocks():
    result = cleaner.clean_page(
        """<main><h1>Fees</h1><p>2027 tuition fees</p>
    <h2>School of Arts and Social Sciences</h2><table>
    <tr><th>Course</th><th>Duration (years)</th><th>Malaysian</th><th>International</th></tr>
    <tr><td><a href="/study/postgraduate-and-research/arts-social-sciences/phd">Doctor of Philosophy (PhD)</a></td><td>3</td><td>100 (per year)</td><td>200 (per year)</td></tr></table>
    <h2>School of Business</h2><table><thead>
    <tr><th>Course</th><th>Duration (years)</th><th>Malaysian</th><th>International</th></tr></thead>
    <tbody><tr><td><a href="/study/postgraduate-and-research/business/phd">Doctor of Philosophy</a></td><td>3</td><td>300 (per year)</td><td>400 (per year)</td></tr></tbody></table></main>""",
        url="https://www.monash.edu.my/study/postgraduate-and-research/fees",
    )
    return result["blocks"]


def test_fee_cell_links_retain_anchor_identity_and_school_specific_urls():
    rows = tuition.parse_blocks(blocks(), "malaysia-pgfees")
    assert [row.school for row in rows] == ["arts", "business"]
    assert [tuition._row(row)["programme_url"] for row in rows] == [ARTS, BUSINESS]
    assert [row.domestic[0].value for row in rows] == [100, 300]


def test_rowspan_links_stay_at_their_actual_cell_positions():
    result = cleaner.clean_page(
        """<main><h1>Example</h1><table><thead><tr><th>Year</th><th>Course</th></tr></thead>
    <tbody><tr><td rowspan="2">2027</td><td><a href="/one">One</a></td></tr>
    <tr><td><a href="/two">Two</a></td></tr></tbody></table></main>""",
        url="https://www.monash.edu.my/",
    )
    table = next(b for b in result["blocks"] if b["type"] == "table")
    assert [(x["row"], x["column"], x["text"], x["url"]) for x in table["cell_links"]] == [
        (0, 1, "One", "https://www.monash.edu.my/one"),
        (1, 1, "Two", "https://www.monash.edu.my/two"),
    ]
    assert table["links"]  # Existing Policy Bank link index is retained.


def test_same_title_in_two_schools_cannot_share_an_application_notice():
    rows = [tuition._row(row) for row in tuition.parse_blocks(blocks(), "malaysia-pgfees")]
    pages = [
        page(ARTS, f"Applications for the {TITLE} are closed."),
        page(BUSINESS, "Apply now. February 2027 deadline."),
    ]
    db = database(pages)
    coverage = a.for_rows(db, rows)
    assert [row["admissions"]["status"] for row in rows] == ["closed", "not_verified"]
    assert coverage == {
        "rows": 2,
        "linked_programme_rows": 2,
        "verified_programme_rows": 2,
        "explicit_notice_rows": 1,
        "conflict_rows": 0,
    }
    assert all(row["admissions"]["intake_status"] == "not_verified" for row in rows)


def test_wrong_page_title_and_unindexed_links_cannot_be_verified():
    mismatch = evaluate(
        TITLE,
        page(ARTS, f"Applications for the {TITLE} are open.", title="Doctor of Other Studies", source_title="Doctor of Other Studies"),
        source_url=ARTS,
    )
    assert mismatch["status"] == "not_verified" and mismatch["reason"] == "source_identity_mismatch"
    assert not mismatch["programme_page_verified"]
    missing = evaluate(TITLE, None, source_url=ARTS)
    assert missing["source_url"] == ARTS and missing["reason"] == "not_indexed"


@pytest.mark.parametrize(
    "url",
    [
        "https://example.org/study/undergraduate/arts/bachelor-x",
        "https://www.monash.edu.my@evil.invalid/study/undergraduate/arts/bachelor-x",
        "http://www.monash.edu.my/study/undergraduate/arts/bachelor-x",
        "https://www.monash.edu.my/study/apply",
        "https://www.monash.edu.my/study/undergraduate/fees",
        ARTS + "?redirect=elsewhere",
        "https://www.monash.edu.my/study/undergraduate/arts/bachelor-x/entry-score",
    ],
)
def test_non_programme_or_untrusted_links_are_rejected(url):
    assert programme_url(url) is None


def test_ambiguous_course_links_do_not_guess_a_handbook_code():
    p = page(ARTS, "No application notice")
    p.blocks[0]["spans"].append({"url": "https://handbook.monash.edu/2027/courses/B6001"})
    assert evaluate(TITLE, p, source_url=ARTS)["course_code"] is None


def test_non_malaysia_handbook_course_never_inherits_a_malaysia_notice():
    db = SimpleNamespace(scalar=lambda _: pytest.fail("must not query unrelated campus source"))
    result = a.for_course(db, "Bachelor of Psychology", None, ["Clayton"])
    assert result["status"] == "not_verified" and result["reason"] == "campus_not_verified"


def test_legacy_whole_row_links_work_without_a_new_production_refresh():
    data = blocks()
    for block in data:
        block.pop("cell_links", None)
    rows = tuition.parse_blocks(data, "malaysia-pgfees")
    assert [tuition._row(row)["programme_url"] for row in rows] == [ARTS, BUSINESS]


def test_conflicting_legacy_destinations_do_not_guess():
    data = blocks()
    table = next(b for b in data if b["type"] == "table")
    table.pop("cell_links")
    alternate = [{**table["links"][0][0], "url": BUSINESS}]
    table["links"].append(alternate)
    assert tuition._row(tuition.parse_blocks(data, "malaysia-pgfees")[0])["programme_url"] is None


def test_reviewed_sources_have_one_bounded_seed_each_and_keep_school_identity():
    from app.knowledge.malaysia_programmes import PROGRAMME_LINKS, source_for

    from crawler.official.seeds import SEEDS

    urls = {url for _, _, url in PROGRAMME_LINKS}
    assert len(urls) >= 60
    assert all(programme_url(url) == url for url in urls)
    for url in urls:
        assert len([seed for seed in SEEDS if seed.url == url]) == 1
    assert source_for(TITLE, "arts") == ARTS
    assert source_for(TITLE, "business") == BUSINESS
    assert source_for(TITLE, "unknown") is None


def test_fee_source_catalogue_is_not_proof_a_programme_has_been_fetched():
    rows = [{"title": "Bachelor of Computer Science", "school": "it"}]
    db = SimpleNamespace(scalars=lambda _: SimpleNamespace(all=list))
    result = a.for_rows(db, rows)
    assert result["linked_programme_rows"] == 1 and result["verified_programme_rows"] == 0
    assert rows[0]["admissions"]["status"] == "not_verified"
    assert rows[0]["admissions"]["reason"] == "not_indexed"


def test_seed_title_cannot_substitute_for_fetched_title():
    record = page(ARTS, f"Applications for the {TITLE} are open.")
    assert not a.evidence(TITLE, record, source_url=ARTS)["programme_page_verified"]
    result = a.evidence(TITLE, record, source_url=ARTS, source_title="Doctor of Other Studies")
    assert result["reason"] == "source_identity_mismatch"
    assert result["status"] == "not_verified"


def test_double_degree_sources_are_distinct_and_wrong_fee_anchor_is_flagged():
    from app.knowledge.malaysia_programmes import source_for

    title = "Bachelor of Business and Commerce and Bachelor of Computer Science"
    correct = "https://www.monash.edu.my/study/undergraduate/business/bachelor-business-commerce-bachelor-computer-science"
    media = correct.replace("bachelor-computer-science", "bachelor-communication")
    assert source_for(title, "business") == correct
    record = page(correct, "No application notice", source_title=title)
    rows = [{"title": title, "school": "business", "programme_url": media}]
    coverage = a.for_rows(database([record]), rows)
    assert coverage["verified_programme_rows"] == 1
    assert rows[0]["programme_url"] == media  # Preserve the fee publisher's original link.
    evidence = rows[0]["admissions"]
    assert evidence["source_url"] == correct and evidence["fee_link_conflict"]
    assert evidence["status"] == "not_verified"


def test_current_version_title_survives_seed_rename_and_rejects_unmatched_hash(db):
    from app.knowledge.repository import get_or_create_source, record_fetch, upsert_seed_page

    source = get_or_create_source(db, "synthetic-programmes", "Synthetic", "https://www.monash.edu.my")
    record = upsert_seed_page(db, source=source, slug="synthetic-programme", url=ARTS,
        title=TITLE, category="malaysia", tags=[], refresh_tier="dynamic")
    wrong = cleaner.clean_page("<main><h1>Doctor of Other Studies</h1><p>Synthetic programme content.</p></main>", url=ARTS)
    record_fetch(db, record, wrong, title=TITLE)
    db.commit()
    rows = [{"title": TITLE, "school": "arts", "programme_url": ARTS}]
    assert a.for_rows(db, rows)["verified_programme_rows"] == 0

    correct = cleaner.clean_page(f"<main><h1>{TITLE}</h1><p>Synthetic programme content.</p></main>", url=ARTS)
    record_fetch(db, record, correct, title="Curated display label")
    db.commit()
    assert a.for_rows(db, rows)["verified_programme_rows"] == 1
    assert record.title == "Curated display label"

    record.content_hash = "unmatched-current-hash"
    db.commit()
    assert a.for_rows(db, rows)["verified_programme_rows"] == 0
