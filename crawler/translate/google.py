"""Google Cloud Translation, as an alternative to the offline model.

On the live degree pages the offline model (Argos) rendered "WAM of 65" as
"65 years old of weighted average mark", *cervical spine* as the cervix and
*mechatronics* five different ways. Google's neural model, given the same
sentences with the glossary's terms masked out exactly as before, got all of
them right. The glossary and the reviewed table in ``structure_zh.py`` stay in
front of it; this only replaces what the model does with the words that are
left.

It is opt-in (``--engine google-cloud``), needs ``GOOGLE_TRANSLATE_API_KEY``,
and is billed per character. Everything it writes is ``machine`` provenance,
named ``machine:google-cloud+glossary``. The text sent is Handbook text that is
public on handbook.monash.edu.
"""
from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request

from crawler.translate.errors import MAX_CONSECUTIVE_FAILURES, Blocked

log = logging.getLogger(__name__)

TARGETS = {"zh": "zh-CN", "ja": "ja", "ko": "ko"}
_RETRIES = 4


CLOUD_ENDPOINT = "https://translation.googleapis.com/language/translate/v2"
KEY_ENV = "GOOGLE_TRANSLATE_API_KEY"


class CloudModel:
    """Cloud Translation (v2, basic NMT) with an API key.

    A callable with the same shape as the Argos one: English in, Chinese out.
    A rejected key or an exhausted quota (403) is not a bad sentence and stops
    the run at once; repeated failure of any kind does too.
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


def load_cloud(locale: str) -> CloudModel:
    import os

    key = os.environ.get(KEY_ENV, "").strip()
    if not key:
        raise SystemExit(f"--engine google-cloud needs {KEY_ENV} in the environment")
    return CloudModel(locale, key)
