"""The remote translation engines' failure behaviour, the part that has to be right.

No network: the opener is a stub. What matters is that a refused key or a
provider that has stopped answering stops the run instead of being recorded,
string after string, as "cannot translate".
"""
from __future__ import annotations

import io
import json
import urllib.error

import pytest
from app.models.translation import ContentTranslation

from crawler.translate.engine import Translator
from crawler.translate.errors import Blocked


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


def test_blocked_gets_past_the_per_string_catch():
    # The engine catches Exception per string; Blocked must get through that.
    assert not issubclass(Blocked, Exception)


def test_the_engine_knows_its_engines():
    assert Translator.__new__(Translator).scope == "general"
    with pytest.raises(ValueError):
        Translator("zh", engine="nope")
    with pytest.raises(ValueError):
        Translator("zh", engine="google")


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


def refused():
    body = json.dumps({"contentFilter": [{"level": 2, "role": "assistant"}],
                       "error": {"code": "1301", "message": "敏感内容"}}).encode()
    return urllib.error.HTTPError("u", 400, "Bad Request", {}, io.BytesIO(body))


def test_a_content_filter_refusal_fails_the_string_once_and_never_stops_the_run():
    """Zhipu refuses some sexual-health and political sentences. Each refusal is
    that string's failure: no retries, and however many arrive in a row the run
    carries on - they once stopped a pass with fifteen pages left."""
    from crawler.translate.llm import ContentRefused, LLMModel

    opener = Opener([refused() for _ in range(20)] + [chat("你好")])
    model = LLMModel("zh", url="http://x/v4", key="K", model="m", opener=opener,
                     sleep=lambda _s: None)
    for _ in range(20):
        with pytest.raises(ContentRefused):
            model("a sentence")
    assert opener.calls == 20  # one request each, no retries
    assert model("hello") == "你好"


def test_a_plain_bad_request_is_still_retried():
    plain = urllib.error.HTTPError("u", 400, "Bad Request", {}, io.BytesIO(b'{"error":"x"}'))
    assert llm([plain, chat("你好")])("hello") == "你好"


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


def test_many_translates_in_parallel_and_keeps_every_string():
    import threading as _t

    from crawler.translate.engine import Translator

    engine = Translator.__new__(Translator)
    engine.locale, engine._cache, engine._renderings = "zh", {}, {}
    engine._lock = _t.Lock()
    engine.workers = 4
    engine.text = lambda s: f"译{s}"  # type: ignore[method-assign]
    out = engine.many(["a", "b", " a ", None, "", "c"])
    assert out == {"a": "译a", "b": "译b", "c": "译c"}


def test_a_blocked_worker_stops_the_batch():
    import threading as _t

    from crawler.translate.engine import Translator

    engine = Translator.__new__(Translator)
    engine.locale, engine._cache, engine._renderings = "zh", {}, {}
    engine._lock = _t.Lock()
    engine.workers = 3

    def boom(_s):
        raise Blocked("stop")

    engine.text = boom  # type: ignore[method-assign]
    with pytest.raises(Blocked):
        engine.many(["a", "b", "c"])


def test_a_translation_that_begins_with_zhe_shi_is_a_translation():
    from crawler.translate.llm import acceptable_reply

    assert acceptable_reply("This is a joint PhD program", "这是一个联合博士项目")
    assert not acceptable_reply("This is a joint PhD program", "以下是翻译：这是一个联合博士项目")


def test_polish_fixes_what_a_model_gets_wrong_and_nothing_else():
    from crawler.translate.engine import polish_zh

    assert polish_zh("完成课程单元 48门学分，您必须") == "完成课程 48 学分，你必须"
    assert polish_zh("6个学分") == "6 学分"
    assert polish_zh("续签学生准证前，先申请特别准证") == "续签学生签证前，先申请特别准证"
    # A Moodle unit is a unit, and 6门课程 is a count of units.
    assert polish_zh("Moodle 的一个单元，选修 6门课程") == "Moodle 的一个单元，选修 6门课程"


def test_polish_rows_rewrites_stored_strings():
    from crawler.translate.polish import polish_rows

    row = ContentTranslation(locale="zh", target_type="course", target_key="X", field="content",
                             provenance="machine", data={"strings": {"a": "完成24门学分", "b": "好"}})
    assert polish_rows([row]) == {"rows": 1, "strings": 1}
    assert row.data["strings"] == {"a": "完成24 学分", "b": "好"}


def test_polish_turns_discipline_the_academic_sense_into_xueke_and_leaves_conduct_alone():
    from crawler.translate.engine import polish_zh

    assert polish_zh("运用一系列纪律办法分析") == "运用一系列学科方法分析"
    assert polish_zh("一个有纪律的过程对于项目至关重要") == "一个规范的流程对于项目至关重要"
    assert polish_zh("培养精确推理的纪律习惯") == "培养精确推理的严谨习惯"
    # conduct stays conduct
    assert polish_zh("纪律委员会取消成绩") == "纪律委员会取消成绩"
    assert polish_zh("正式纪律处分") == "正式纪律处分"
