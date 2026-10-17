"""Unit ratings: one per student, averaged from what is visible, moderated like posts."""
from __future__ import annotations

import pytest
from app.core import throttle
from app.handbook.parser import parse_unit_page, unit_url
from app.handbook.repository import upsert_unit
from app.models.user import User

PASSWORD = "Correct-Horse-9"
BROWSER = {"X-Guest-Key": "0b7c1f0e-5d1a-4b8e-9b55-2f4f5a1c9e01"}
OTHER_BROWSER = {"X-Guest-Key": "6a2d9c44-1e7b-4f0a-8c3d-77e1b0f2a6d9"}


@pytest.fixture
def unit(db, handbook_html):
    upsert_unit(db, parse_unit_page(handbook_html("FIT2102"), unit_url("FIT2102", 2026)))
    db.commit()
    return "FIT2102"


def _account(client, mailbox, email: str, nickname: str) -> dict:
    client.post("/api/v1/auth/verification-code", json={"email": email, "purpose": "registration"})
    response = client.post("/api/v1/auth/signup", json={
        "email": email, "nickname": nickname, "password": PASSWORD,
        "verification_code": mailbox.code_for(email),
    })
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['token']}"}


def _rate(client, auth, code: str = "FIT2102", **scores) -> dict:
    response = client.put(f"/api/v1/reviews/units/{code}", headers=auth,
                          json={"overall": 4, **scores})
    assert response.status_code == 200, response.text
    return response.json()


def test_rating_again_edits_the_same_row(client, db, mailbox, unit):
    auth = _account(client, mailbox, "wen@example.com", "wen")
    first = _rate(client, auth, overall=2, body="  Rough start.  ")
    assert first["created"] is True
    assert first["body"] == "Rough start."
    second = _rate(client, auth, overall=5)
    assert second["created"] is False
    assert second["id"] == first["id"]

    page = client.get("/api/v1/reviews/units/fit2102").json()
    assert page["total"] == 1
    assert page["summary"]["average"] == 5
    assert page["summary"]["distribution"] == {"1": 0, "2": 0, "3": 0, "4": 0, "5": 1}


def test_the_average_and_each_dimension_count_only_who_answered(client, db, mailbox, unit):
    a = _account(client, mailbox, "a@example.com", "alice")
    b = _account(client, mailbox, "b@example.com", "bob")
    c = _account(client, mailbox, "c@example.com", "carol")
    _rate(client, a, overall=5, teaching=4, workload=5)
    _rate(client, b, overall=3, teaching=2)
    _rate(client, c, overall=4)

    summary = client.get("/api/v1/reviews/units/FIT2102").json()["summary"]
    assert summary["count"] == 3
    assert summary["average"] == 4
    assert summary["dimensions"]["teaching"] == {"average": 3, "count": 2}
    assert summary["dimensions"]["workload"] == {"average": 5, "count": 1}
    assert summary["dimensions"]["content"] == {"average": None, "count": 0}
    assert summary["distribution"] == {"1": 0, "2": 0, "3": 1, "4": 1, "5": 1}


def test_other_readers_see_initials_and_the_author_sees_their_own(client, db, mailbox, unit):
    author = _account(client, mailbox, "wen@example.com", "waldo")
    reader = _account(client, mailbox, "reader@example.com", "reader")
    _rate(client, author, body="Good lectures.")

    seen = client.get("/api/v1/reviews/units/FIT2102", headers=reader).json()
    assert seen["results"][0]["author"] == "W."
    assert seen["results"][0]["is_mine"] is False
    assert seen["mine"] is None
    assert "waldo" not in str(seen)

    own = client.get("/api/v1/reviews/units/FIT2102", headers=author).json()
    assert own["results"][0]["is_mine"] is True
    assert own["mine"]["body"] == "Good lectures."


def test_writing_needs_an_owner_a_real_unit_and_scores_in_range(client, db, mailbox, unit):
    # Neither an account nor a browser key: nobody could edit it afterwards.
    assert client.put("/api/v1/reviews/units/FIT2102", json={"overall": 4}).status_code == 401
    assert client.put("/api/v1/reviews/units/FIT2102", headers={"X-Guest-Key": "short"},
                      json={"overall": 4}).status_code == 401
    auth = _account(client, mailbox, "wen@example.com", "wen")
    assert client.put("/api/v1/reviews/units/FIT9999", headers=auth,
                      json={"overall": 4}).status_code == 404
    assert client.put("/api/v1/reviews/units/not-a-unit", headers=auth,
                      json={"overall": 4}).status_code == 422
    for bad in ({"overall": 0}, {"overall": 6}, {"overall": 3, "difficulty": 9}, {}):
        assert client.put("/api/v1/reviews/units/FIT2102", headers=auth,
                          json=bad).status_code == 422


def test_taking_a_rating_back_removes_it(client, db, mailbox, unit):
    auth = _account(client, mailbox, "wen@example.com", "wen")
    _rate(client, auth)
    assert client.delete("/api/v1/reviews/units/FIT2102", headers=auth).status_code == 200
    assert client.get("/api/v1/reviews/units/FIT2102").json()["summary"]["count"] == 0
    assert client.delete("/api/v1/reviews/units/FIT2102", headers=auth).status_code == 404


