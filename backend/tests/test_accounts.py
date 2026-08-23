"""Registration, sign-in and password recovery.

The security-relevant behaviour here is what the endpoints *do not* say. A
student forum where a stranger can probe which email addresses have accounts is
a worse product, so these tests assert on the silence as much as the success.
"""
from __future__ import annotations

import pytest
from app.core.security import password_problem

PASSWORD = "Correct-Horse-9"


def _request_code(client, email: str, purpose: str = "registration"):
    return client.post(
        "/api/v1/auth/verification-code", json={"email": email, "purpose": purpose}
    )


def _make_account(db, email: str, nickname: str):
    """An account that never went through the code endpoint.

    Registering through the API spends the address's rate-limit budget, which
    makes it useless for comparing a known address against an unknown one - the
    known one is already throttled before the comparison starts.
    """
    from app.core.security import hash_password
    from app.models.user import User

    db.add(User(email=email, nickname=nickname, password_hash=hash_password(PASSWORD)))
    db.commit()


def _register(client, mailbox, email: str, nickname: str, password: str = PASSWORD):
    _request_code(client, email)
    return client.post(
        "/api/v1/auth/signup",
        json={
            "email": email,
            "nickname": nickname,
            "password": password,
            "verification_code": mailbox.code_for(email),
        },
    )


# --- registration ---------------------------------------------------------

def test_registration_needs_a_code_from_the_email(client, db, mailbox):
    response = _register(client, mailbox, "new@example.com", "newcomer")
    assert response.status_code == 201
    body = response.json()
    assert body["user"]["nickname"] == "newcomer"
    assert body["token"]


def test_registration_without_a_valid_code_is_refused(client, db, mailbox):
    _request_code(client, "new@example.com")
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "new@example.com",
            "nickname": "newcomer",
            "password": PASSWORD,
            "verification_code": "000000",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "That code is not valid"


def test_a_code_cannot_be_used_twice(client, db, mailbox):
    assert _register(client, mailbox, "twice@example.com", "twice").status_code == 201
    replay = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "twice@example.com",
            "nickname": "twice2",
            "password": PASSWORD,
            "verification_code": mailbox.code_for("twice@example.com"),
        },
    )
    assert replay.status_code == 400


def test_a_code_is_bound_to_its_purpose(client, db, mailbox):
    _request_code(client, "purpose@example.com", "registration")
    code = mailbox.code_for("purpose@example.com")
    # Registered, so a reset code would be issued - but the registration code
    # must not stand in for one.
    assert _register(client, mailbox, "purpose@example.com", "purposeful").status_code == 201
    reset = client.post(
        "/api/v1/auth/password-reset",
        json={"email": "purpose@example.com", "verification_code": code, "password": "Another-Pass-9"},
    )
    assert reset.status_code == 400


def test_requesting_a_code_never_reveals_whether_the_account_exists(client, db, mailbox):
    """Same status, same body, same number of emails, same throttling.

    The last one matters as much as the rest. While a taken address was skipped
    outright it never touched the rate limiter, so it never got a 429 - and
    "this address is never throttled" is exactly the answer the endpoint is not
    supposed to give.
    """
    _make_account(db, "known@example.com", "known")

    before = len(mailbox.messages)
    taken = _request_code(client, "known@example.com")
    free = _request_code(client, "stranger@example.com")

    assert taken.status_code == free.status_code == 200
    assert taken.json() == free.json()
    recipients = [m.to for m in mailbox.messages[before:]]
    assert recipients == ["known@example.com", "stranger@example.com"]

    # Immediately again: both throttled, identically.
    assert _request_code(client, "known@example.com").status_code == 429
    assert _request_code(client, "stranger@example.com").status_code == 429


def test_a_second_code_request_is_rate_limited(client, db, mailbox):
    assert _request_code(client, "fast@example.com").status_code == 200
    again = _request_code(client, "fast@example.com")
    assert again.status_code == 429
    assert "Retry-After" in again.headers


def test_duplicate_nickname_is_reported_only_after_the_code_proves_the_address(
    client, db, mailbox
):
    assert _register(client, mailbox, "first@example.com", "sharedname").status_code == 201
    clash = _register(client, mailbox, "second@example.com", "sharedname")
    assert clash.status_code == 409
    assert clash.json()["detail"] == "That nickname is taken."


def test_lookalike_nicknames_do_not_become_separate_accounts(client, db, mailbox):
    assert _register(client, mailbox, "wide@example.com", "student").status_code == 201
    # Full-width characters normalise to the same nickname.
    clash = _register(client, mailbox, "wide2@example.com", "ｓｔｕｄｅｎｔ")
    assert clash.status_code == 409


@pytest.mark.parametrize(
    "nickname", ["ab", "has space", "a" * 49, "semi;colon", "sla/sh"]
)
def test_invalid_nicknames_are_refused(client, db, mailbox, nickname):
    response = _register(client, mailbox, f"{abs(hash(nickname))}@example.com", nickname)
    assert response.status_code in (409, 422)


