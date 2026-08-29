"""Sign up, sign in, and password recovery.

Registration and recovery are both gated on a six-digit code sent to the
address, which is what makes an account recoverable at all - without it, a
forgotten password is a lost account.

Two rules run through every endpoint here:

* **Answer the same way regardless of whether the account exists.** "That email
  is already registered" and "no account with that email" both tell a stranger
  who has an account on a student forum. Requesting a code always looks like it
  worked; conflicts are reported only after a valid code proves the requester
  controls the address.
* **Never collect more than a nickname.** No real name, no student ID. The
  roadmap is explicit that registration friction is what leaves a forum empty.
"""
from __future__ import annotations

import logging
import re
import secrets
import unicodedata
import urllib.parse

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core import avatars, google_oauth, verification
from app.core.config import get_settings
from app.core.db import get_db
from app.core.email import EmailDeliveryError
from app.core.security import (
    create_access_token,
    hash_password,
    password_problem,
    verify_password,
)
from app.models.user import User

log = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

# Spelled out rather than taken from `status`: Starlette is mid-rename on this
# one and the constant emits a deprecation warning under the current version.
HTTP_422_UNPROCESSABLE = 422

NICKNAME_MIN = 3
NICKNAME_MAX = 48
# Letters (including CJK, so a Chinese or Japanese nickname is allowed), digits,
# and the three separators people expect. No spaces, no punctuation that can be
# used to impersonate another nickname.
NICKNAME_ALLOWED = re.compile(r"^[\w.\-]+$", re.UNICODE)


class SendCodeRequest(BaseModel):
    email: EmailStr
    purpose: str = Field(pattern="^(registration|password_reset)$")


class SignUpRequest(BaseModel):
    email: EmailStr
    nickname: str = Field(min_length=NICKNAME_MIN, max_length=NICKNAME_MAX)
    password: str = Field(min_length=1, max_length=128)
    verification_code: str = Field(min_length=6, max_length=6)


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    verification_code: str = Field(min_length=6, max_length=6)
    password: str = Field(min_length=1, max_length=128)


def _me(user: User) -> dict:
    return {
        "id": user.id,
        "nickname": user.nickname,
        "email": user.email,
        "is_admin": user.is_admin,
        # Carried here so the header can show the picture without a second
        # request on every page load.
        "avatar_url": avatars.url_for(user.avatar_file),
    }


def _nickname_problem(nickname: str) -> str | None:
    value = nickname.strip()
    if len(value) < NICKNAME_MIN:
        return f"Use at least {NICKNAME_MIN} characters."
    if len(value) > NICKNAME_MAX:
        return f"Use at most {NICKNAME_MAX} characters."
    if not NICKNAME_ALLOWED.match(value):
        return "Use letters, numbers, underscore, dot or hyphen only."
    return None


def _normalise_nickname(nickname: str) -> str:
    # NFKC folds the lookalike width variants, so "ｗaldo" cannot sit beside
    # "waldo" as a separate account.
    return unicodedata.normalize("NFKC", nickname.strip())


@router.post("/verification-code")
def send_verification_code(payload: SendCodeRequest, db: Session = Depends(get_db)) -> dict:
    """Send something to the address, whatever its state.

    The response is the same either way. A caller cannot learn from it whether
    the address is registered - and neither can they learn it from whether an
    email turns up, because one always does. Which email depends on the account,
    and only the person holding the mailbox ever reads it.
    """
    settings = get_settings()
    email = str(payload.email).strip().lower()

    exists = bool(db.scalar(select(func.count(User.id)).where(User.email == email)) or 0)

    try:
        verification.issue(db, email, payload.purpose, account_exists=exists)
    except verification.RateLimited as limited:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Too many code requests. Wait a moment and try again.",
            headers={"Retry-After": str(limited.retry_after_seconds)},
        ) from limited
    except EmailDeliveryError as exc:
        # A provider outage is our problem, and saying so is not a leak -
        # the caller learns nothing about the address from it.
        log.error("verification email failed: %s", exc)
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "We could not send the email just now. Try again shortly.",
        ) from exc

    return {
        "expires_in_seconds": settings.verification_code_ttl_seconds,
        "resend_available_in_seconds": settings.verification_resend_interval_seconds,
        "delivery_configured": settings.email_is_deliverable,
    }


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def sign_up(payload: SignUpRequest, db: Session = Depends(get_db)) -> dict:
    nickname = _normalise_nickname(payload.nickname)
    email = str(payload.email).strip().lower()

    problem = _nickname_problem(nickname)
    if problem:
        raise HTTPException(HTTP_422_UNPROCESSABLE, problem)
    problem = password_problem(payload.password, [nickname, email])
    if problem:
        raise HTTPException(HTTP_422_UNPROCESSABLE, problem)

    try:
        verification.verify(db, email, verification.REGISTRATION, payload.verification_code)
    except verification.VerificationError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    # Only now, with the address proven, is it safe to say what is taken.
    clash = db.scalar(
        select(User).where(or_(User.email == email, func.lower(User.nickname) == nickname.lower()))
    )
    if clash is not None:
        detail = (
            "That email is already registered."
            if clash.email == email
            else "That nickname is taken."
        )
        raise HTTPException(status.HTTP_409_CONFLICT, detail)

    user = User(email=email, nickname=nickname, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"token": create_access_token(str(user.id), user.token_version), "user": _me(user)}


