"""Signing in with Google.

The authorization code flow, server side. Three things in it are worth reading
rather than skimming, because each one is a place this kind of code is usually
got wrong.

**The state parameter is signed, not stored, and bound to one browser.** It
carries an expiry, a nonce and an HMAC over the app's secret key, so a callback
arriving with a state we did not issue is rejected without needing a session
table or a Redis. The signature alone is not enough: anybody can start a sign-in
of their own, stop at the callback, and hand that URL - with its perfectly
valid state - to somebody else, whose browser then signs into the sender's
account. So the nonce is also set as a cookie by the browser that started, and
the callback only completes in a browser that sends the same one back.

**The ID token is decoded without verifying its signature, and that is
deliberate.** Normally that would be indefensible. It is safe here for one
specific reason: this token does not come from the browser. It comes back on a
direct TLS connection to Google's token endpoint, authenticated with our client
secret, in response to a code we just sent. Google's own documentation says a
token obtained this way needs no local signature check. `issuer` and `audience`
are still checked, because defence that costs two comparisons is worth having.

**A Google identity is only accepted when Google says the address is verified.**
Accounts are matched by email, so an unverified address would let somebody who
signed up to Google with an address they do not own walk into the account that
does. `email_verified` is not optional.
"""
from __future__ import annotations

import base64
import binascii
import hmac
import json
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from hashlib import sha256

from app.core.config import Settings, get_settings

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
ISSUERS = ("https://accounts.google.com", "accounts.google.com")
SCOPES = "openid email profile"

# Long enough to sign in, short enough that a leaked callback URL is stale by
# the time anyone finds it.
STATE_TTL_SECONDS = 10 * 60
# Holds the nonce from the state, so the callback can tell the browser that
# started a sign-in from one that was merely handed the callback URL.
NONCE_COOKIE = "mh_google_nonce"

USER_AGENT = "MonashHub/0.1 (+https://monashhub.secureview.tech)"


class GoogleAuthError(RuntimeError):
    """The sign-in could not be completed. The message is shown to nobody."""


@dataclass(frozen=True, slots=True)
class GoogleIdentity:
    email: str
    email_verified: bool
    name: str | None
    subject: str


def is_configured(settings: Settings | None = None) -> bool:
    settings = settings or get_settings()
    return bool(settings.google_client_id and settings.google_client_secret)


def redirect_uri(settings: Settings | None = None) -> str:
    """Where Google sends the browser back to.

    Derived from ``site_url`` unless overridden, because it has to match what is
    registered in the Google console character for character, and having it
    computed from one value means one place to change when the host does.
    """
    settings = settings or get_settings()
    if settings.google_redirect_uri:
        return settings.google_redirect_uri
    base = settings.site_url.rstrip("/")
    return f"{base}{settings.api_prefix}/auth/google/callback"


# --- state ----------------------------------------------------------------

def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _unb64(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def new_nonce() -> str:
    return secrets.token_urlsafe(16)


def issue_state(nonce: str, next_path: str = "/") -> str:
    """A signed, expiring token proving this callback answers our own request.

    ``nonce`` is the value the starting browser holds in its cookie.
    ``next_path`` rides along so the user lands back where they started. It is
    checked by the caller before use - a path from a query string is somebody
    else's input, and an open redirect is exactly what it would buy them.
    """
    payload = json.dumps(
        {"n": nonce, "exp": int(time.time()) + STATE_TTL_SECONDS, "next": next_path},
        separators=(",", ":"),
    ).encode("utf-8")
    signature = hmac.new(get_settings().secret_key.encode("utf-8"), payload, sha256).digest()
    return f"{_b64(payload)}.{_b64(signature)}"


def read_state(state: str, nonce: str) -> str:
    """Return the ``next`` path, or raise if the state is not one we issued to
    the browser holding ``nonce``."""
    try:
        encoded, signature = state.split(".", 1)
        payload = _unb64(encoded)
        expected = hmac.new(
            get_settings().secret_key.encode("utf-8"), payload, sha256
        ).digest()
        if not hmac.compare_digest(expected, _unb64(signature)):
            raise GoogleAuthError("state signature does not match")
        data = json.loads(payload)
    except GoogleAuthError:
        raise
    except (ValueError, binascii.Error, UnicodeDecodeError) as exc:
        raise GoogleAuthError("state is malformed") from exc

    if int(data.get("exp", 0)) < time.time():
        raise GoogleAuthError("state has expired")
    if not nonce or not hmac.compare_digest(str(data.get("n", "")), nonce):
        raise GoogleAuthError("state was issued to a different browser")
    return str(data.get("next") or "/")


# --- the flow -------------------------------------------------------------

def authorize_url(state: str, settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    query = urllib.parse.urlencode(
        {
            "client_id": settings.google_client_id,
            "redirect_uri": redirect_uri(settings),
            "response_type": "code",
            "scope": SCOPES,
            "state": state,
            # Google remembers the last account otherwise, which on a shared
            # laptop signs the previous person back in without asking.
            "prompt": "select_account",
        }
    )
    return f"{AUTHORIZE_URL}?{query}"


def exchange(code: str, settings: Settings | None = None) -> GoogleIdentity:
    """Trade the one-time code for the identity behind it."""
    settings = settings or get_settings()
    body = urllib.parse.urlencode(
        {
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": redirect_uri(settings),
            "grant_type": "authorization_code",
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        TOKEN_URL,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=settings.google_timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise GoogleAuthError(f"token endpoint returned HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise GoogleAuthError(f"token endpoint unreachable: {exc.reason}") from exc

    id_token = payload.get("id_token")
    if not id_token:
        raise GoogleAuthError("no id_token in the token response")
    return _identity_from(id_token, settings)


def _identity_from(id_token: str, settings: Settings) -> GoogleIdentity:
    """Read the claims. See the module docstring for why this does not verify."""
    try:
        _header, body, _signature = id_token.split(".")
        claims = json.loads(_unb64(body))
    except (ValueError, binascii.Error, UnicodeDecodeError) as exc:
        raise GoogleAuthError("id_token is not a readable JWT") from exc

    if claims.get("iss") not in ISSUERS:
        raise GoogleAuthError(f"unexpected issuer: {claims.get('iss')!r}")
    if claims.get("aud") != settings.google_client_id:
        raise GoogleAuthError("id_token was issued for a different client")

    email = (claims.get("email") or "").strip().lower()
    if not email:
        raise GoogleAuthError("no email in the id_token")

    return GoogleIdentity(
        email=email,
        # Google sends this as a real boolean or as the string "true".
        email_verified=str(claims.get("email_verified", "")).lower() == "true",
        name=(claims.get("name") or "").strip() or None,
        subject=str(claims.get("sub") or ""),
    )
