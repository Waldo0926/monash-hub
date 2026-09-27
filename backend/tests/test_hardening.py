"""Account safety, anonymity and forum integrity.

Each test here is a way the public site could be abused or could betray
somebody before this change: password guessing with no limit, a reset form
that told strangers which nickname an address belonged to, notifications that
named anonymous writers, and posts their own authors could not take down.
"""
from __future__ import annotations

import pytest

PASSWORD = "Correct-Horse-9"


def _account(client, mailbox, email: str, nickname: str) -> dict:
    client.post("/api/v1/auth/verification-code", json={"email": email, "purpose": "registration"})
    response = client.post("/api/v1/auth/signup", json={
        "email": email, "nickname": nickname, "password": PASSWORD,
        "verification_code": mailbox.code_for(email),
    })
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['token']}"}


def _post(client, auth, **extra) -> dict:
    body = {"title": "How hard is FIT2004?", "body": "Asking before I enrol next term.",
            "category": "units", **extra}
    response = client.post("/api/v1/community/posts", headers=auth, json=body)
    assert response.status_code == 201, response.text
    return response.json()


def _sign_in(client, email, password):
    return client.post("/api/v1/auth/signin", json={"email": email, "password": password})


# --- sign-in ---------------------------------------------------------------------

def test_password_guessing_is_stopped_per_account(client, db, mailbox):
    _account(client, mailbox, "target@example.com", "target")
    for _ in range(10):
        assert _sign_in(client, "target@example.com", "Wrong-guess-1").status_code == 401
    blocked = _sign_in(client, "target@example.com", PASSWORD)
    assert blocked.status_code == 429
    assert int(blocked.headers["Retry-After"]) > 0


def test_an_unknown_address_is_limited_exactly_like_a_real_one(client, db):
    """A lockout only real accounts could reach would say which ones exist."""
    answers = [_sign_in(client, "nobody@example.com", "Wrong-guess-1").status_code
               for _ in range(11)]
    assert answers == [401] * 10 + [429]


def test_a_successful_sign_in_clears_the_count(client, db, mailbox):
    _account(client, mailbox, "forgetful@example.com", "forgetful")
    for _ in range(9):
        _sign_in(client, "forgetful@example.com", "Wrong-guess-1")
    assert _sign_in(client, "forgetful@example.com", PASSWORD).status_code == 200
    for _ in range(9):
        assert _sign_in(client, "forgetful@example.com", "Wrong-guess-1").status_code == 401


def test_code_requests_are_limited_per_client_address(client, db, mailbox):
    """One client asking for codes to a long list of other people's addresses."""
    codes = [
        client.post("/api/v1/auth/verification-code",
                    json={"email": f"victim{i}@example.com", "purpose": "registration"},
                    headers={"X-Real-IP": "203.0.113.9"}).status_code
        for i in range(31)
    ]
    assert codes[:30] == [200] * 30
    assert codes[30] == 429
    # Somebody else on another address is unaffected.
    assert client.post("/api/v1/auth/verification-code",
                       json={"email": "fresh@example.com", "purpose": "registration"},
                       headers={"X-Real-IP": "198.51.100.1"}).status_code == 200


# --- password reset ----------------------------------------------------------------

def test_reset_does_not_reveal_the_nickname_before_the_code_is_proven(client, db, mailbox):
    _account(client, mailbox, "secret@example.com", "quietfox")
    client.post("/api/v1/auth/verification-code",
                json={"email": "secret@example.com", "purpose": "password_reset"})

    # A stranger guessing the nickname learns nothing: same answer as any wrong code.
    guess = client.post("/api/v1/auth/password-reset", json={
        "email": "secret@example.com", "verification_code": "000000",
        "password": "quietfox-Rules-1",
    })
    assert guess.status_code == 400
    assert "nickname" not in guess.text.lower()

    # The owner, with the real code, is told - and the code survives the refusal.
    code = mailbox.code_for("secret@example.com")
    refused = client.post("/api/v1/auth/password-reset", json={
        "email": "secret@example.com", "verification_code": code,
        "password": "quietfox-Rules-1",
    })
    assert refused.status_code == 422
    accepted = client.post("/api/v1/auth/password-reset", json={
        "email": "secret@example.com", "verification_code": code,
        "password": "Brand-New-Pass-7",
    })
    assert accepted.status_code == 200, accepted.text


