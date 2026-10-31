"""Verification codes: what an attempt costs, and when the budget is spent."""
from __future__ import annotations

import pytest
from app.core import email as email_module
from app.core import throttle, verification
from app.core.config import get_settings
from app.models.user import EmailVerificationCode

PASSWORD = "Correct-Horse-9"


def _register(client, mailbox, email: str, nickname: str):
    client.post("/api/v1/auth/verification-code", json={"email": email, "purpose": "registration"})
    response = client.post("/api/v1/auth/signup", json={
        "email": email, "nickname": nickname, "password": PASSWORD,
        "verification_code": mailbox.code_for(email),
    })
    assert response.status_code == 201, response.text


def _attempts(db, email: str) -> int:
    row = db.query(EmailVerificationCode).filter(
        EmailVerificationCode.email == email,
        EmailVerificationCode.consumed_at.is_(None),
    ).one()
    db.refresh(row)
    return row.attempt_count


def test_the_right_code_on_the_last_attempt_resets_the_password(client, db, mailbox):
    """Four wrong guesses, then the real code: a reset, not a 500.

    The reset checks the code once before the nickname rule and once to spend
    it. Both used to count, so the fifth attempt passed the first check and
    was refused by the second, uncaught.
    """
    _register(client, mailbox, "last@example.com", "lastchance")
    client.post("/api/v1/auth/verification-code",
                json={"email": "last@example.com", "purpose": "password_reset"})
    limit = get_settings().verification_max_attempts
    for _ in range(limit - 1):
        wrong = client.post("/api/v1/auth/password-reset", json={
            "email": "last@example.com", "verification_code": "000000",
            "password": "Brand-New-Pass-7",
        })
        assert wrong.status_code == 400
    right = client.post("/api/v1/auth/password-reset", json={
        "email": "last@example.com", "verification_code": mailbox.code_for("last@example.com"),
        "password": "Brand-New-Pass-7",
    })
    assert right.status_code == 200, right.text


def test_a_check_and_its_consume_cost_one_attempt(client, db, mailbox):
    client.post("/api/v1/auth/verification-code",
                json={"email": "once@example.com", "purpose": "registration"})
    code = mailbox.code_for("once@example.com")

    verification.verify(db, "once@example.com", verification.REGISTRATION, code, consume=False)
    assert _attempts(db, "once@example.com") == 0
    with pytest.raises(verification.VerificationError):
        verification.verify(db, "once@example.com", verification.REGISTRATION, "000000")
    assert _attempts(db, "once@example.com") == 1
    verification.verify(db, "once@example.com", verification.REGISTRATION, code)
    with pytest.raises(verification.VerificationError):
        verification.verify(db, "once@example.com", verification.REGISTRATION, code)


def test_the_attempt_cap_holds_whatever_the_object_in_memory_says(client, db, mailbox):
    """The cap is enforced by the UPDATE, not by a count read earlier."""
    client.post("/api/v1/auth/verification-code",
                json={"email": "cap@example.com", "purpose": "registration"})
    limit = get_settings().verification_max_attempts
    for _ in range(limit):
        with pytest.raises(verification.VerificationError):
            verification.verify(db, "cap@example.com", verification.REGISTRATION, "000000")
    assert _attempts(db, "cap@example.com") == limit
    with pytest.raises(verification.VerificationError):
        verification.verify(db, "cap@example.com", verification.REGISTRATION,
                            mailbox.code_for("cap@example.com"))


def test_an_email_that_never_went_out_does_not_spend_the_resend_interval(client, db, monkeypatch):
    calls = {"n": 0}

    def flaky(self, message):
        calls["n"] += 1
        if calls["n"] == 1:
            raise email_module.EmailDeliveryError("provider down")

    monkeypatch.setattr(email_module.Emailer, "send", flaky)
    body = {"email": "retry@example.com", "purpose": "registration"}
    assert client.post("/api/v1/auth/verification-code", json=body).status_code == 503
    assert client.post("/api/v1/auth/verification-code", json=body).status_code == 200


# --- whose address is it -------------------------------------------------------

class _Request:
    def __init__(self, peer: str, real_ip: str | None):
        self.headers = {"x-real-ip": real_ip} if real_ip else {}
        self.client = type("Client", (), {"host": peer})()


def test_x_real_ip_is_believed_only_from_a_trusted_proxy(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "trusted_proxies", "127.0.0.1, 172.16.0.0/12", raising=False)
    assert throttle.client_address(_Request("127.0.0.1", "203.0.113.9")) == "203.0.113.9"
    assert throttle.client_address(_Request("172.18.0.1", "203.0.113.9")) == "203.0.113.9"
    assert throttle.client_address(_Request("198.51.100.1", "203.0.113.9")) == "198.51.100.1"
    assert throttle.client_address(_Request("testclient", "203.0.113.9")) == "testclient"


def test_every_peer_is_trusted_when_no_proxy_is_configured(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "trusted_proxies", "", raising=False)
    assert throttle.client_address(_Request("testclient", "203.0.113.9")) == "203.0.113.9"
