"""Signing in with Google.

Two things carry the security of this flow, and both are tested here rather
than trusted: the signature on the `state` parameter, and the refusal to accept
an address Google has not verified. Accounts are matched by email, so the second
one is the difference between a convenience and a way into somebody else's
account.
"""
from __future__ import annotations

import base64
import json
import time

import pytest
from app.core import google_oauth
from app.core.config import get_settings
from app.core.security import hash_password
from app.models.user import User


def _identity(email="waldo@example.com", verified=True, name="Waldo Wen"):
    return google_oauth.GoogleIdentity(
        email=email, email_verified=verified, name=name, subject="12345"
    )


@pytest.fixture
def configured(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "google_client_id", "test-client-id", raising=False)
    monkeypatch.setattr(settings, "google_client_secret", "test-secret", raising=False)
    return settings


# --- the state parameter --------------------------------------------------

def test_a_state_we_issued_round_trips():
    assert google_oauth.read_state(google_oauth.issue_state("/plan")) == "/plan"


def test_a_state_we_did_not_issue_is_refused():
    """Without this, a crafted callback URL completes a sign-in the person
    never started."""
    forged = json.dumps({"n": "x", "exp": int(time.time()) + 600, "next": "/"})
    encoded = base64.urlsafe_b64encode(forged.encode()).decode().rstrip("=")
    for state in (f"{encoded}.{encoded}", encoded, "", "not-a-state", f"{encoded}."):
        with pytest.raises(google_oauth.GoogleAuthError):
            google_oauth.read_state(state)


def test_a_tampered_state_is_refused():
    """The payload and the signature must agree, not merely both be present."""
    good = google_oauth.issue_state("/plan")
    payload, signature = good.split(".", 1)
    swapped = json.dumps({"n": "x", "exp": int(time.time()) + 600, "next": "/evil"})
    other = base64.urlsafe_b64encode(swapped.encode()).decode().rstrip("=")
    with pytest.raises(google_oauth.GoogleAuthError):
        google_oauth.read_state(f"{other}.{signature}")
    assert payload  # the original halves are what a real one is made of


def test_an_expired_state_is_refused(monkeypatch):
    monkeypatch.setattr(google_oauth, "STATE_TTL_SECONDS", -1)
    with pytest.raises(google_oauth.GoogleAuthError, match="expired"):
        google_oauth.read_state(google_oauth.issue_state("/"))


# --- reading the identity -------------------------------------------------

def _id_token(claims: dict) -> str:
    def part(data):
        return base64.urlsafe_b64encode(json.dumps(data).encode()).decode().rstrip("=")
    return f"{part({'alg': 'RS256'})}.{part(claims)}.signature-not-checked"


def test_an_id_token_for_another_client_is_refused(configured):
    """A token minted for a different application must not sign anyone in."""
    token = _id_token({
        "iss": "https://accounts.google.com", "aud": "somebody-elses-client",
        "email": "waldo@example.com", "email_verified": True,
    })
    with pytest.raises(google_oauth.GoogleAuthError, match="different client"):
        google_oauth._identity_from(token, configured)


def test_an_id_token_from_another_issuer_is_refused(configured):
    token = _id_token({
        "iss": "https://evil.example", "aud": "test-client-id",
        "email": "waldo@example.com", "email_verified": True,
    })
    with pytest.raises(google_oauth.GoogleAuthError, match="issuer"):
        google_oauth._identity_from(token, configured)


def test_email_verified_is_read_as_a_string_or_a_boolean(configured):
    """Google sends it both ways depending on the endpoint."""
    for value, expected in ((True, True), ("true", True), (False, False), ("false", False)):
        token = _id_token({
            "iss": "accounts.google.com", "aud": "test-client-id",
            "email": "waldo@example.com", "email_verified": value,
        })
        assert google_oauth._identity_from(token, configured).email_verified is expected


# --- the endpoints --------------------------------------------------------

def test_the_button_is_not_offered_when_it_is_not_configured(client):
    assert client.get("/api/v1/auth/google/start").status_code == 503


def test_start_returns_an_authorize_url(client, configured):
    body = client.get("/api/v1/auth/google/start", params={"next": "/plan"}).json()
    assert body["url"].startswith(google_oauth.AUTHORIZE_URL)
    assert "test-client-id" in body["url"]
    assert "select_account" in body["url"]


