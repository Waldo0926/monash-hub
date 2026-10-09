"""The forum's state machine at its edges.

Each test is a combination the happy-path tests never reached: a hidden post
whose replies were still readable, a nested reply "accepted" without anything
changing, a count decremented twice, a moderator's takedown that could never be
undone, and a thread with no bottom.
"""
from __future__ import annotations

from app.api.v1.community import MAX_REPLY_DEPTH
from app.models.user import User

PASSWORD = "Correct-Horse-9"


def _account(client, mailbox, email: str, nickname: str) -> dict:
    client.post("/api/v1/auth/verification-code", json={"email": email, "purpose": "registration"})
    response = client.post("/api/v1/auth/signup", json={
        "email": email, "nickname": nickname, "password": PASSWORD,
        "verification_code": mailbox.code_for(email),
    })
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['token']}"}


def _moderator(client, db, mailbox, email: str, nickname: str) -> dict:
    auth = _account(client, mailbox, email, nickname)
    db.query(User).filter(User.nickname == nickname).update({"is_admin": True})
    db.commit()
    return auth


def _post(client, auth, **extra) -> dict:
    body = {"title": "How hard is FIT2004?", "body": "Asking before I enrol next term.",
            "category": "units", **extra}
    response = client.post("/api/v1/community/posts", headers=auth, json=body)
    assert response.status_code == 201, response.text
    return response.json()


def _answer(client, auth, post_id: int, body: str = "Hard but fair.", **extra) -> dict:
    response = client.post(f"/api/v1/community/posts/{post_id}/answers",
                           headers=auth, json={"body": body, **extra})
    assert response.status_code == 201, response.text
    return response.json()


def _count(client, post_id: int) -> int:
    return client.get(f"/api/v1/community/posts/{post_id}").json()["answer_count"]


# --- visibility -----------------------------------------------------------------

def test_replies_under_a_hidden_post_are_not_listed(client, db, mailbox):
    author = _account(client, mailbox, "author@example.com", "author")
    helper = _account(client, mailbox, "helper@example.com", "helper")
    post = _post(client, author)
    _answer(client, helper, post["id"], "Here is my name in a screenshot.")

    assert client.get(f"/api/v1/community/posts/{post['id']}/answers").json()["total"] == 1
    assert client.delete(f"/api/v1/community/posts/{post['id']}", headers=author).status_code == 200
    assert client.get(f"/api/v1/community/posts/{post['id']}/answers").status_code == 404


# --- accepting ------------------------------------------------------------------

def test_a_nested_reply_cannot_be_the_accepted_answer(client, db, mailbox):
    asker = _account(client, mailbox, "asker@example.com", "asker")
    helper = _account(client, mailbox, "helper@example.com", "helper")
    post = _post(client, asker)
    top = _answer(client, helper, post["id"])
    nested = _answer(client, asker, post["id"], "Which part?", parent_id=top["id"])

    refused = client.post(f"/api/v1/community/answers/{nested['id']}/accept", headers=asker)
    assert refused.status_code == 400
    assert client.get(f"/api/v1/community/posts/{post['id']}").json()["is_solved"] is False


def test_accepting_a_second_answer_un_accepts_the_first(client, db, mailbox):
    asker = _account(client, mailbox, "asker@example.com", "asker")
    helper = _account(client, mailbox, "helper@example.com", "helper")
    post = _post(client, asker)
    first = _answer(client, helper, post["id"], "First try.")
    second = _answer(client, helper, post["id"], "Better answer.")

    assert client.post(f"/api/v1/community/answers/{first['id']}/accept", headers=asker).status_code == 200
    assert client.post(f"/api/v1/community/answers/{second['id']}/accept", headers=asker).status_code == 200
    answers = client.get(f"/api/v1/community/posts/{post['id']}").json()["answers"]
    accepted = {a["id"]: a["is_accepted"] for a in answers}
    assert accepted == {first["id"]: False, second["id"]: True}


# --- counting -------------------------------------------------------------------

def test_hiding_a_reply_its_author_deleted_does_not_count_it_twice(client, db, mailbox):
    asker = _account(client, mailbox, "asker@example.com", "asker")
    helper = _account(client, mailbox, "helper@example.com", "helper")
    mod = _moderator(client, db, mailbox, "mod@example.com", "moderator")
    post = _post(client, asker)
    keep = _answer(client, helper, post["id"], "This one stays.")
    gone = _answer(client, helper, post["id"], "This one goes.")
    assert _count(client, post["id"]) == 2

    assert client.delete(f"/api/v1/community/answers/{gone['id']}", headers=helper).status_code == 200
    assert _count(client, post["id"]) == 1
    client.post(f"/api/v1/community/moderate/answer/{gone['id']}", params={"action": "hide"}, headers=mod)
    assert _count(client, post["id"]) == 1
    client.post(f"/api/v1/community/moderate/answer/{keep['id']}", params={"action": "hide"}, headers=mod)
    assert _count(client, post["id"]) == 0


