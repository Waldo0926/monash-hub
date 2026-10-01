"""Google's web translation endpoint, as an alternative to the offline model.

Why it exists
-------------
On the live degree pages the offline model (Argos) rendered "WAM of 65" as
"65 years old of weighted average mark", *cervical spine* as the cervix and
*mechatronics* five different ways. Google's neural model, given the same
sentences with the glossary's terms masked out exactly as before, got all of
them right - grammar, word order and the domain word. The glossary and the
reviewed table in ``structure_zh.py`` stay in front of it; this only replaces
what the model does with the words that are left.

What it costs, and why it is opt-in
-----------------------------------
It is the unofficial ``translate_a/single`` endpoint the public web page uses.
There is no key and no contract: it rate-limits, and it can start refusing a
client without notice. So:

* it is never the default - ``--engine google`` on the translate runner;
* requests are paced and retried with backoff;
* a run that keeps failing **stops** instead of carrying on. The engine catches
  an ordinary exception per string so one bad sentence cannot end a pass of five
  thousand units - which, against a blocked endpoint, would quietly record every
  string as untranslatable. ``Blocked`` is a ``BaseException`` for exactly that
  reason.

Everything it writes is ``machine`` provenance, named ``machine:google+glossary``.
The text sent is Handbook text that is public on handbook.monash.edu.
"""
from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request

log = logging.getLogger(__name__)

ENDPOINT = "https://translate.googleapis.com/translate_a/single"
TARGETS = {"zh": "zh-CN", "ja": "ja", "ko": "ko"}

#: Seconds between requests. The endpoint starts answering 429 well before a
#: steady two a second, so this is deliberately slower than it needs to be.
MIN_INTERVAL = 1.5
#: Seconds to sit out a 429 before asking again. The endpoint throttles a client
#: for minutes at a time; retrying after two seconds only extends it.
COOLDOWN = 120.0
#: Consecutive failed requests, after backoff, before the run gives up.
MAX_CONSECUTIVE_FAILURES = 8
_RETRIES = 4


class Blocked(BaseException):
    """The endpoint has stopped answering. Not an ``Exception`` on purpose."""


class GoogleModel:
    """A callable with the same shape as the Argos one: English in, Chinese out."""

    def __init__(self, locale: str, *, opener=urllib.request.urlopen, sleep=time.sleep,
                 clock=time.monotonic) -> None:
        if locale not in TARGETS:
            raise ValueError(f"no target code for {locale!r}")
        self.target = TARGETS[locale]
        self._open = opener
        self._sleep = sleep
        self._clock = clock
        self._last = 0.0
        self._failures = 0
        self.requests = 0

    def __call__(self, text: str) -> str:
        body = urllib.parse.urlencode(
            {"client": "gtx", "sl": "en", "tl": self.target, "dt": "t", "q": text}
        ).encode()
        delay = 2.0
        for attempt in range(_RETRIES):
            wait = MIN_INTERVAL - (self._clock() - self._last)
            if wait > 0:
                self._sleep(wait)
            self._last = self._clock()
            self.requests += 1
            try:
                request = urllib.request.Request(
                    ENDPOINT, data=body, headers={"User-Agent": "Mozilla/5.0"}
                )
                with self._open(request, timeout=30) as response:
                    payload = json.load(response)
                rendered = "".join(part[0] for part in payload[0] if part and part[0])
                self._failures = 0
                return rendered
            except urllib.error.HTTPError as exc:
                log.warning("google translate attempt %d failed: %s", attempt + 1, exc)
                self._sleep(COOLDOWN * (attempt + 1) if exc.code == 429 else delay)
                delay *= 2
            except (urllib.error.URLError, TimeoutError, ValueError, KeyError, IndexError) as exc:
                log.warning("google translate attempt %d failed: %s", attempt + 1, exc)
                self._sleep(delay)
                delay *= 2
        self._failures += 1
        if self._failures >= MAX_CONSECUTIVE_FAILURES:
            raise Blocked(
                f"{self._failures} requests in a row failed after retries; stopping rather "
                "than recording every remaining string as untranslatable"
            )
        raise RuntimeError("google translate did not answer")


CLOUD_ENDPOINT = "https://translation.googleapis.com/language/translate/v2"
KEY_ENV = "GOOGLE_TRANSLATE_API_KEY"


class CloudModel:
    """Cloud Translation (v2, basic NMT) with an API key: the supported route.

    Same shape as ``GoogleModel``. No cooldown dance - it is a paid API with a
    quota, not a web page - but the same rule about failure: a rejected key or an
    exhausted quota (403) is not a bad sentence and stops the run at once, and
    repeated failure of any kind does too.
    """

    def __init__(self, locale: str, key: str, *, opener=urllib.request.urlopen,
                 sleep=time.sleep) -> None:
        if locale not in TARGETS:
            raise ValueError(f"no target code for {locale!r}")
        self.target = TARGETS[locale].split("-")[0] if locale != "zh" else "zh-CN"
        self._key = key
        self._open = opener
        self._sleep = sleep
        self._failures = 0
        self.requests = 0
        self.characters = 0

    def __call__(self, text: str) -> str:
        body = urllib.parse.urlencode(
            {"q": text, "source": "en", "target": self.target, "format": "text"}
        ).encode()
        delay = 1.0
        for attempt in range(_RETRIES):
            self.requests += 1
            try:
                request = urllib.request.Request(
                    f"{CLOUD_ENDPOINT}?key={urllib.parse.quote(self._key)}", data=body
                )
                with self._open(request, timeout=30) as response:
                    payload = json.load(response)
                self._failures = 0
                self.characters += len(text)
                return payload["data"]["translations"][0]["translatedText"]
            except urllib.error.HTTPError as exc:
                if exc.code in (400, 401, 403):
                    # Key rejected, API not enabled, or quota/billing exhausted.
                    raise Blocked(f"Cloud Translation answered {exc.code}: {exc.reason}") from exc
                log.warning("cloud translate attempt %d failed: %s", attempt + 1, exc)
                self._sleep(delay)
                delay *= 2
            except (urllib.error.URLError, TimeoutError, ValueError, KeyError, IndexError) as exc:
                log.warning("cloud translate attempt %d failed: %s", attempt + 1, exc)
                self._sleep(delay)
                delay *= 2
        self._failures += 1
        if self._failures >= MAX_CONSECUTIVE_FAILURES:
            raise Blocked(f"{self._failures} requests in a row failed after retries")
        raise RuntimeError("cloud translate did not answer")


def load(locale: str):
    return GoogleModel(locale)


def load_cloud(locale: str) -> CloudModel:
    import os

    key = os.environ.get(KEY_ENV, "").strip()
    if not key:
        raise SystemExit(f"--engine google-cloud needs {KEY_ENV} in the environment")
    return CloudModel(locale, key)