@router.post("/signin")
def sign_in(payload: SignInRequest, db: Session = Depends(get_db)) -> dict:
    user = db.scalar(select(User).where(User.email == str(payload.email).strip().lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong email or password")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This account is suspended")
    user.last_login_at = func.now()
    db.commit()
    db.refresh(user)
    return {"token": create_access_token(str(user.id), user.token_version), "user": _me(user)}


@router.post("/password-reset")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> dict:
    """Set a new password using a code sent to the address.

    Succeeds into a signed-in session, and bumps ``token_version`` so every
    other device is signed out - if the reset was needed because someone else
    had the password, leaving their session alive would defeat the point.
    """
    email = str(payload.email).strip().lower()
    user = db.scalar(select(User).where(User.email == email))

    problem = password_problem(payload.password, [email, user.nickname if user else ""])
    if problem:
        raise HTTPException(HTTP_422_UNPROCESSABLE, problem)

    try:
        verification.verify(db, email, verification.PASSWORD_RESET, payload.verification_code)
    except verification.VerificationError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    # A valid password-reset code is only ever issued to a registered address,
    # so reaching here without a user means the account was deleted in between.
    if user is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "That code is not valid")

    user.password_hash = hash_password(payload.password)
    user.token_version += 1
    db.commit()
    db.refresh(user)
    return {
        "token": create_access_token(str(user.id), user.token_version),
        "user": _me(user),
        "other_sessions_signed_out": True,
    }


@router.get("/me")
def me(user: User = Depends(current_user)) -> dict:
    return _me(user)


# --- signing in with Google ------------------------------------------------
#
# The browser leaves for Google and comes back to /callback, which means the
# session token cannot be returned as JSON the way /signin does. It is handed
# over in the URL *fragment* instead: a fragment is never sent to a server, so
# it stays out of our access logs, out of nginx's, and out of any proxy in
# between. The page that receives it strips it from the address bar immediately.


def _unique_nickname(db: Session, preferred: str) -> str:
    """A nickname derived from the Google profile that nobody else holds.

    Falls back to a generated one rather than failing the sign-in: somebody
    whose Google name happens to collide, or is punctuation, should still get an
    account and can rename themselves on their profile afterwards.
    """
    # Nicknames deliberately allow no spaces - the rule exists so one cannot be
    # dressed up to look like another - and a Google profile name is almost
    # always two words. Cleaning it beats discarding it: "Waldo Wen" becomes
    # "WaldoWen", which is still recognisably the person, where a fallback to
    # "student" throws their name away over a space.
    base = re.sub(r"\s+", "", (preferred or "").strip())
    base = "".join(ch for ch in base if NICKNAME_ALLOWED.match(ch))[:NICKNAME_MAX]
    if _nickname_problem(base) is not None:
        base = "student"
    candidate = base
    for suffix in range(1, 200):
        clash = db.scalar(
            select(User).where(func.lower(User.nickname) == candidate.lower())
        )
        if clash is None and _nickname_problem(candidate) is None:
            return candidate
        candidate = f"{base[:NICKNAME_MAX - len(str(suffix))]}{suffix}"
    return f"student{secrets.token_hex(4)}"


@router.get("/google/start")
def google_start(next: str = "/", db: Session = Depends(get_db)) -> dict:
    """Where to send the browser to begin. The frontend follows this URL."""
    if not google_oauth.is_configured():
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, "Google sign-in is not configured"
        )
    # Only a path on this site, never an absolute URL somebody supplied - that
    # is the difference between a redirect and an open redirect.
    safe_next = next if next.startswith("/") and not next.startswith("//") else "/"
    return {"url": google_oauth.authorize_url(google_oauth.issue_state(safe_next))}


@router.get("/google/callback")
def google_callback(
    state: str = "",
    code: str = "",
    error: str = "",
    db: Session = Depends(get_db),
) -> RedirectResponse:
    """Where Google sends the browser back.

    Every failure lands the person on the sign-in page with a reason rather
    than on a JSON error, because this is a page they arrived at by clicking a
    button, not an API call they made.
    """
    settings = get_settings()
    site = settings.site_url.rstrip("/")

    def failed(reason: str) -> RedirectResponse:
        return RedirectResponse(f"{site}/login?google={reason}", status_code=303)

    if error or not code:
        # The commonest one by far is the person pressing cancel.
        return failed("cancelled")
    if not google_oauth.is_configured():
        return failed("unavailable")

    try:
        next_path = google_oauth.read_state(state)
        identity = google_oauth.exchange(code)
    except google_oauth.GoogleAuthError as exc:
        log.warning("google sign-in failed: %s", exc)
        return failed("failed")

    if not identity.email_verified:
        # Accounts are matched by address, so an unverified one would be a way
        # into somebody else's account.
        return failed("unverified")

    user = db.scalar(select(User).where(User.email == identity.email))
    if user is None:
        user = User(
            email=identity.email,
            nickname=_unique_nickname(db, identity.name or identity.email.split("@")[0]),
            # Signed in by Google, so there is no password to check. An unusable
            # hash rather than an empty one: /signin compares against this, and
            # it must never match anything a person could type.
            password_hash=hash_password(secrets.token_urlsafe(32)),
            is_active=True,
        )
        db.add(user)
    elif not user.is_active:
        return failed("suspended")

    user.last_login_at = func.now()
    db.commit()
    db.refresh(user)

    token = create_access_token(str(user.id), user.token_version)
    # The fragment, not the query string. See the note above.
    return RedirectResponse(
        f"{site}/auth/google#token={token}&next={urllib.parse.quote(next_path, safe='/')}",
        status_code=303,
    )