# --- who took it down ---------------------------------------------------------------

def test_a_moderators_takedown_can_be_undone_but_the_authors_cannot(client, db, mailbox):
    author = _account(client, mailbox, "author@example.com", "author")
    mod = _moderator(client, db, mailbox, "mod@example.com", "moderator")
    by_mod = _post(client, author, title="Taken down by a moderator")
    by_author = _post(client, author, title="Taken down by its author")

    assert client.delete(f"/api/v1/community/posts/{by_mod['id']}", headers=mod).status_code == 200
    assert client.delete(f"/api/v1/community/posts/{by_author['id']}", headers=author).status_code == 200

    restored = client.post(f"/api/v1/community/moderate/post/{by_mod['id']}",
                           params={"action": "unhide"}, headers=mod)
    assert restored.status_code == 200
    assert client.get(f"/api/v1/community/posts/{by_mod['id']}").status_code == 200

    refused = client.post(f"/api/v1/community/moderate/post/{by_author['id']}",
                          params={"action": "unhide"}, headers=mod)
    assert refused.status_code == 409


def test_a_moderator_removing_a_reply_hides_it_rather_than_leaving_a_placeholder(client, db, mailbox):
    asker = _account(client, mailbox, "asker@example.com", "asker")
    helper = _account(client, mailbox, "helper@example.com", "helper")
    mod = _moderator(client, db, mailbox, "mod@example.com", "moderator")
    post = _post(client, asker)
    answer = _answer(client, helper, post["id"], "Something that had to go.")
    _answer(client, asker, post["id"], "A reply under it.", parent_id=answer["id"])

    assert client.delete(f"/api/v1/community/answers/{answer['id']}", headers=mod).status_code == 200
    thread = client.get(f"/api/v1/community/posts/{post['id']}").json()
    assert thread["answers"] == []
    # And a moderator can bring it back, which a placeholder never allows.
    restored = client.post(f"/api/v1/community/moderate/answer/{answer['id']}",
                           params={"action": "unhide"}, headers=mod)
    assert restored.status_code == 200
    thread = client.get(f"/api/v1/community/posts/{post['id']}").json()
    assert [a["body"] for a in thread["answers"]] == ["Something that had to go."]


# --- depth ------------------------------------------------------------------------

def test_a_thread_has_a_bottom(client, db, mailbox):
    asker = _account(client, mailbox, "asker@example.com", "asker")
    post = _post(client, asker)
    parent = _answer(client, asker, post["id"], "depth 1")
    for depth in range(2, MAX_REPLY_DEPTH + 4):
        parent = _answer(client, asker, post["id"], f"depth {depth}", parent_id=parent["id"])

    thread = client.get(f"/api/v1/community/posts/{post['id']}").json()
    level, deepest = thread["answers"][0], 1
    while level["replies"]:
        assert len(level["replies"]) in (1, 4) or deepest < MAX_REPLY_DEPTH - 1
        level, deepest = level["replies"][0], deepest + 1
    assert deepest == MAX_REPLY_DEPTH
    # The replies past the limit sit at the bottom level, not below it.
    bottom_parent = thread["answers"][0]
    for _ in range(MAX_REPLY_DEPTH - 2):
        bottom_parent = bottom_parent["replies"][0]
    assert [r["body"] for r in bottom_parent["replies"]] == [
        f"depth {d}" for d in range(MAX_REPLY_DEPTH, MAX_REPLY_DEPTH + 4)
    ]


# --- notifications -------------------------------------------------------------

def test_marking_an_empty_list_read_marks_nothing(client, db, mailbox):
    asker = _account(client, mailbox, "asker@example.com", "asker")
    helper = _account(client, mailbox, "helper@example.com", "helper")
    post = _post(client, asker)
    _answer(client, helper, post["id"])

    nothing = client.post("/api/v1/notifications/read", json={"ids": []}, headers=asker)
    assert nothing.json() == {"marked": 0, "unread": 1}
    everything = client.post("/api/v1/notifications/read", json={}, headers=asker)
    assert everything.json() == {"marked": 1, "unread": 0}
