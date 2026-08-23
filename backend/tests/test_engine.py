"""The engine's decisions that are made without the model.

Two of them, both from pages that were shipped wrong: the codes in the results
legend, which the model read as English words, and the multi-line strings that
made it hallucinate instead of translate. Neither needs Argos loaded, so the
model is stubbed and the assertions are about what is handed to it.
"""
from __future__ import annotations

import threading

import pytest

from crawler.translate.engine import _CODE, Translator

CODES = ["P", "N", "HD", "D", "C", "NE", "NAS", "NGO", "NH", "NS", "NSR",
         "PGO", "SFR", "WDN", "WH", "WI", "WN", "DEF"]


def translator(stub):
    """A Translator with the model replaced, so nothing is downloaded."""
    engine = Translator.__new__(Translator)
    engine.locale = "zh"
    engine._cache = {}
    engine._renderings = {}
    engine._lock = threading.Lock()
    engine._translate = stub
    return engine


@pytest.mark.parametrize("code", CODES)
def test_a_grade_code_is_recognised(code):
    assert _CODE.match(code)


@pytest.mark.parametrize("prose", ["Pass", "Fail", "Credit", "Withheld", "Not Assessed",
                                   "High Distinction", "Hurdle Fail", "80–100"])
def test_prose_is_not_mistaken_for_a_code(prose):
    assert not _CODE.match(prose)


@pytest.mark.parametrize("code", CODES)
def test_a_code_never_reaches_the_model(code):
    calls = []
    engine = translator(lambda text: calls.append(text) or "译")
    assert engine.text(code) is None  # so the reader is shown the code itself
    assert calls == []


def test_a_term_that_looks_like_a_code_still_gets_its_wording():
    """WAM matches the code shape. The glossary is consulted first anyway."""
    calls = []
    engine = translator(lambda text: calls.append(text) or "译")
    assert engine.text("WAM") == "WAM（加权平均分）"
    assert calls == []


def test_each_line_is_translated_on_its_own():
    """A link's title and the sentence under it arrive as one string.

    Handed over whole, the model wrote a wiki's citation error into the middle
    of it. Each line goes over separately now.
    """
    calls = []
    engine = translator(lambda text: calls.append(text) or f"中文{len(calls)}")
    result = engine.text("Take a look\n \nIt covers a range of topics.")
    assert calls == ["Take a look", "It covers a range of topics."]
    assert result == "中文1\n \n中文2"


def test_a_line_the_model_cannot_manage_keeps_its_english():
    """One bad line must not cost the rest of the string."""
    def stub(text):
        return text if text.startswith("Not") else "中文"

    engine = translator(stub)
    assert engine.text("Take a look\nNot Configured line") == "中文\nNot Configured line"


def test_a_string_of_one_line_is_unaffected():
    engine = translator(lambda text: "中文")
    assert engine.text("A single sentence.") == "中文"


def test_a_lost_placeholder_no_longer_costs_the_sentence():
    """The guides were left half English by giving up at this point.

    The model transliterated the token instead of copying it. Rather than keep
    the English, the sentence is translated again unmasked and the term's own
    rendering is replaced with the agreed wording.
    """
    def stub(text):
        if "Zq" in text:
            return "在兹卡之前付款。"          # the placeholder did not survive
        if text == "census date":
            return "人口普查日期"              # what the model calls it alone
        return "在人口普查日期之前付款。"

    engine = translator(stub)
    assert engine.text("Pay before the census date.") == "在census date（学籍统计日）之前付款。"


def test_english_is_kept_when_the_term_cannot_be_found():
    """The repair only works if the rendering is actually in the sentence.

    Approximating instead would put 人口普查日期 in front of a student, which
    is the whole reason the term is reserved.
    """
    def stub(text):
        if "Zq" in text:
            return "在兹卡之前付款。"
        if text == "census date":
            return "人口普查日期"
        return "在某个日子之前付款。"          # nothing to match on

    engine = translator(stub)
    assert engine.text("Pay before the census date.") is None


def test_the_model_landing_on_the_agreed_wording_is_accepted():
    def stub(text):
        if "Zq" in text:
            return "在兹卡之前付款。"
        return "在census date（学籍统计日）之前付款。"

    engine = translator(stub)
    assert engine.text("Pay before the census date.") == "在census date（学籍统计日）之前付款。"


def test_an_acronym_the_model_copied_is_still_replaced():
    """WAM, NSR and SFR come back from the model untouched.

    The term is then still in English rather than wrongly rendered, so the
    agreed wording can go in instead of the sentence being given up on.
    """
    def stub(text):
        if "Zq" in text:
            return "兹卡不计入。"                 # placeholder lost
        if text == "WAM":
            return "WAM"
        return "WAM 不计入计算。"                 # copied straight through

    engine = translator(stub)
    assert engine.text("WAM is not included.") == "WAM（加权平均分）不计入计算。"


def test_a_title_of_two_terms_loses_the_english_space():
    """"Accounting fundamentals" is two glossary terms and no translation.

    It still needs tidying: the space that separated the English words is not
    a space between two Chinese ones, and it shipped as 会计 基础.
    """
    calls = []
    engine = translator(lambda text: calls.append(text) or "译")
    assert engine.text("Accounting fundamentals") == "会计基础"
    assert calls == []  # never reached the model


def test_tidying_does_not_close_a_paragraph_break():
    """The punctuation rules used to match across a blank line.

    A workload field arrived as several paragraphs and left as one: the rule
    that turns ")" between two Chinese characters into "）" was reading the
    blank line after it as more whitespace to swallow.
    """
    from crawler.translate.engine import _tidy

    source = "参加每周小组会议（每周5小时)\n\n参加研讨会和座谈会\n\n每周至少5小时"
    assert _tidy(source, "zh") == "参加每周小组会议（每周5小时）\n\n参加研讨会和座谈会\n\n每周至少5小时"


def test_tidying_still_fixes_punctuation_within_a_line():
    from crawler.translate.engine import _tidy

    assert _tidy("找到教室,查看你的考核", "zh") == "找到教室，查看你的考核"
    assert _tidy("系： 市场营销", "zh") == "系：市场营销"


def test_a_full_width_bracket_is_closed_full_width():
    from crawler.translate.engine import _tidy

    assert _tidy("实习合同（及格门槛要求)", "zh") == "实习合同（及格门槛要求）"


def test_a_space_before_a_digit_is_kept():
    """财务会计 1 reads correctly; 会计基础 does not want the space."""
    from crawler.translate.engine import _tidy

    assert _tidy("财务会计 1", "zh") == "财务会计 1"


def test_a_costly_term_still_holds_the_sentence_back():
    """census date is the reason the glossary exists. No guessing at it."""
    def stub(text):
        if "Zq" in text:
            return "在兹卡之前付款。"
        if text == "census date":
            return "人口普查日期"
        return "在某个日子之前付款。"          # rendered a third way

    engine = translator(stub)
    assert engine.text("Pay before the census date.") is None


def test_an_ordinary_term_does_not():
    """"results" rendered some other way is not worth an English page.

    159 sentences across the guides were being held back by terms like this
    one - results, Moodle, teaching period - none of which decides anything a
    student spends money on.
    """
    def stub(text):
        if "Zq" in text:
            return "兹卡在周五公布。"
        if text == "results":
            return "结果"
        return "成绩在周五公布。"              # 成绩, not the 结果 we look for

    engine = translator(stub)
    assert engine.text("Results are released on Friday.") == "成绩在周五公布。"
