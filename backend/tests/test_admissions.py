"""Synthetic programme notices; no copied pages, real accounts or network."""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from app.knowledge import admissions as a
from sqlalchemy import select

TITLE = "Master of Professional Counselling"
NOW = datetime(2026, 11, 3, tzinfo=UTC)


def page(text=None, **kwargs):
    values = {
        "canonical_url": a.PROGRAMMES[a.normalise(TITLE)][1],
        "clean_text": text or f"Applications for the {TITLE} are currently closed.",
        "status": "ok",
        "fetch_error": None,
        "requires_sign_in": False,
        "last_checked": NOW - timedelta(days=1),
        "content_hash": "synthetic",
    }
    return SimpleNamespace(**(values | kwargs))


def test_explicit_scoped_notice_is_separate_from_future_intake():
    result = a.evidence(TITLE, page(), now=NOW)
    assert result["status"] == "closed" and result["intake_status"] == "not_verified"
    assert result["course_code"] == "D6006"
    assert result["source_url"] and result["source_hash"] == "synthetic"
    assert result["valid_until"] and result["scope"] == "current_programme_notice"


@pytest.mark.parametrize(
    "text",
    [
        "In 2025, Applications for the Master of Professional Counselling are closed.",
        "Apply now! February 2027 application deadline: 18 December 2026.",
        "Applications for the Master of Other Studies are currently open.",
        "Applications for the Master of Professional Counselling are not currently open.",
        "Applications for the Master of Professional Counselling are currently closed for international students only.",
    ],
)
def test_buttons_dates_unrelated_negated_or_qualified_notices_do_not_prove_open(text):
    assert a.notice(text, TITLE) == "not_verified"


@pytest.mark.parametrize(
    "changes,reason",
    [
        ({"last_checked": NOW - timedelta(days=31)}, "stale_source"),
        ({"last_checked": None}, "stale_source"),
        ({"last_checked": NOW + timedelta(days=1)}, "stale_source"),
        ({"status": "error"}, "source_unavailable"),
        ({"fetch_error": "HTTP error"}, "source_unavailable"),
        ({"requires_sign_in": True}, "source_unavailable"),
    ],
)
def test_stale_failed_and_unavailable_sources_fall_back(changes, reason):
    result = a.evidence(TITLE, page(**changes), now=NOW)
    assert result["status"] == "not_verified" and result["reason"] == reason
    assert result["observed_status"] == "closed"


def test_conflicting_notices_require_review():
    p = page(f"Applications for the {TITLE} are open. Applications for the {TITLE} are closed.")
    result = a.evidence(TITLE, p, now=NOW)
    assert result["status"] == "conflict" and result["reason"] == "conflict"


def test_missing_and_wrong_degree_sources_stay_unverified():
    assert a.evidence(TITLE, None, now=NOW)["status"] == "not_verified"
    assert (
        a.evidence(TITLE, page(canonical_url="https://example.invalid/"), now=NOW)["status"]
        == "not_verified"
    )
    assert (
        a.evidence("Bachelor of Psychology (Honours)", None, now=NOW)["reason"]
        == "no_reviewed_source"
    )


def test_indexed_programme_notice_and_fee_api_stay_independent(client, db):
    from app.models.knowledge import OfficialPage, OfficialSource

    from tests.test_tuition import _store

    _store(db)
    source = db.scalar(select(OfficialSource))
    db.add(
        OfficialPage(
            source_id=source.id,
            slug=a.PROGRAMMES[a.normalise(TITLE)][0],
            canonical_url=a.PROGRAMMES[a.normalise(TITLE)][1],
            title=TITLE,
            category="malaysia",
            applies_to="malaysia",
            tags=[],
            status="ok",
            clean_text=f"Applications for the {TITLE} are currently closed.",
            content_hash="synthetic",
            last_checked=datetime.now(UTC) - timedelta(hours=1),
        )
    )
    db.commit()
    assert a.for_titles(db, [TITLE])[TITLE]["status"] == "closed"
    # Unrelated fee rows cannot inherit this application's state.
    result = client.get("/api/v1/fees").json()
    rows = [
        row
        for section in result["sections"]
        for group in section["schools"]
        for row in group["rows"]
    ]
    assert rows and all(row["admissions"]["status"] == "not_verified" for row in rows)
