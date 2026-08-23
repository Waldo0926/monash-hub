"""Notifications, and the counters they sit alongside.

The product question behind these: if you ask something and nobody tells you it
was answered, you do not come back. So an answer has to reach the asker, and it
has to be visible from the home page without hunting for the thread.
"""
from __future__ import annotations

PASSWORD = "Correct-Horse-9"


def _account(client, mailbox, email: str, nickname: str) -> str:
    client.post("/api/v1/auth/verification-code", json={"email": email, "purpose": "registration"})
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


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _post(client, token: str, title: str = "How heavy is FIT2102 really?") -> int:
    response = client.post(
        "/api/v1/community/posts",
        json={
            "title": title,
            "body": "Trying to work out whether to take it with three other units.",
            "category": "units",
            "unit_code": "FIT2102",
        },
        headers=_auth(token),
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _answer(client, token: str, post_id: int, body: str = "About twelve hours a week.") -> int:
    response = client.post(
        f"/api/v1/community/posts/{post_id}/answers", json={"body": body}, headers=_auth(token)
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_an_answer_notifies_the_asker(client, db, mailbox):
    asker = _account(client, mailbox, "asker@example.com", "asker")
    helper = _account(client, mailbox, "helper@example.com", "helper")

    post_id = _post(client, asker)
    _answer(client, helper, post_id)

    feed = client.get("/api/v1/notifications", headers=_auth(asker)).json()
    assert feed["unread"] == 1
    item = feed["results"][0]
    assert item["kind"] == "answer"
    assert item["actor"] == "helper"
    assert item["post_id"] == post_id
    assert item["post_title"] == "How heavy is FIT2102 really?"
    assert "twelve hours" in item["excerpt"]
    assert item["is_read"] is False


def test_answering_your_own_post_notifies_nobody(client, db, mailbox):
    asker = _account(client, mailbox, "solo@example.com", "solo")
    post_id = _post(client, asker)
    _answer(client, asker, post_id)

    feed = client.get("/api/v1/notifications", headers=_auth(asker)).json()
    assert feed["unread"] == 0
    assert feed["results"] == []


def test_marking_an_answer_helpful_notifies_the_answerer(client, db, mailbox):
    asker = _account(client, mailbox, "grateful@example.com", "grateful")
    helper = _account(client, mailbox, "expert@example.com", "expert")

    post_id = _post(client, asker)
    answer_id = _answer(client, helper, post_id)
    accepted = client.post(f"/api/v1/community/answers/{answer_id}/accept", headers=_auth(asker))
    assert accepted.status_code == 200

    feed = client.get("/api/v1/notifications", headers=_auth(helper)).json()
    kinds = [n["kind"] for n in feed["results"]]
    assert "accepted" in kinds
    assert feed["unread"] >= 1


def test_notifications_are_private_to_their_owner(client, db, mailbox):
    asker = _account(client, mailbox, "owner@example.com", "owner")
    helper = _account(client, mailbox, "other@example.com", "other")
    _answer(client, helper, _post(client, asker))

    assert client.get("/api/v1/notifications", headers=_auth(helper)).json()["unread"] == 0
    assert client.get("/api/v1/notifications").status_code == 401


def test_marking_read_clears_the_badge(client, db, mailbox):
    asker = _account(client, mailbox, "reader@example.com", "reader")
    helper = _account(client, mailbox, "writer@example.com", "writer")
    post_id = _post(client, asker)
    _answer(client, helper, post_id)
    _answer(client, helper, post_id, body="Also the applied sessions are compulsory.")

    assert client.get("/api/v1/notifications/unread-count", headers=_auth(asker)).json()["unread"] == 2

    first = client.get("/api/v1/notifications", headers=_auth(asker)).json()["results"][0]["id"]
    one = client.post("/api/v1/notifications/read", json={"ids": [first]}, headers=_auth(asker))
    assert one.json() == {"marked": 1, "unread": 1}

    everything = client.post("/api/v1/notifications/read", json={}, headers=_auth(asker))
    assert everything.json() == {"marked": 1, "unread": 0}


def test_the_thread_shows_who_wrote_what(client, db, mailbox):
    asker = _account(client, mailbox, "who@example.com", "who")
    helper = _account(client, mailbox, "whom@example.com", "whom")
    post_id = _post(client, asker)
    _answer(client, helper, post_id)

    detail = client.get(f"/api/v1/community/posts/{post_id}").json()
    assert detail["author"] == "who"
    assert detail["body"].startswith("Trying to work out")
    assert [a["author"] for a in detail["answers"]] == ["whom"]
    assert detail["answers"][0]["body"] == "About twelve hours a week."

    listed = client.get("/api/v1/community/posts").json()["results"][0]
    assert listed["author"] == "who"
    assert listed["answer_count"] == 1


def test_answer_count_and_ordering_survive_several_answers(client, db, mailbox):
    asker = _account(client, mailbox, "counter@example.com", "counter")
    helper = _account(client, mailbox, "many@example.com", "many")
    post_id = _post(client, asker)
    for i in range(5):
        _answer(client, helper, post_id, body=f"Answer number {i}.")

    detail = client.get(f"/api/v1/community/posts/{post_id}").json()
    assert detail["answer_count"] == 5
    assert len(detail["answers"]) == 5
    assert client.get("/api/v1/notifications", headers=_auth(asker)).json()["unread"] == 5


def test_views_and_votes_are_counted(client, db, mailbox):
    asker = _account(client, mailbox, "views@example.com", "views")
    voter = _account(client, mailbox, "voter@example.com", "voter")
    post_id = _post(client, asker)

    for _ in range(3):
        client.get(f"/api/v1/community/posts/{post_id}")

    up = client.post(
        f"/api/v1/community/vote?target_type=post&target_id={post_id}", headers=_auth(voter)
    ).json()
    assert up == {"voted": True, "vote_count": 1}
    down = client.post(
        f"/api/v1/community/vote?target_type=post&target_id={post_id}", headers=_auth(voter)
    ).json()
    assert down == {"voted": False, "vote_count": 0}


def test_a_hidden_post_disappears_from_the_feed(client, db, mailbox):
    from app.models.user import User

    asker = _account(client, mailbox, "hidden@example.com", "hidden")
    post_id = _post(client, asker)

    admin_token = _account(client, mailbox, "mod@example.com", "moderator")
    db.query(User).filter(User.email == "mod@example.com").update({"is_admin": True})
    db.commit()

    moderated = client.post(
        f"/api/v1/community/moderate/post/{post_id}?action=hide", headers=_auth(admin_token)
    )
    assert moderated.status_code == 200
    assert client.get(f"/api/v1/community/posts/{post_id}").status_code == 404
    assert client.get("/api/v1/community/posts").json()["total"] == 0
