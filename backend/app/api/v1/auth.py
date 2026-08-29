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
import unicodedata

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core import avatars, verification
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