def test_start_refuses_to_carry_an_absolute_next(client, configured):
    """A `next` from a query string is somebody else's input; an open redirect
    is exactly what it would buy them."""
    for hostile in ("https://evil.example", "//evil.example"):
        body = client.get("/api/v1/auth/google/start", params={"next": hostile}).json()
        # The state is what carries `next`, so read it back rather than the URL.
        state = body["url"].split("state=")[1].split("&")[0]
        assert google_oauth.read_state(state) == "/"


def _callback(client, monkeypatch, identity, state=None):
    monkeypatch.setattr(google_oauth, "exchange", lambda code, settings=None: identity)
    return client.get(
        "/api/v1/auth/google/callback",
        params={"code": "abc", "state": state or google_oauth.issue_state("/plan")},
        follow_redirects=False,
    )


def test_an_unverified_address_is_refused(client, db, configured, monkeypatch):
    """The whole flow matches accounts by email. An unverified address would be
    a way into somebody else's account."""
    response = _callback(client, monkeypatch, _identity(verified=False))
    assert response.status_code == 303
    assert "google=unverified" in response.headers["location"]
    assert db.query(User).count() == 0


def test_a_first_sign_in_creates_an_account(client, db, configured, monkeypatch):
    response = _callback(client, monkeypatch, _identity())
    assert response.status_code == 303
    location = response.headers["location"]
    # The token rides in the fragment, which never reaches a server log.
    assert "/auth/google#token=" in location
    assert "?token=" not in location

    created = db.query(User).one()
    assert created.email == "waldo@example.com"
    # Nicknames allow no spaces, so the Google name is cleaned rather than
    # discarded - the person is still recognisable.
    assert created.nickname == "WaldoWen"


def test_signing_in_again_reuses_the_same_account(client, db, configured, monkeypatch):
    _callback(client, monkeypatch, _identity())
    _callback(client, monkeypatch, _identity())
    assert db.query(User).count() == 1


def test_google_signs_into_an_existing_password_account(client, db, configured, monkeypatch):
    """Same address, same person - Google has verified it, so this is a linked
    identity rather than a second account."""
    existing = User(
        email="waldo@example.com", nickname="Waldo",
        password_hash=hash_password("Correct-Horse-9"), is_active=True,
    )
    db.add(existing)
    db.commit()

    response = _callback(client, monkeypatch, _identity())
    assert response.status_code == 303
    assert db.query(User).count() == 1
    db.refresh(existing)
    assert existing.nickname == "Waldo", "an existing account keeps its own name"


def test_a_suspended_account_cannot_come_in_through_google(client, db, configured, monkeypatch):
    db.add(User(email="waldo@example.com", nickname="Waldo",
                password_hash=hash_password("Correct-Horse-9"), is_active=False))
    db.commit()
    response = _callback(client, monkeypatch, _identity())
    assert "google=suspended" in response.headers["location"]


def test_a_clashing_nickname_still_gets_an_account(client, db, configured, monkeypatch):
    db.add(User(email="someone@example.com", nickname="WaldoWen",
                password_hash=hash_password("Correct-Horse-9"), is_active=True))
    db.commit()

    _callback(client, monkeypatch, _identity(email="new@example.com"))
    created = db.query(User).filter(User.email == "new@example.com").one()
    assert created.nickname != "WaldoWen"
    assert created.nickname.startswith("WaldoWen")


def test_a_google_account_cannot_be_signed_into_with_a_password(
    client, db, configured, monkeypatch
):
    """The placeholder hash must never match something a person could type."""
    _callback(client, monkeypatch, _identity())
    for attempt in ("", " ", "password", "google"):
        response = client.post(
            "/api/v1/auth/signin",
            json={"email": "waldo@example.com", "password": attempt},
        )
        assert response.status_code == 401


def test_cancelling_at_google_comes_back_without_an_account(client, db, configured):
    response = client.get(
        "/api/v1/auth/google/callback",
        params={"error": "access_denied", "state": google_oauth.issue_state("/")},
        follow_redirects=False,
    )
    assert "google=cancelled" in response.headers["location"]
    assert db.query(User).count() == 0


def test_a_forged_callback_creates_nothing(client, db, configured, monkeypatch):
    response = _callback(client, monkeypatch, _identity(), state="forged.state")
    assert "google=failed" in response.headers["location"]
    assert db.query(User).count() == 0
