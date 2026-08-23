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
