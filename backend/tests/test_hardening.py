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


@pytest.mark.parametrize(
    "body",
    [{"year": "next", "entries": []},
     {"entries": ["FIT1045"]},
     {"entries": [{"unit_code": "FIT1045", "year": "soon", "teaching_period": "S1"}]},
     {"entries": [{"unit_code": "FIT1045", "year": 2026, "teaching_period": "S1"}] * 81}],
)
def test_a_malformed_plan_is_a_422_not_a_500(client, db, body):
    assert client.post("/api/v1/plan/check", json=body).status_code == 422


def test_a_plan_without_a_year_is_checked_against_the_current_handbook(client, db):
    body = client.post("/api/v1/plan/check", json={"entries": []}).json()
    assert body["academic_year"] == 2026


def test_a_page_dropped_from_the_seed_list_is_retired(db, engine, monkeypatch):
    from app.models.knowledge import OfficialPage
    from sqlalchemy import select
    from sqlalchemy.orm import sessionmaker

    from crawler.official import run
    from crawler.official.seeds import SEEDS

    monkeypatch.setattr(run, "SessionLocal", sessionmaker(bind=engine))
    run.register(SEEDS[:3])
    run.register(SEEDS[:2], retire_others=True)
    statuses = dict(db.execute(select(OfficialPage.slug, OfficialPage.status)).all())
    assert statuses[SEEDS[2].slug] == "retired"
    assert statuses[SEEDS[0].slug] != "retired"

    # A --slugs run must not retire what it was not asked about.
    run.register(SEEDS[:1])
    db.expire_all()
    statuses = dict(db.execute(select(OfficialPage.slug, OfficialPage.status)).all())
    assert statuses[SEEDS[1].slug] != "retired"


# --- closing an account --------------------------------------------------------

def test_closing_an_account_removes_what_identifies_you(client, db, mailbox):
    from app.models.user import User

    leaver = _account(client, mailbox, "leaver@example.com", "leaver")
    other = _account(client, mailbox, "stayer@example.com", "stayer")
    post = _post(client, leaver)
    client.post(f"/api/v1/community/posts/{post['id']}/answers", headers=other,
                json={"body": "Here is an answer"})
    answer = client.post(f"/api/v1/community/posts/{post['id']}/answers", headers=leaver,
                         json={"body": "Thanks, that helped"}).json()
    other_post = _post(client, other, title="Another question")
    client.post(f"/api/v1/community/posts/{other_post['id']}/answers", headers=leaver,
                json={"body": "I think the answer is yes"})

    wrong = client.request("DELETE", "/api/v1/profile", headers=leaver,
                           json={"password": "not-it-1A"})
    assert wrong.status_code == 403

    closed = client.request("DELETE", "/api/v1/profile", headers=leaver,
                            json={"password": PASSWORD})
    assert closed.status_code == 200

    # Signed out everywhere, and the address is free again.
    assert client.get("/api/v1/auth/me", headers=leaver).status_code == 401
    assert _sign_in(client, "leaver@example.com", PASSWORD).status_code == 401
    _account(client, mailbox, "leaver@example.com", "leaver2")

    # What they wrote stays, with no name on it.
    thread = client.get(f"/api/v1/community/posts/{post['id']}").json()
    assert thread["author"] is None and thread["anonymous"] is True
    mine = next(a for a in thread["answers"] if a["id"] == answer["id"])
    assert mine["author"] is None
    # ...including in the notification the other person already received.
    notes = client.get("/api/v1/notifications", headers=other).json()["results"]
    assert notes and all(n["actor"] != "leaver" for n in notes)

    row = db.query(User).filter(User.nickname.like("deleted-%")).one()
    assert row.is_active is False and row.bio is None and row.avatar_file is None
    assert "leaver" not in row.email


