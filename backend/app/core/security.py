"""Password hashing and the small JWT helper the community module needs.

``bcrypt`` is used directly rather than through passlib: one dependency fewer,
and passlib's backend detection has been a recurring source of noisy warnings.
"""
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.core.config import get_settings

ALGORITHM = "HS256"
# bcrypt silently truncates at 72 bytes, so reject longer input rather than
# accept a password whose tail never mattered.
MAX_PASSWORD_BYTES = 72
MIN_PASSWORD_LENGTH = 10


def hash_password(raw: str) -> str:
    return bcrypt.hashpw(_encode(raw), bcrypt.gensalt()).decode("utf-8")


def verify_password(raw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_encode(raw), hashed.encode("utf-8"))
    except ValueError:
        return False


def _encode(raw: str) -> bytes:
    encoded = raw.encode("utf-8")
    if len(encoded) > MAX_PASSWORD_BYTES:
        raise ValueError("password must be at most 72 bytes")
    return encoded


def create_access_token(subject: str, token_version: int = 0) -> str:
    """Issue a session token.

    The token carries the account's ``token_version``. Bumping that column
    invalidates every token already issued, which is how a password reset signs
    other devices out without a session table to delete from.
    """
    settings = get_settings()
    expires = datetime.now(UTC) + timedelta(minutes=settings.access_token_ttl_minutes)
    return jwt.encode(
        {"sub": subject, "ver": token_version, "exp": expires},
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> tuple[str, int] | None:
    """Return ``(subject, token_version)``, or ``None`` if the token is unusable."""
    try:
        payload = jwt.decode(token, get_settings().secret_key, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None
    subject = payload.get("sub")
    if not subject:
        return None
    return str(subject), int(payload.get("ver", 0))


def password_problem(password: str, avoid: list[str] | None = None) -> str | None:
    """Why this password is not acceptable, or ``None`` if it is.

    Length first, then variety, then the thing people actually do: reusing the
    nickname or the local part of the email as the password that protects them.
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"Use at least {MIN_PASSWORD_LENGTH} characters."
    if len(password.encode("utf-8")) > MAX_PASSWORD_BYTES:
        return "That password is too long."
    kinds = sum(
        [
            any(c.islower() for c in password),
            any(c.isupper() for c in password),
            any(c.isdigit() for c in password),
            any(not c.isalnum() for c in password),
        ]
    )
    if kinds < 2:
        return "Mix at least two of: lower case, upper case, digits, symbols."
    lowered = password.lower()
    for term in avoid or []:
        term = (term or "").strip().lower()
        term = term.split("@")[0]
        if len(term) >= 3 and term in lowered:
            return "Do not build the password out of your nickname or email."
    return None
