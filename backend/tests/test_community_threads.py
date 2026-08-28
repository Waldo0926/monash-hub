"""Anonymity, threaded replies and likes.

Modelled on Ed, which is what students here already use: you can post without
your name on it, you can reply to a reply, and you can like either.
"""
from __future__ import annotations

import pytest

PASSWORD = "correct horse battery staple"


def _account(client, mailbox, email: str, nickname: str) -> str:
    client.post(
        "/api/v1/auth/verification-code",
        json={"email": email, "purpose": "registration"},
    )
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


@pytest.fixture
def asker(client, mailbox):
    return _account(client, mailbox, "asker@example.com", "asker")


@pytest.fixture
def helper(client, mailbox):
    return _account(client, mailbox, "helper@example.com", "helper")


def _post(client, token, **overrides) -> dict:
    body = {
        "title": "Is the hurdle really 45 percent",
        "body": "The Handbook says 45 for the classwork. Does that include the quiz?",
        "category": "units",
        **overrides,
    }
    response = client.post("/api/v1/community/posts", json=body, headers=_auth(token))
    assert response.status_code == 201, response.text
    return response.json()


def _answer(client, token, post_id, body="Yes, both count.", **overrides) -> dict:
    response = client.post(
        f"/api/v1/community/posts/{post_id}/answers",
        json={"body": body, **overrides},
        headers=_auth(token),
    )
    assert response.status_code == 201, response.text
    return response.json()


# --- anonymity --------------------------------------------------------------

def test_a_post_is_signed_unless_you_ask_otherwise(client, asker):
    """Not an account setting: the same person signs some posts and not others."""
    named = _post(client, asker)
    assert named["author"] == "asker"
    assert named["anonymous"] is False


def test_an_anonymous_post_never_names_its_author(client, asker, helper):
    post = _post(client, asker, anonymous=True)
    assert post["anonymous"] is True
    assert post["author"] is None

    # not to a stranger, not to another signed-in reader, not in the list
    for headers in ({}, _auth(helper)):
        seen = client.get(f"/api/v1/community/posts/{post['id']}", headers=headers).json()
        assert seen["author"] is None
        assert seen["anonymous"] is True

    listed = client.get("/api/v1/community/posts").json()["results"]
    assert all(p["author"] is None for p in listed if p["id"] == post["id"])


def test_the_writer_can_still_recognise_their_own_anonymous_post(client, asker, helper):
    """Anonymous to everyone else, but you should know which one was yours."""
    post = _post(client, asker, anonymous=True)
    mine = client.get(f"/api/v1/community/posts/{post['id']}", headers=_auth(asker)).json()
    assert mine["is_mine"] is True
    assert mine["author"] is None

    theirs = client.get(f"/api/v1/community/posts/{post['id']}", headers=_auth(helper)).json()
    assert theirs["is_mine"] is False


def test_a_reply_can_be_anonymous_on_a_signed_post(client, asker, helper):
    post = _post(client, asker)
    reply = _answer(client, helper, post["id"], anonymous=True)
    assert reply["anonymous"] is True
    assert reply["author"] is None

    thread = client.get(f"/api/v1/community/posts/{post['id']}").json()
    assert thread["author"] == "asker"
    assert thread["answers"][0]["author"] is None


# --- threading --------------------------------------------------------------

def test_a_reply_can_reply_to_a_reply(client, asker, helper):
    """The thing a flat list cannot say: which remark is about which answer."""
    post = _post(client, asker)
    answer = _answer(client, helper, post["id"], "Yes, both count.")
    follow_up = _answer(client, asker, post["id"], "Where does it say so?",
                        parent_id=answer["id"])
    assert follow_up["parent_id"] == answer["id"]

    thread = client.get(f"/api/v1/community/posts/{post['id']}").json()
    assert len(thread["answers"]) == 1, "a reply to a reply is not a second answer"
    assert [r["body"] for r in thread["answers"][0]["replies"]] == ["Where does it say so?"]


def test_a_thread_goes_deeper_than_two(client, asker, helper):
    post = _post(client, asker)
    first = _answer(client, helper, post["id"], "Yes.")
    second = _answer(client, asker, post["id"], "Where?", parent_id=first["id"])
    _answer(client, helper, post["id"], "Assessment section.", parent_id=second["id"])

    thread = client.get(f"/api/v1/community/posts/{post['id']}").json()
    deepest = thread["answers"][0]["replies"][0]["replies"][0]
    assert deepest["body"] == "Assessment section."


def test_a_reply_cannot_be_attached_to_another_thread(client, asker, helper):
    """Otherwise a remark appears under a post its author never opened."""
    first = _post(client, asker)
    second = _post(client, asker, title="A different question entirely")
    answer = _answer(client, helper, first["id"])

    response = client.post(
        f"/api/v1/community/posts/{second['id']}/answers",
        json={"body": "Wrong thread", "parent_id": answer["id"]},
        headers=_auth(helper),
    )
    assert response.status_code == 404


def test_only_top_level_replies_count_as_answers(client, asker, helper):
    post = _post(client, asker)
    answer = _answer(client, helper, post["id"])
    _answer(client, asker, post["id"], "A remark.", parent_id=answer["id"])

    listed = client.get(f"/api/v1/community/posts/{post['id']}/answers").json()
    assert listed["total"] == 1
    assert len(listed["results"][0]["replies"]) == 1


# --- likes ------------------------------------------------------------------

def test_a_like_is_counted_and_can_be_taken_back(client, asker, helper):
    post = _post(client, asker)
    liked = client.post(
        "/api/v1/community/vote",
        params={"target_type": "post", "target_id": post["id"]},
        headers=_auth(helper),
    ).json()
    assert liked == {"voted": True, "vote_count": 1}

    again = client.post(
        "/api/v1/community/vote",
        params={"target_type": "post", "target_id": post["id"]},
        headers=_auth(helper),
    ).json()
    assert again == {"voted": False, "vote_count": 0}


def test_the_payload_says_whether_you_have_already_liked_it(client, asker, helper):
    """Without this the heart cannot show its own state."""
    post = _post(client, asker)
    client.post(
        "/api/v1/community/vote",
        params={"target_type": "post", "target_id": post["id"]},
        headers=_auth(helper),
    )

    mine = client.get(f"/api/v1/community/posts/{post['id']}", headers=_auth(helper)).json()
    assert mine["viewer_voted"] is True

    stranger = client.get(f"/api/v1/community/posts/{post['id']}").json()
    assert stranger["viewer_voted"] is False


def test_a_reply_deep_in_a_thread_carries_its_own_like_state(client, asker, helper):
    post = _post(client, asker)
    answer = _answer(client, helper, post["id"])
    nested = _answer(client, asker, post["id"], "A remark.", parent_id=answer["id"])
    client.post(
        "/api/v1/community/vote",
        params={"target_type": "answer", "target_id": nested["id"]},
        headers=_auth(helper),
    )

    thread = client.get(f"/api/v1/community/posts/{post['id']}", headers=_auth(helper)).json()
    reply = thread["answers"][0]["replies"][0]
    assert reply["viewer_voted"] is True
    assert reply["vote_count"] == 1
    assert thread["answers"][0]["viewer_voted"] is False


def test_liking_without_an_account_is_refused_not_ignored(client, asker):
    """It used to fail silently in the browser, which reads as a broken button."""
    post = _post(client, asker)
    response = client.post(
        "/api/v1/community/vote",
        params={"target_type": "post", "target_id": post["id"]},
    )
    assert response.status_code == 401