def test_closing_an_account_can_take_its_writing_down_too(client, db, mailbox):
    leaver = _account(client, mailbox, "gone@example.com", "gonegirl")
    other = _account(client, mailbox, "asker2@example.com", "asker2")
    post = _post(client, leaver)
    question = _post(client, other, title="Is FIT1045 hard?")
    reply = client.post(f"/api/v1/community/posts/{question['id']}/answers", headers=leaver,
                        json={"body": "Not really, practise loops"}).json()
    client.post(f"/api/v1/community/answers/{reply['id']}/accept", headers=other)

    client.request("DELETE", "/api/v1/profile", headers=leaver,
                   json={"password": PASSWORD, "delete_content": True})
    assert client.get(f"/api/v1/community/posts/{post['id']}").status_code == 404
    thread = client.get(f"/api/v1/community/posts/{question['id']}").json()
    assert thread["answers"] == []
    assert thread["answer_count"] == 0 and thread["is_solved"] is False


def test_the_closed_account_nickname_pattern_is_reserved(client, db, mailbox):
    client.post("/api/v1/auth/verification-code",
                json={"email": "squat@example.com", "purpose": "registration"})
    response = client.post("/api/v1/auth/signup", json={
        "email": "squat@example.com", "nickname": "deleted-1", "password": PASSWORD,
        "verification_code": mailbox.code_for("squat@example.com")})
    assert response.status_code == 422


# --- reports and the moderation queue --------------------------------------------

def test_reports_are_deduplicated_and_can_be_resolved(client, db, mailbox):
    from app.models.user import User

    author = _account(client, mailbox, "spam@example.com", "spammer")
    reporter = _account(client, mailbox, "rep@example.com", "reporter")
    post = _post(client, author, title="Cheap essays here")
    body = {"target_type": "post", "target_id": post["id"], "reason": "spam",
            "detail": "Advertising"}
    first = client.post("/api/v1/community/reports", headers=reporter, json=body).json()
    again = client.post("/api/v1/community/reports", headers=reporter, json=body).json()
    assert first["id"] == again["id"]

    db.query(User).filter(User.nickname == "reporter").update({"is_admin": True})
    db.commit()
    queue = client.get("/api/v1/community/reports", headers=reporter).json()
    assert queue["total"] == 1
    item = queue["results"][0]
    assert item["target"]["title"] == "Cheap essays here"
    assert item["target"]["post_id"] == post["id"]

    resolved = client.post(f"/api/v1/community/reports/{item['id']}/resolve",
                           params={"action": "hide"}, headers=reporter)
    assert resolved.status_code == 200
    assert client.get(f"/api/v1/community/posts/{post['id']}").status_code == 404
    assert client.get("/api/v1/community/reports", headers=reporter).json()["total"] == 0
    assert client.get("/api/v1/community/reports", params={"status": "resolved"},
                      headers=reporter).json()["total"] == 1


def test_a_report_can_be_dismissed(client, db, mailbox):
    from app.models.user import User

    author = _account(client, mailbox, "fine@example.com", "fineauthor")
    mod = _account(client, mailbox, "mod@example.com", "moderator1")
    post = _post(client, author)
    report = client.post("/api/v1/community/reports", headers=mod, json={
        "target_type": "post", "target_id": post["id"], "reason": "other"}).json()
    db.query(User).filter(User.nickname == "moderator1").update({"is_admin": True})
    db.commit()
    client.post(f"/api/v1/community/reports/{report['id']}/resolve",
                params={"action": "dismiss"}, headers=mod)
    assert client.get(f"/api/v1/community/posts/{post['id']}").status_code == 200
    assert client.get("/api/v1/community/reports", headers=mod).json()["total"] == 0


def test_reports_are_rate_limited(client, db, mailbox):
    author = _account(client, mailbox, "busy@example.com", "busyauthor")
    posts = [_post(client, author, title=f"Question number {i}") for i in range(21)]
    codes = [client.post("/api/v1/community/reports", json={
        "target_type": "post", "target_id": p["id"], "reason": "spam"}).status_code
        for p in posts]
    assert codes[:20] == [201] * 20 and codes[20] == 429


# --- entries Monash withdraws from the Handbook -----------------------------------