# --- password policy ------------------------------------------------------

@pytest.mark.parametrize(
    "password,reason",
    [
        ("short1A", "too short"),
        ("alllowercase", "one character class"),
        ("1234567890", "one character class"),
    ],
)
def test_weak_passwords_are_refused(password, reason):
    assert password_problem(password) is not None, reason


def test_password_cannot_be_built_from_the_account_details():
    assert password_problem("newcomer-1234", ["newcomer", "new@example.com"]) is not None


def test_a_reasonable_password_passes():
    assert password_problem("Correct-Horse-9", ["someone", "a@example.com"]) is None


def test_signup_rejects_a_weak_password(client, db, mailbox):
    response = _register(client, mailbox, "weak@example.com", "weakling", password="password")
    assert response.status_code == 422


# --- sign in and reset ----------------------------------------------------

def test_sign_in_and_me(client, db, mailbox):
    _register(client, mailbox, "signin@example.com", "signer")
    signed = client.post(
        "/api/v1/auth/signin", json={"email": "signin@example.com", "password": PASSWORD}
    )
    assert signed.status_code == 200
    token = signed.json()["token"]
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["nickname"] == "signer"


def test_wrong_password_and_unknown_email_look_identical(client, db, mailbox):
    _register(client, mailbox, "victim@example.com", "victim")
    wrong = client.post(
        "/api/v1/auth/signin", json={"email": "victim@example.com", "password": "Wrong-Pass-9"}
    )
    unknown = client.post(
        "/api/v1/auth/signin", json={"email": "nobody@example.com", "password": "Wrong-Pass-9"}
    )
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()


def test_password_reset_signs_other_sessions_out(client, db, mailbox):
    old_token = _register(client, mailbox, "reset@example.com", "resetter").json()["token"]
    assert client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {old_token}"}
    ).status_code == 200

    _request_code(client, "reset@example.com", "password_reset")
    reset = client.post(
        "/api/v1/auth/password-reset",
        json={
            "email": "reset@example.com",
            "verification_code": mailbox.code_for("reset@example.com"),
            "password": "Brand-New-Pass-7",
        },
    )
    assert reset.status_code == 200
    assert reset.json()["other_sessions_signed_out"] is True

    # The token issued before the reset is no longer a session.
    assert client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {old_token}"}
    ).status_code == 401
    # The one handed back by the reset is.
    new_token = reset.json()["token"]
    assert client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {new_token}"}
    ).status_code == 200
    # And the new password is the one that works.
    assert client.post(
        "/api/v1/auth/signin",
        json={"email": "reset@example.com", "password": "Brand-New-Pass-7"},
    ).status_code == 200
    assert client.post(
        "/api/v1/auth/signin", json={"email": "reset@example.com", "password": PASSWORD}
    ).status_code == 401


def test_reset_code_is_not_issued_for_an_unknown_address(client, db, mailbox):
    assert _request_code(client, "ghost@example.com", "password_reset").status_code == 200
    with pytest.raises(AssertionError):
        mailbox.code_for("ghost@example.com")


# --- a code request always produces an email ------------------------------
#
# The endpoint stays uninformative; the inbox does not. Sending nothing at all
# is indistinguishable from a broken mail provider, and that ambiguity is what
# makes "I never got the code" unanswerable.

def _last_message(mailbox, address: str):
    for message in reversed(mailbox.messages):
        if message.to.lower() == address.lower():
            return message
    raise AssertionError(f"nothing was sent to {address}")


def test_registering_an_address_that_already_has_an_account_still_emails(client, db, mailbox):
    _make_account(db, "taken@example.com", "taken")
    before = len(mailbox.messages)

    assert _request_code(client, "taken@example.com").status_code == 200

    assert len(mailbox.messages) == before + 1, "a second request must still send something"
    message = _last_message(mailbox, "taken@example.com")
    assert "already have" in message.subject.lower()
    # And nothing in it can be mistaken for a code to type in.
    with pytest.raises(AssertionError):
        mailbox.code_for("taken@example.com")


def test_reset_for_an_unknown_address_still_emails(client, db, mailbox):
    assert _request_code(client, "ghost2@example.com", "password_reset").status_code == 200
    message = _last_message(mailbox, "ghost2@example.com")
    assert "no monash hub account" in message.subject.lower()


def test_a_dead_end_code_can_never_be_redeemed(client, db, mailbox):
    """The row is written so rate limiting behaves the same, not so it works."""
    from app.core import verification

    _make_account(db, "settled@example.com", "settled")
    _request_code(client, "settled@example.com")

    for guess in ("000000", "123456"):
        with pytest.raises(verification.VerificationError):
            verification.verify(db, "settled@example.com", verification.REGISTRATION, guess)


# --- password length ------------------------------------------------------

def test_eight_characters_with_two_classes_is_enough():
    """The floor is 8. Pinned because it moved once and the four locales,
    the browser copy and the server copy all have to agree on the number."""
    assert password_problem("Abcdef-1") is None
    assert password_problem("Abcde-1") is not None