# --- anonymity ---------------------------------------------------------------------

def test_an_anonymous_answer_is_not_named_in_the_askers_notification(client, db, mailbox):
    asker = _account(client, mailbox, "asker@example.com", "asker")
    helper = _account(client, mailbox, "helper@example.com", "helper")
    post = _post(client, asker)
    answer = client.post(f"/api/v1/community/posts/{post['id']}/answers", headers=helper,
                         json={"body": "It is fine if you practise.", "anonymous": True}).json()

    notes = client.get("/api/v1/notifications", headers=asker).json()["results"]
    assert notes[0]["kind"] == "answer"
    assert notes[0]["actor"] is None
    assert "helper" not in str(notes)

    client.post(f"/api/v1/community/answers/{answer['id']}/accept", headers=asker)
    assert client.get("/api/v1/notifications", headers=helper).json()["results"][0]["actor"] \
        == "asker"


def test_an_anonymous_asker_is_not_named_when_accepting(client, db, mailbox):
    asker = _account(client, mailbox, "shy@example.com", "shyasker")
    helper = _account(client, mailbox, "kind@example.com", "kindhelper")
    post = _post(client, asker, anonymous=True)
    answer = client.post(f"/api/v1/community/posts/{post['id']}/answers", headers=helper,
                         json={"body": "Take the Malaysia offering."}).json()
    client.post(f"/api/v1/community/answers/{answer['id']}/accept", headers=asker)
    note = client.get("/api/v1/notifications", headers=helper).json()["results"][0]
    assert note["kind"] == "accepted" and note["actor"] is None


# --- deleting your own words ---------------------------------------------------------

def test_an_author_can_delete_their_post_and_a_moderator_cannot_undo_it(client, db, mailbox):
    from app.models.user import User

    author = _account(client, mailbox, "regret@example.com", "regret")
    other = _account(client, mailbox, "other@example.com", "otherone")
    post = _post(client, author)

    assert client.delete(f"/api/v1/community/posts/{post['id']}", headers=other).status_code == 403
    assert client.delete(f"/api/v1/community/posts/{post['id']}", headers=author).status_code == 200
    assert client.get(f"/api/v1/community/posts/{post['id']}").status_code == 404

    db.query(User).filter(User.nickname == "otherone").update({"is_admin": True})
    db.commit()
    unhide = client.post(f"/api/v1/community/moderate/post/{post['id']}",
                         params={"action": "unhide"}, headers=other)
    assert unhide.status_code == 409


def test_deleting_a_reply_keeps_the_replies_under_it(client, db, mailbox):
    asker = _account(client, mailbox, "q@example.com", "questioner")
    first = _account(client, mailbox, "a@example.com", "answerer")
    second = _account(client, mailbox, "b@example.com", "replier")
    post = _post(client, asker)
    answer = client.post(f"/api/v1/community/posts/{post['id']}/answers", headers=first,
                         json={"body": "My email is me@example.com, message me"}).json()
    client.post(f"/api/v1/community/posts/{post['id']}/answers", headers=second,
                json={"body": "Agreed with the above", "parent_id": answer["id"]})
    client.post(f"/api/v1/community/answers/{answer['id']}/accept", headers=asker)

    assert client.delete(f"/api/v1/community/answers/{answer['id']}",
                         headers=first).status_code == 200
    thread = client.get(f"/api/v1/community/posts/{post['id']}").json()
    placeholder = thread["answers"][0]
    assert placeholder["deleted"] is True
    assert placeholder["body"] is None and placeholder["author"] is None
    assert "me@example.com" not in str(thread)
    assert placeholder["replies"][0]["body"] == "Agreed with the above"
    assert thread["is_solved"] is False
    assert thread["answer_count"] == 1


