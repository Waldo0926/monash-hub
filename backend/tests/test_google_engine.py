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


def cloud(answers):
    from crawler.translate.google import CloudModel

    return CloudModel("zh", "KEY", opener=Opener(answers), sleep=lambda _s: None)


def cloud_reply(text):
    return io.BytesIO(json.dumps({"data": {"translations": [{"translatedText": text}]}}).encode())


def test_cloud_returns_the_translated_text():
    m = cloud([cloud_reply("你好")])
    assert m("hello") == "你好"
    assert m.characters == 5


def test_a_rejected_key_or_exhausted_quota_stops_the_run_at_once():
    err = urllib.error.HTTPError("u", 403, "Forbidden", {}, None)
    m = cloud([err])
    with pytest.raises(Blocked):
        m("hello")


def test_cloud_without_a_key_refuses_to_start(monkeypatch):
    from crawler.translate.google import KEY_ENV, load_cloud

    monkeypatch.delenv(KEY_ENV, raising=False)
    with pytest.raises(SystemExit):
        load_cloud("zh")


def llm(answers):
    from crawler.translate.llm import LLMModel

    return LLMModel("zh", url="http://x/v4", key="K", model="m",
                    opener=Opener(answers), sleep=lambda _s: None)


def chat(text):
    return io.BytesIO(json.dumps({"choices": [{"message": {"content": text}}]}).encode())


def test_the_chat_model_returns_its_reply():
    assert llm([chat("你好")])("hello") == "你好"


def test_a_reply_that_is_not_a_translation_is_a_failure_of_that_string():
    for bad in ("", "以下是翻译：你好", "好" * 400):
        with pytest.raises(RuntimeError):
            llm([chat(bad)])("hello")


def test_a_refused_key_stops_the_run():
    err = urllib.error.HTTPError("u", 401, "Unauthorized", {}, None)
    with pytest.raises(Blocked):
        llm([err])("hello")


def test_the_prompt_forbids_prefaces_and_keeps_placeholders():
    from crawler.translate.llm import SYSTEM

    assert "ONLY the translation" in SYSTEM and "Zqa" in SYSTEM


def test_a_reply_missing_an_agreed_wording_a_code_or_a_number_is_not_faithful():
    from crawler.translate.llm import faithful, prompt_with_glossary

    terms = [("units", "课程"), ("credit points", "学分")]
    src = "Complete FIT1008 (24 credit points) from these units"
    assert faithful(src, "从这些课程中完成 FIT1008（24 学分）", terms)
    assert not faithful(src, "从这些科目中完成 FIT1008（24 学分）", terms)
    assert not faithful(src, "从这些课程中完成课程（24 学分）", terms)
    assert not faithful(src, "从这些课程中完成 FIT1008（学分）", terms)
    assert "units = 课程" in prompt_with_glossary(src, terms)


def test_a_repeated_term_is_collapsed():
    from crawler.translate.engine import _tidy

    assert _tidy("本学位课程课程提供", "zh") == "本学位课程提供"


def test_a_degree_named_in_prose_is_handed_over_and_checked():
    from app.knowledge.degrees import names_in

    from crawler.translate.llm import faithful

    text = "The Master of Regulation and Compliance is aimed at professionals."
    names = names_in(text)
    assert names and names[0][1] == "监管与合规硕士"
    assert not faithful(text, "城市设计硕士旨在面向专业人士", names)
    assert faithful(text, "监管与合规硕士面向专业人士", names)


def test_a_dropped_bullet_is_not_faithful():
    from crawler.translate.llm import faithful

    assert not faithful("- one\n- two", "一\n二", [])
    assert faithful("- one\n- two", "- 一\n- 二", [])


def test_a_coded_unit_line_uses_the_agreed_title_and_never_the_model():
    calls = []
    import threading

    from crawler.translate.engine import Translator

    engine = Translator.__new__(Translator)
    engine.locale = "zh"
    engine._cache = {}
    engine._renderings = {}
    engine._lock = threading.Lock()
    engine._translate = lambda text: calls.append(text) or "错"
    out = engine.text("MCD1270 Accounting in business")
    assert out == "MCD1270 商业会计"
    assert calls == []
