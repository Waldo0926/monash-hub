"""The engine's decisions that are made without the model.

Two of them, both from pages that were shipped wrong: the codes in the results
legend, which the model read as English words, and the multi-line strings that
made it hallucinate instead of translate. Neither needs Argos loaded, so the
model is stubbed and the assertions are about what is handed to it.
"""
from __future__ import annotations

import threading

import pytest
from app.knowledge.glossary import MASKS, placeholder

from crawler.translate.engine import _CODE, _SENTENCES, Translator

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


def test_a_rewritten_date_is_never_asked_for_unmasked():
    """The repair path re-translates with nothing masked.

    For a term that is the right answer - the model's own wording for
    "results" beats a page left in English. For a date it is how "1 Aug 2024"
    came back as 2024年8月1日纽约 in the first place. Every mask may be tried,
    because a token this model rewrites another one survives, but the date is
    behind one of them every time.
    """
    calls = []
    engine = translator(lambda text: calls.append(text) or "考核于兹卡截止")
    assert engine.text("The assessment is due on 1 Aug 2024.") is None
    assert not any("1 Aug 2024" in call for call in calls)
    assert len(calls) == len(MASKS)  # each mask once, and then it stops


def test_a_token_the_model_rewrites_is_swapped_for_one_it_copies():
    """The whole point of the cascade: a sentence lost to Zq is not lost.

    This stub does what the live model does - transliterates the Zq token and
    copies every other one - so the sentence only comes back whole if a second
    mask is tried.
    """
    def stub(text):
        if "Zq" in text:
            return "什么是兹卡?"
        return text.replace("What is", "什么是").replace("?", "?")

    engine = translator(stub)
    assert engine.text("What is academic integrity?") == "什么是学术诚信?"


def test_the_masks_are_tried_in_order_and_the_first_win_is_kept():
    calls = []
    engine = translator(lambda text: calls.append(text) or (
        "Qxa是什么" if "Qx" in text else "兹卡是什么"  # only Qx is copied back
    ))
    engine.text("What is academic integrity?")
    tried = [mask for call in calls for mask in MASKS if placeholder(0, mask) in call]
    assert tried == list(MASKS[:3])  # in order, and stopped at the one that held


def test_a_bracketed_label_is_translated_a_part_at_a_time():
    """A teaching period and its code are two problems, not one sentence.

    The stub rewrites any mask it is given, which is what the live model does
    to these labels - "Summer semester A (SSA-02)" was published in English
    because the lone "A" was enough to make it look like a sentence.
    """
    engine = translator(lambda text: "夏天")
    assert engine.text("Summer semester A (SSA-02)") == "夏季学期 A (SSA-02)"


def test_a_bracketed_labels_qualifier_is_still_translated():
    """The code keeps its ASCII brackets; the Chinese qualifier does not."""
    def stub(text):
        if "Except" in text:
            return "法学院课程除外"
        return "三月一日"

    engine = translator(stub)
    result = engine.text("Trimester 1 (T1-58) (Except Faculty of Law units)")
    assert result == "第 1 学段 (T1-58)（法学院课程除外）"


def test_the_model_is_given_a_straight_apostrophe():
    """Monash writes ’ and the model was trained on '.

    Eight of the sentences left in English on the live guides came back whole
    once the apostrophe was straightened, and nothing else changed.
    """
    calls = []
    engine = translator(lambda text: calls.append(text) or "如果你不确定，请联系学院。")
    engine.text("Check with your faculty if you’re unsure.")
    assert calls and all("’" not in call for call in calls)
    assert "you're" in calls[0]


def test_a_sentence_with_brackets_is_not_split_at_them():
    """Only labels are taken apart at their brackets.

    "... after the census date (but before the Withdrawn Fail date) your record
    will show ..." is a sentence. Split at the bracket, its head stands alone
    and comes back in English on an otherwise Chinese page.
    """
    engine = translator(lambda text: "兹卡")
    source = (
        "If you withdraw from a unit after the census date "
        "(but before the Withdrawn Fail date) your record will show it."
    )
    assert engine.text(source) is None  # English, rather than half a sentence


def test_a_term_and_its_acronym_are_not_glossed_twice():
    """Both halves of "grade point average (GPA)" are reserved terms.

    Each one's agreed wording carries the other, so restoring both wrote the
    gloss out twice on the live GPA page.
    """
    engine = translator(lambda text: text)
    assert engine.text("grade point average (GPA)") == "平均绩点（GPA）"


def test_sentences_glued_together_are_still_separate_sentences():
    """The crawler hands the transcripts page over with the spaces missing."""
    parts = _SENTENCES.split("about you:If it is Incomplete.Masters awarded")
    assert [part for part in parts if part] == [
        "about you:", "If it is Incomplete.", "Masters awarded",
    ]


def test_a_full_stop_inside_a_time_is_not_a_boundary():
    assert _SENTENCES.split("due at 11.55pm Friday") == ["due at 11.55pm Friday"]


def test_a_dash_between_clauses_splits_and_a_dash_in_a_date_does_not():
    assert len(_SENTENCES.split("continuing your course – we’re here to help")) == 3
    assert _SENTENCES.split("1 Jul – 30 Sep 2026") == ["1 Jul – 30 Sep 2026"]


def test_a_lost_term_still_gets_its_second_attempt():
    """The guard is about dates and codes, not about every lost placeholder."""
    calls = []
    engine = translator(lambda text: calls.append(text) or "兹卡是结果")
    engine.text("Results are published in WES.")
    assert len(calls) > 1


def test_one_terms_wording_is_not_read_as_another_terms():
    """*course* is 学位课程 and *unit* is 课程, one inside the other.

    Checking the shorter against the whole sentence found 课程 sitting inside
    学位课程 and called *unit* correctly rendered, which let 单位 - the reading
    this glossary exists to prevent - through onto the transcripts page.
    """
    plain = "成绩单列出所有学位课程和在校学习的所有单位。"
    engine = translator(lambda text: plain if len(text) > 12 else "单位")
    result = engine.text("It lists all courses and all units studied.")
    assert result is not None
    assert "单位" not in result
    assert "学位课程" in result and "课程" in result


def test_a_sentence_that_cannot_be_managed_does_not_take_the_others():
    """A time that came back rewritten used to cost the whole paragraph."""
    def stub(text: str) -> str:
        if "Zq" in text:
            return "申请于兹卡截止"  # the placeholder came back transliterated
        return "无需缴费。"
    engine = translator(stub)
    result = engine.text(
        "Applications close at 11.59pm on the day it is set. No fees are incurred."
    )
    assert result is not None
    # The sentence the engine will not vouch for keeps its English ...
    assert "Applications close at 11.59pm on the day it is set." in result
    # ... and the one that was never in question is still translated.
    assert "无需缴费。" in result


@pytest.mark.parametrize(
    "signed,expected",
    [
        ("退课你的学位课程（英语）.", "退课你的学位课程"),
        ("2026年4月1日（中文（简体)）.", "2026年4月1日"),
        ("2025年9月10日（简体中文）.", "2025年9月10日"),
    ],
)
def test_the_model_does_not_get_to_sign_its_work(signed, expected):
    """A short heading came back with the name of a language stuck on the end."""
    engine = translator(lambda text: signed)
    assert engine.text("Read this notice") == expected


def test_a_sentence_that_is_really_about_a_language_keeps_its_brackets():
    engine = translator(lambda text: "本Zqa以英文授课（英语）")
    assert engine.text("This unit is taught in English") == "本课程以英文授课（英语）"
