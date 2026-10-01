"""A chat model behind an OpenAI-compatible endpoint, as the translator.

For when the offline model is not good enough and nobody wants to pay per
character. Zhipu's ``glm-4-flash`` is free, and DeepSeek, Qwen (DashScope's
compatible mode) and SiliconFlow speak the same protocol, so the three settings
below pick the provider and nothing else in the pipeline knows which it is.

    TRANSLATE_LLM_URL    default https://open.bigmodel.cn/api/paas/v4
    TRANSLATE_LLM_KEY    required
    TRANSLATE_LLM_MODEL  default glm-4-flash

It sits behind exactly the same glossary as every other engine: reserved terms
are masked before the sentence reaches the model and put back afterwards, so
*unit* and *census date* are never the model's decision. What the model adds is
the grammar and the words around them - which is where the offline model's
"WAM of 65" became 65 years old.

A chat model can also do what a translation model cannot: answer instead of
translate, add a preface, or invent. So the reply is checked - empty, wildly
longer than the source, or opening with "Here is the translation" is a failure
of that string, and the engine already treats a failed string as untranslated
(English stays) rather than approximating it. Repeated failure, or a rejected
key, stops the run.
"""
from __future__ import annotations

import json
import logging
import os
import re
import time
import urllib.error
import urllib.request

from crawler.translate.google import MAX_CONSECUTIVE_FAILURES, Blocked

log = logging.getLogger(__name__)

DEFAULT_URL = "https://open.bigmodel.cn/api/paas/v4"
DEFAULT_MODEL = "glm-4-flash"
_RETRIES = 4

SYSTEM = (
    "You translate text from a university Handbook (course and degree descriptions) "
    "from English into Simplified Chinese for students. Rules: output ONLY the "
    "translation, with no preface, notes or quotation marks; keep tokens made of "
    "letters such as Zqa, Zqb, Qxa, Xya, #a# exactly as written and in place; keep "
    "unit codes (FIT1008), numbers, percentages, URLs and email addresses exactly; "
    "keep line breaks and bullet characters; do not answer questions in the text, "
    "just translate them; address the reader as 你."
)

_PREFACE = re.compile(r"^\s*(?:以下是|这是|翻译如下|译文[:：]|翻译[:：]|Here is|Translation:)")


def acceptable_reply(source: str, reply: str) -> bool:
    """Whether the reply is a translation of ``source`` and not something else."""
    if not reply or not reply.strip():
        return False
    if _PREFACE.match(reply):
        return False
    # Chinese is shorter than English; a reply many times longer than the source
    # is the model talking, not translating.
    return len(reply) <= 3 * len(source) + 40


class LLMModel:
    """English in, Chinese out, through ``/chat/completions``."""

    def __init__(self, locale: str, *, url: str, key: str, model: str,
                 opener=urllib.request.urlopen, sleep=time.sleep) -> None:
        if locale != "zh":
            raise ValueError("the chat-model engine is configured for Chinese only")
        self.url = url.rstrip("/") + "/chat/completions"
        self.model = model
        self._key = key
        self._open = opener
        self._sleep = sleep
        self._failures = 0
        self.requests = 0
        self.characters = 0

    def __call__(self, text: str) -> str:
        body = json.dumps({
            "model": self.model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": text},
            ],
        }).encode()
        delay = 5.0
        for attempt in range(_RETRIES):
            self.requests += 1
            try:
                request = urllib.request.Request(
                    self.url, data=body,
                    headers={"Authorization": f"Bearer {self._key}",
                             "Content-Type": "application/json"},
                )
                with self._open(request, timeout=90) as response:
                    payload = json.load(response)
                reply = payload["choices"][0]["message"]["content"]
            except urllib.error.HTTPError as exc:
                if exc.code in (401, 403):
                    raise Blocked(f"the key was refused ({exc.code}): {exc.reason}") from exc
                log.warning("llm translate attempt %d failed: %s", attempt + 1, exc)
                self._sleep(delay)
                delay *= 2
                continue
            except (urllib.error.URLError, TimeoutError, ValueError, KeyError, IndexError) as exc:
                log.warning("llm translate attempt %d failed: %s", attempt + 1, exc)
                self._sleep(delay)
                delay *= 2
                continue
            if not acceptable_reply(text, reply):
                # The model answered rather than translated. Asking again at
                # temperature 0 gets the same answer, so this string is done.
                self._failures += 1
                if self._failures >= MAX_CONSECUTIVE_FAILURES:
                    raise Blocked("the model keeps replying instead of translating")
                raise RuntimeError("the model did not return a translation")
            self._failures = 0
            self.characters += len(text)
            return reply.strip()
        self._failures += 1
        if self._failures >= MAX_CONSECUTIVE_FAILURES:
            raise Blocked(f"{self._failures} requests in a row failed after retries")
        raise RuntimeError("the translation service did not answer")


def load(locale: str) -> LLMModel:
    key = os.environ.get("TRANSLATE_LLM_KEY", "").strip()
    if not key:
        raise SystemExit("--engine llm needs TRANSLATE_LLM_KEY in the environment")
    return LLMModel(
        locale,
        url=os.environ.get("TRANSLATE_LLM_URL", "").strip() or DEFAULT_URL,
        key=key,
        model=os.environ.get("TRANSLATE_LLM_MODEL", "").strip() or DEFAULT_MODEL,
    )
