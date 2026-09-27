"""Sliding-window limits for the account endpoints, kept in PostgreSQL.

nginx already limits requests per client address, but at one request a second
that is still 86,400 password guesses a day against one account, and a
university's Wi-Fi puts thousands of students behind a handful of addresses -
so a per-address limit strict enough to stop guessing would lock out a lecture
theatre. What protects an account is a limit on the *account*: a few failed
sign-ins for one email, whoever is making them.

The database rather than process memory, because there is more than one worker
and a limit each worker counts on its own is several limits.

Every check here behaves identically for an address with an account and one
without. A lockout only real accounts could hit would tell a stranger which
addresses are registered.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from fastapi import Request
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.user import AuthThrottle

SIGNIN_FAILURE = "signin_failure"
SIGNIN_FAILURE_IP = "signin_failure_ip"
CODE_REQUEST_IP = "code_request_ip"
REPORT = "report"


@dataclass(frozen=True)
class Limit:
    kind: str
    max_events: int
    window_seconds: int


# Ten wrong passwords in fifteen minutes is a person who has forgotten theirs;
# they are pointed at the reset flow. It is also a ceiling of about a thousand
# guesses a day, which is not a way into an account with a real password.
SIGNIN_PER_ACCOUNT = Limit(SIGNIN_FAILURE, 10, 15 * 60)
# Generous, because of shared campus addresses. It exists to stop one machine
# spraying guesses across many accounts, not to stop a busy lecture theatre.
SIGNIN_PER_ADDRESS = Limit(SIGNIN_FAILURE_IP, 100, 15 * 60)
# Codes are already limited per email. This stops one client asking for codes
# to a long list of other people's addresses.
CODES_PER_ADDRESS = Limit(CODE_REQUEST_IP, 30, 60 * 60)
# Reports reach a person, so a flood of them is a way to bury the real ones.
# Keyed by account, or by address for a signed-out reader.
REPORTS_PER_REPORTER = Limit(REPORT, 20, 60 * 60)


class Throttled(Exception):
    def __init__(self, retry_after_seconds: int) -> None:
        super().__init__("Too many attempts")
        self.retry_after_seconds = retry_after_seconds


def client_address(request: Request) -> str:
    """The address nginx saw.

    ``X-Real-IP`` is set by nginx from the connection itself and overwrites
    anything a client sent. ``X-Forwarded-For`` is appended to, so its first
    entry is whatever the client chose to write there.
    """
    real = (request.headers.get("x-real-ip") or "").strip()
    if real:
        return real[:64]
    return (request.client.host if request.client else "unknown")[:64]


def _now() -> datetime:
    return datetime.now(UTC)


def check(db: Session, limit: Limit, key: str) -> None:
    """Raise :class:`Throttled` if ``key`` has used up ``limit``."""
    since = _now() - timedelta(seconds=limit.window_seconds)
    count, oldest = db.execute(
        select(func.count(AuthThrottle.id), func.min(AuthThrottle.created_at)).where(
            AuthThrottle.kind == limit.kind,
            AuthThrottle.key == key,
            AuthThrottle.created_at >= since,
        )
    ).one()
    if (count or 0) >= limit.max_events:
        retry = limit.window_seconds
        if oldest is not None:
            retry = max(1, int((oldest - since).total_seconds()) + 1)
        raise Throttled(retry)


def record(db: Session, limit: Limit, key: str) -> None:
    db.add(AuthThrottle(kind=limit.kind, key=key))


def clear(db: Session, limit: Limit, key: str) -> None:
    db.execute(delete(AuthThrottle).where(
        AuthThrottle.kind == limit.kind, AuthThrottle.key == key))


def prune(db: Session, older_than_days: int = 2) -> int:
    cutoff = _now() - timedelta(days=older_than_days)
    result = db.execute(delete(AuthThrottle).where(AuthThrottle.created_at < cutoff))
    db.commit()
    return result.rowcount or 0