def test_a_reported_rating_a_moderator_hides_leaves_the_average(client, db, mailbox, unit):
    author = _account(client, mailbox, "wen@example.com", "wen")
    fair = _account(client, mailbox, "fair@example.com", "fair")
    mod = _account(client, mailbox, "mod@example.com", "moderator")
    db.query(User).filter(User.nickname == "moderator").update({"is_admin": True})
    db.commit()
    rude = _rate(client, author, overall=1, body="Something that had to go.")
    _rate(client, fair, overall=5)

    report = client.post("/api/v1/community/reports", headers=fair, json={
        "target_type": "review", "target_id": rude["id"], "reason": "abuse"})
    assert report.status_code in (200, 201), report.text

    queue = client.get("/api/v1/community/reports", headers=mod).json()["results"]
    assert queue[0]["target_type"] == "review"
    assert queue[0]["target"]["unit_code"] == "FIT2102"
    assert client.post(f"/api/v1/community/reports/{queue[0]['id']}/resolve",
                       params={"action": "hide"}, headers=mod).status_code == 200

    public = client.get("/api/v1/reviews/units/FIT2102").json()
    assert public["summary"] == {**public["summary"], "count": 1, "average": 5}
    assert [r["overall"] for r in public["results"]] == [5]
    # Its author still sees it, marked hidden, instead of it silently vanishing.
    own = client.get("/api/v1/reviews/units/FIT2102", headers=author).json()["mine"]
    assert own["hidden"] is True

    restored = client.post(f"/api/v1/community/moderate/review/{rude['id']}",
                           params={"action": "unhide"}, headers=mod)
    assert restored.status_code == 200
    assert client.get("/api/v1/reviews/units/FIT2102").json()["summary"]["count"] == 2


def test_unit_lists_carry_the_rating(client, db, mailbox, unit):
    listed = client.get("/api/v1/units", params={"codes": "FIT2102"}).json()["results"]
    assert listed[0]["rating"] is None

    auth = _account(client, mailbox, "wen@example.com", "wen")
    _rate(client, auth, overall=3)
    listed = client.get("/api/v1/units", params={"codes": "FIT2102"}).json()["results"]
    assert listed[0]["rating"] == {"average": 3, "count": 1}
    summary = client.get("/api/v1/reviews/summary", params={"codes": "FIT2102, BFF2140"}).json()
    assert summary == {"results": {"FIT2102": {"average": 3, "count": 1}}}


def test_limit_zero_is_the_summary_alone(client, db, mailbox, unit):
    auth = _account(client, mailbox, "wen@example.com", "wen")
    _rate(client, auth, overall=4, difficulty=2)
    page = client.get("/api/v1/reviews/units/FIT2102", params={"limit": 0}).json()
    assert page["results"] == []
    assert page["total"] == 1
    assert page["summary"]["dimensions"]["difficulty"] == {"average": 2, "count": 1}


def test_a_browser_can_rate_without_signing_in_and_change_its_mind(client, db, unit):
    first = _rate(client, BROWSER, overall=2, body="Signed out.")
    assert first["created"] is True
    assert first["author"] is None and first["is_guest"] is True
    again = _rate(client, BROWSER, overall=4)
    assert again["id"] == first["id"] and again["created"] is False

    page = client.get("/api/v1/reviews/units/FIT2102", headers=BROWSER).json()
    assert page["total"] == 1 and page["summary"]["average"] == 4
    assert page["mine"]["id"] == first["id"]
    assert page["results"][0]["is_mine"] is True

    # Another browser sees it as somebody else's and rates on its own.
    other = client.get("/api/v1/reviews/units/FIT2102", headers=OTHER_BROWSER).json()
    assert other["mine"] is None and other["results"][0]["is_mine"] is False
    _rate(client, OTHER_BROWSER, overall=5)
    assert client.get("/api/v1/reviews/units/FIT2102").json()["summary"]["count"] == 2

    assert client.delete("/api/v1/reviews/units/FIT2102", headers=OTHER_BROWSER).status_code == 200
    assert client.delete("/api/v1/reviews/units/FIT2102", headers=OTHER_BROWSER).status_code == 404
    assert client.get("/api/v1/reviews/units/FIT2102").json()["summary"]["count"] == 1


def test_the_browser_key_is_not_stored_as_sent(client, db, unit):
    from app.models.review import UnitReview

    _rate(client, BROWSER)
    stored = db.query(UnitReview).one().guest_key
    assert stored and BROWSER["X-Guest-Key"] not in stored


def test_signed_out_ratings_are_limited_per_network(client, db, unit, monkeypatch):
    monkeypatch.setattr(throttle, "REVIEWS_PER_ADDRESS", throttle.Limit(throttle.REVIEW_IP, 2, 3600))
    keys = [f"{i:08d}-aaaa-4bbb-8ccc-dddddddddddd" for i in range(3)]
    for key in keys[:2]:
        _rate(client, {"X-Guest-Key": key})
    # A fresh key does not get round it: the limit is on the address.
    limited = client.put("/api/v1/reviews/units/FIT2102", headers={"X-Guest-Key": keys[2]},
                         json={"overall": 4})
    assert limited.status_code == 429