def test_a_404_retires_a_unit_and_a_network_error_does_not(db, engine, handbook_html, monkeypatch):
    from app.handbook.parser import parse_unit_page, unit_url
    from app.handbook.repository import upsert_unit
    from app.models.handbook import Unit
    from sqlalchemy.orm import sessionmaker

    from crawler.handbook import run
    from crawler.handbook.fetch import FetchResult

    for code in ("FIT2102", "BFF2140"):
        upsert_unit(db, parse_unit_page(handbook_html(code), unit_url(code, 2026)))
    db.commit()

    answers = {
        "FIT2102": FetchResult(url="", status=404, html=None, error="not found"),
        "BFF2140": FetchResult(url="", status=None, html=None, error="ReadTimeout"),
    }

    class Fetcher:
        def __init__(self, *_):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def fetch(self, url):
            return answers[url.rstrip("/").rsplit("/", 1)[-1]]

    monkeypatch.setattr(run, "SessionLocal", sessionmaker(bind=engine))
    monkeypatch.setattr(run, "HandbookFetcher", Fetcher)
    summary = run.crawl(["FIT2102", "BFF2140"], 2026, min_interval=1.0)
    assert summary["withdrawn"] == 1 and summary["failed"] == 1

    db.expire_all()
    active = {u.unit_code: u.is_active for u in db.query(Unit)}
    assert active == {"FIT2102": False, "BFF2140": True}


def test_rows_the_index_dropped_are_rechecked(db, handbook_html):
    from app.handbook.parser import parse_unit_page, unit_url
    from app.handbook.repository import upsert_unit
    from app.models.handbook import Unit

    from crawler.handbook.withdrawn import recheck_candidates

    for code in ("FIT2102", "BFF2140"):
        upsert_unit(db, parse_unit_page(handbook_html(code), unit_url(code, 2026)))
    db.commit()
    assert recheck_candidates(db, Unit, "unit_code", 2026, ["FIT2102"]) == ["BFF2140"]


def test_a_withdrawn_unit_is_not_answered_for_and_its_page_says_so(client, db, handbook_html):
    from app.handbook.parser import parse_unit_page, unit_url
    from app.handbook.repository import upsert_unit
    from app.models.handbook import Unit

    upsert_unit(db, parse_unit_page(handbook_html("FIT2102"), unit_url("FIT2102", 2026)))
    db.query(Unit).update({"is_active": False})
    db.commit()
    assert client.post("/api/v1/ask", json={"query": "FIT2102 exam"}).json()["answer_type"] \
        == "unit_not_found"
    assert client.get("/api/v1/units/FIT2102").json()["is_active"] is False


def test_next_year_is_published_only_when_the_index_lists_that_year(monkeypatch):
    from crawler.handbook import next_year

    class Response:
        def __init__(self, payload):
            self.payload = payload

        def raise_for_status(self):
            pass

        def json(self):
            return {"data": self.payload}

    payloads = {
        "2027": {"total": 0, "results": []},
        "2026": {"total": 6143, "results": [{"uri": "/2026/units/ACB1020"}]},
        # An index that answers an unpublished year with the current one's
        # entries must not count as that year being out.
        "2028": {"total": 6143, "results": [{"uri": "/2026/units/ACB1020"}]},
    }

    class Client:
        def __init__(self, **_):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def get(self, url, params):
            return Response(payloads[params["siteYear"]])

    monkeypatch.setattr(next_year.httpx, "Client", Client)
    assert next_year.published_entries(2027) == 0
    assert next_year.published_entries(2026) == 6143
    assert next_year.published_entries(2028) == 0


def test_an_alert_without_an_address_is_only_logged(monkeypatch):
    from app.core import notify

    sent = []
    monkeypatch.setattr(notify.Emailer, "send", lambda self, message: sent.append(message))
    monkeypatch.setattr(notify, "get_settings",
                        lambda: type("S", (), {"alert_email": None})())
    assert notify.notify("s", "b") is False and sent == []


def test_an_alert_goes_to_every_listed_address(monkeypatch):
    from app.core import notify

    sent = []
    monkeypatch.setattr(notify.Emailer, "send", lambda self, message: sent.append(message.to))
    monkeypatch.setattr(notify, "get_settings", lambda: type(
        "S", (), {"alert_email": " a@example.com, b@example.com ,"})())
    assert notify.notify("s", "b") is True
    assert sent == ["a@example.com", "b@example.com"]
