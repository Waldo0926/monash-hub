"""Email verification codes.

Six digits, ten minutes, five guesses. Only an HMAC of the code is stored, so a
database dump does not hand anyone a usable code, and comparisons are constant
time.

The endpoints that use this must answer identically whether or not the address
belongs to an account. Registration and password reset are both places where a
helpful "no such user" tells a stranger who has an account here.
"""
from __future__ import annotations

import hmac
import secrets
from datetime import UTC, datetime, timedelta
from hashlib import sha256

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.email import Emailer, Message
from app.models.user import EmailVerificationCode

REGISTRATION = "registration"
PASSWORD_RESET = "password_reset"
PURPOSES = (REGISTRATION, PASSWORD_RESET)


class VerificationError(Exception):
    """The code was wrong, expired, already used, or out of attempts."""


class RateLimited(Exception):
    """Too many codes requested for this address."""

    def __init__(self, retry_after_seconds: int) -> None:
        super().__init__("Too many requests")
        self.retry_after_seconds = retry_after_seconds


def _digest(code: str, email: str) -> str:
    """Keyed digest, bound to the address so a code cannot be replayed elsewhere."""
    settings = get_settings()
    return hmac.new(
        settings.secret_key.encode("utf-8"),
        f"{email.lower()}:{code}".encode(),
        sha256,
    ).hexdigest()


def _now() -> datetime:
    return datetime.now(UTC)


def issue(db: Session, email: str, purpose: str) -> tuple[int, int]:
    """Create and send a code. Returns ``(ttl_seconds, resend_after_seconds)``.

    Raises :class:`RateLimited` when the address has asked too often. Callers
    must still answer the client neutrally.
    """
    if purpose not in PURPOSES:
        raise ValueError(f"unknown purpose: {purpose}")

    settings = get_settings()
    email = email.strip().lower()
    now = _now()

    latest = db.scalar(
        select(EmailVerificationCode)
        .where(EmailVerificationCode.email == email, EmailVerificationCode.purpose == purpose)
        .order_by(EmailVerificationCode.id.desc())
        .limit(1)
    )
    if latest is not None:
        since = (now - latest.created_at).total_seconds()
        if since < settings.verification_resend_interval_seconds:
            raise RateLimited(int(settings.verification_resend_interval_seconds - since) + 1)

    window_start = now - timedelta(seconds=settings.verification_send_window_seconds)
    recent = db.scalar(
        select(func.count(EmailVerificationCode.id)).where(
            EmailVerificationCode.email == email,
            EmailVerificationCode.created_at >= window_start,
        )
    ) or 0
    if recent >= settings.verification_send_max_per_window:
        raise RateLimited(settings.verification_send_window_seconds)

    # Any code still outstanding for this address and purpose is retired, so a
    # new request always means exactly one live code.
    for row in db.scalars(
        select(EmailVerificationCode).where(
            EmailVerificationCode.email == email,
            EmailVerificationCode.purpose == purpose,
            EmailVerificationCode.consumed_at.is_(None),
        )
    ):
        row.consumed_at = now

    code = f"{secrets.randbelow(1_000_000):06d}"
    db.add(
        EmailVerificationCode(
            email=email,
            purpose=purpose,
            code_digest=_digest(code, email),
            max_attempts=settings.verification_max_attempts,
            expires_at=now + timedelta(seconds=settings.verification_code_ttl_seconds),
        )
    )
    db.commit()

    minutes = max(1, settings.verification_code_ttl_seconds // 60)
    Emailer(settings).send(
        Message(
            to=email,
            subject=_subject(purpose),
            text=_body(purpose, code, minutes),
        )
    )
    return settings.verification_code_ttl_seconds, settings.verification_resend_interval_seconds


def verify(db: Session, email: str, purpose: str, code: str) -> None:
    """Consume a code, or raise :class:`VerificationError`.

    Every failure raises the same exception with the same message. Telling the
    caller apart "expired" from "wrong" from "no code was ever sent" would let
    someone map which addresses have pending signups.
    """
    email = email.strip().lower()
    code = (code or "").strip()
    now = _now()

    row = db.scalar(
        select(EmailVerificationCode)
        .where(
            EmailVerificationCode.email == email,
            EmailVerificationCode.purpose == purpose,
            EmailVerificationCode.consumed_at.is_(None),
        )
        .order_by(EmailVerificationCode.id.desc())
        .limit(1)
    )
    if row is None or row.expires_at <= now or row.attempt_count >= row.max_attempts:
        raise VerificationError("That code is not valid")

    row.attempt_count += 1
    if not hmac.compare_digest(row.code_digest, _digest(code, email)):
        db.commit()
        raise VerificationError("That code is not valid")

    row.consumed_at = now
    db.commit()


def prune(db: Session, older_than_days: int = 30) -> int:
    """Drop codes old enough that no rate-limit window still counts them."""
    cutoff = _now() - timedelta(days=older_than_days)
    rows = db.scalars(
        select(EmailVerificationCode).where(EmailVerificationCode.created_at < cutoff)
    ).all()
    for row in rows:
        db.delete(row)
    db.commit()
    return len(rows)


def _subject(purpose: str) -> str:
    return {
        REGISTRATION: "Your Monash Hub verification code",
        PASSWORD_RESET: "Reset your Monash Hub password",
    }[purpose]


def _body(purpose: str, code: str, minutes: int) -> str:
    action = {
        REGISTRATION: "create your Monash Hub account",
        PASSWORD_RESET: "reset your Monash Hub password",
    }[purpose]
    return (
        f"Your Monash Hub verification code is:\n\n"
        f"    {code}\n\n"
        f"Enter it to {action}. It expires in {minutes} minutes.\n\n"
        "If you did not ask for this, you can ignore this email - nothing has "
        "changed on your account.\n\n"
        "Monash Hub is an independent student platform and is not affiliated "
        "with Monash University.\n"
        "https://monashhub.secureview.tech\n"
    )
