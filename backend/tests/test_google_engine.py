"""The Google backend's failure behaviour - the part that has to be right.

No network: the opener is a stub. What matters is that a blocked endpoint stops
the run instead of being recorded, string after string, as "cannot translate".
"""
from __future__ import annotations

import io
import json
import urllib.error

import pytest

from crawler.translate.engine import Translator
from crawler.translate.google import Blocked, GoogleModel


def reply(text):
    return io.BytesIO(json.dumps([[[text, "src", None, None]], None, "en"]).encode())


class Opener:
    def __init__(self, answers):
        self.answers = list(answers)
        self.calls = 0

    def __call__(self, request, timeout=0):
        self.calls += 1
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer


def model(answers):
    return GoogleModel("zh", opener=Opener(answers), sleep=lambda _s: None, clock=lambda: 0.0)


def test_a_reply_is_joined_from_its_segments():
    body = io.BytesIO(json.dumps([[["你好，", "Hello, ", 0], ["世界", "world", 0]]]).encode())
    assert model([body])("Hello, world") == "你好，世界"


def test_a_transient_failure_is_retried():
    m = model([urllib.error.URLError("reset"), reply("好")])
    assert m("fine") == "好"


def test_one_bad_string_does_not_stop_the_run():
    bad = [urllib.error.URLError("x")] * 4
    m = model(bad)
    with pytest.raises(RuntimeError):
        m("one")


def test_a_blocked_endpoint_stops_the_run_and_is_not_swallowed():
    m = model([urllib.error.URLError("429")] * 4 * 8)
    for _ in range(7):
        with pytest.raises(RuntimeError):
            m("x")
    with pytest.raises(Blocked):
        m("x")
    # The engine catches Exception per string; Blocked must get through that.
    assert not issubclass(Blocked, Exception)


def test_the_engine_uses_the_google_model_only_when_asked():
    assert Translator.__new__(Translator).scope == "general"
    with pytest.raises(ValueError):
        Translator("zh", engine="nope")
