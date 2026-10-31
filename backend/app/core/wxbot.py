"""The 马莫百科 WeChat bot, asked on behalf of the Ask panel.

The bot answers from the owner's taught Q&A, the 马莫百科 posts and sentences
quoted from official pages, none of which this API holds. It is a separate
service on its own host name, so anything going wrong there (not configured,
down, slow, refusing) comes back as ``None`` and the panel carries on with
this API's own answer.
"""
from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass

from app.core.config import get_settings

log = logging.getLogger(__name__)

USER_AGENT = "MonashHub/1.0 (+https://monashhub.secureview.tech)"


@dataclass(frozen=True)
class BotAnswer:
    route: str
    reply: str | None


def configured() -> bool:
    settings = get_settings()
    return bool(settings.wxbot_url and settings.wxbot_web_secret)


def ask(question: str, visitor: str) -> BotAnswer | None:
    if not configured():
        return None
    settings = get_settings()
    request = urllib.request.Request(
        settings.wxbot_url.rstrip("/") + "/web/ask",
        data=json.dumps({"question": question, "visitor": visitor}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.wxbot_web_secret}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=settings.wxbot_timeout_seconds) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            return BotAnswer("rate_limited", None)
        log.warning("wechat bot returned HTTP %s", exc.code)
        return None
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        log.warning("wechat bot unreachable: %s", exc)
        return None
    route = body.get("route")
    reply = body.get("reply")
    if not isinstance(route, str):
        return None
    return BotAnswer(route, reply if isinstance(reply, str) and reply.strip() else None)