def test_a_deleted_reply_with_nothing_under_it_disappears(client, db, mailbox):
    asker = _account(client, mailbox, "q2@example.com", "questioner2")
    first = _account(client, mailbox, "a2@example.com", "answerer2")
    post = _post(client, asker)
    answer = client.post(f"/api/v1/community/posts/{post['id']}/answers", headers=first,
                         json={"body": "Wrong thread, sorry"}).json()
    client.delete(f"/api/v1/community/answers/{answer['id']}", headers=first)
    assert client.get(f"/api/v1/community/posts/{post['id']}").json()["answers"] == []
    assert client.get(f"/api/v1/community/posts/{post['id']}/answers").json()["results"] == []


# --- forum integrity -----------------------------------------------------------------

def test_voting_on_a_hidden_post_is_refused(client, db, mailbox):
    author = _account(client, mailbox, "h@example.com", "hiddenauthor")
    voter = _account(client, mailbox, "v@example.com", "voter")
    post = _post(client, author)
    client.delete(f"/api/v1/community/posts/{post['id']}", headers=author)
    voted = client.post("/api/v1/community/vote", headers=voter,
                        params={"target_type": "post", "target_id": post["id"]})
    assert voted.status_code == 404
    saved = client.post(f"/api/v1/community/bookmarks/{post['id']}", headers=voter)
    assert saved.status_code == 404


def test_a_search_inside_a_category_stays_inside_it(client, db, mailbox):
    auth = _account(client, mailbox, "c@example.com", "categorised")
    _post(client, auth, title="Parking near Clayton?", category="campus-life")
    _post(client, auth, title="Parking in Malaysia campus?", category="malaysia")
    body = client.get("/api/v1/community/posts",
                      params={"q": "parking", "category": "malaysia"}).json()
    assert [p["title"] for p in body["results"]] == ["Parking in Malaysia campus?"]


@pytest.mark.parametrize("unit_code", ["DROP TABLE", "FIT", "12345678"])
def test_a_post_unit_code_must_be_a_unit_code(client, db, mailbox, unit_code):
    auth = _account(client, mailbox, "u@example.com", "unitposter")
    response = client.post("/api/v1/community/posts", headers=auth, json={
        "title": "A question", "body": "With some detail in it", "category": "units",
        "unit_code": unit_code,
    })
    assert response.status_code == 422


def test_a_unit_code_is_tidied_not_refused(client, db, mailbox):
    auth = _account(client, mailbox, "u2@example.com", "unitposter2")
    assert _post(client, auth, unit_code="fit 2004")["unit_code"] == "FIT2004"


def test_a_blank_title_padded_with_spaces_is_refused(client, db, mailbox):
    auth = _account(client, mailbox, "s@example.com", "spacer")
    response = client.post("/api/v1/community/posts", headers=auth, json={
        "title": "      ", "body": "            ", "category": "units"})
    assert response.status_code == 422


def test_the_same_tag_twice_does_not_break_the_post(client, db, mailbox):
    auth = _account(client, mailbox, "t@example.com", "tagger")
    post = _post(client, auth, tags=["FIT2004", "fit2004", "  fit2004 "])
    assert post["tags"] == ["fit2004"]


@pytest.mark.parametrize(
    "path", ["/api/v1/community/posts?offset=-1", "/api/v1/units?limit=0",
             "/api/v1/guides?offset=-5", "/api/v1/official/search?limit=-1"],
)
def test_a_negative_page_is_a_validation_error_not_a_crash(client, db, path):
    assert client.get(path).status_code == 422


def test_a_renamed_nickname_is_folded_like_a_registered_one(client, db, mailbox):
    _account(client, mailbox, "w1@example.com", "waldo")
    other = _account(client, mailbox, "w2@example.com", "someone")
    response = client.patch("/api/v1/profile", headers=other, json={"nickname": "ｗaldo"})
    assert response.status_code == 409


# --- configuration -------------------------------------------------------------------

@pytest.mark.parametrize(
    "key,bad",
    [("dev-only-not-a-secret-change-in-production-0001", True),
     ("change-me-openssl-rand-hex-32", True),
     ("short", True),
     ("f" * 64, False)],
)
def test_production_refuses_a_placeholder_secret(key, bad):
    from app.core.config import Settings

    assert (Settings(secret_key=key).secret_key_problem() is not None) is bad
