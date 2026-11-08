"""Synthetic year/intake notices; no copied official pages or network."""
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from app.api.v1.fees import fee_publication
from app.knowledge import admissions as a

TITLE = "Bachelor of Psychology"
NOW = datetime(2026, 11, 8, tzinfo=UTC)


@pytest.mark.parametrize("state", ["open", "closed", "suspended"])
def test_exact_programme_year_and_intake_are_required(state):
    text = f"Applications for the {TITLE} for the October 2027 intake are {state}."
    assert a.intake_notice(text, TITLE, 2027, "october") == state
    assert a.intake_notice(text, TITLE, 2028, "october") == "not_verified"
    assert a.intake_notice(text, TITLE, 2027, "february") == "not_verified"
    assert a.intake_notice(text, TITLE + " (Honours)", 2027, "october") == "not_verified"


@pytest.mark.parametrize("text", [
    f"Applications for the {TITLE} are closed.",
    f"Applications for the {TITLE} for the October 2027 intake are not open.",
    f"Applications for the {TITLE} for the October 2027 intake are open for domestic students only.",
    f"In 2026, applications for the {TITLE} for the October 2027 intake are open.",
    "October 2027 application deadline: 15 October. Apply now!",
])
def test_generic_negated_historical_and_qualified_sentences_stay_unverified(text):
    assert a.intake_notice(text, TITLE, 2027, "october") == "not_verified"


def test_explicit_campus_absence_is_not_inferred_from_a_missing_row():
    text = f"The {TITLE} is not offered at the Malaysia campus for the October 2027 intake."
    assert a.intake_notice(text, TITLE, 2027, "october") == "not_offered_on_campus"
    assert a.intake_notice(text, TITLE, 2028, "october") == "not_verified"
    assert a.intake_notice("", TITLE, 2027, "october") == "not_verified"


def test_conflicting_notices_are_not_collapsed_to_open():
    text = " ".join(f"Applications for the {TITLE} for the October 2027 intake are {s}."
                    for s in ("open", "closed"))
    assert a.intake_notice(text, TITLE, 2027, "october") == "conflict"


@pytest.mark.parametrize("failure", ["stale", "failed", "identity"])
def test_scoped_notice_still_needs_a_fresh_matching_programme_source(failure):
    page = SimpleNamespace(
        canonical_url=a.PROGRAMMES[a.normalise(TITLE)][1],
        clean_text=f"Applications for the {TITLE} for the October 2027 intake are open.",
        last_checked=NOW - timedelta(days=31 if failure == "stale" else 1),
        status="ok", fetch_error="HTTP 503" if failure == "failed" else None,
        requires_sign_in=False, content_hash="synthetic", blocks=[],
    )
    result = a.evidence(TITLE, page, now=NOW,
                        source_title="Another degree" if failure == "identity" else TITLE,
                        intake_year=2027, intake_period="october")
    assert result["intake_status"] == "not_verified"
    assert result["effective_year"] is None


def test_scoped_open_does_not_become_a_timeless_current_notice():
    page = SimpleNamespace(
        canonical_url=a.PROGRAMMES[a.normalise(TITLE)][1],
        clean_text=f"Applications for the {TITLE} for the October 2027 intake are open.",
        last_checked=NOW, status="ok", fetch_error=None, requires_sign_in=False,
        content_hash="synthetic", blocks=[],
    )
    result = a.evidence(TITLE, page, now=NOW, source_title=TITLE,
                        intake_year=2027, intake_period="october")
    assert result["status"] == "not_verified" and result["intake_status"] == "open"
    assert result["effective_year"] == 2027 and result["source_hash"] == "synthetic"


def test_fee_year_basis_and_freshness_are_separate_from_admissions():
    source = {"last_checked": NOW.isoformat(), "source_hash": "synthetic", "url": "https://example.invalid/fees"}
    row = {"unreadable": False, "basis": "full_course"}
    assert fee_publication(row, 2027, 2027, source, now=NOW)["status"] == "published"
    mismatch = fee_publication(row, 2027, 2028, source, now=NOW)
    assert mismatch["status"] == "not_verified" and mismatch["reason"] == "different_fee_year"
    assert mismatch["basis"] == "full_course" and mismatch["published_year"] == 2027
    assert fee_publication(row, None, 2027, source, now=NOW)["reason"] == "unknown_fee_year"
    assert fee_publication(row, 2027, 2027, source | {"refresh_failed": True}, now=NOW)["reason"] == "refresh_failed"
    old = source | {"last_checked": (NOW - timedelta(days=31)).isoformat()}
    assert fee_publication(row, 2027, 2027, old, now=NOW)["reason"] == "stale_source"


def test_fee_api_preserves_selection_and_does_not_relabel_another_fee_year(client, db):
    from tests.test_tuition import _store

    _store(db)
    response = client.get("/api/v1/fees?year=2028&intake=july&campus=Malaysia")
    assert response.status_code == 200
    data = response.json()
    assert data["selection"] == {"year": 2028, "intake": "july", "campus": "Malaysia"}
    rows = [row for s in data["sections"] for g in s["schools"] for row in g["rows"]]
    assert rows and all(row["fee_publication"]["reason"] == "different_fee_year" for row in rows)
    assert all(row["admissions"]["intake_status"] == "not_verified" for row in rows)
    for query in ("year=2027.5", "intake=unknown", "campus=Clayton"):
        assert client.get("/api/v1/fees?" + query).status_code == 422
