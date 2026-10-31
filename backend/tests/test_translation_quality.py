"""What the October 2026 side-by-side of four free models found wrong.

Seventy paragraphs of the guides, read against their English. Some of what went
wrong was the model; most of it was ours - the glossary reaching into web
addresses and into phrases it has no business in - and every model did it.
"""
from __future__ import annotations

import threading

import pytest
from app.knowledge.glossary import GENERAL, HANDBOOK, addresses_kept, protect, terms_in

from crawler.translate import llm
from crawler.translate.engine import Translator


def _engine(reply, scope=GENERAL) -> Translator:
    engine = Translator.__new__(Translator)
    engine.locale = "zh"
    engine.engine = "argos"
    engine.workers = 1
    engine._caches = {}
    engine._renderings = {}
    engine._lock = threading.Lock()
    engine.use_scope(scope)
    engine._translate = reply
    return engine


# -- addresses -------------------------------------------------------------------


@pytest.mark.parametrize("address", [
    "https://www.monash.edu/students/admin/fees",
    "www.monash.edu.my/finance",
    "monash.edu/policy-bank",
    "https://www.monash.edu/__data/assets/pdf_file/mon2750-monash-innovation-guarantee.pdf",
    "servicedesk@monash.edu",
])
def test_an_address_is_kept_whole_and_never_given_a_capital(address):
    masked, kept = protect(f"See {address} for details.", "zh")
    assert address not in masked and kept == [address]
    assert not terms_in(f"Visit {address}.", "zh")


def test_an_address_does_not_swallow_the_full_stop_after_it():
    _masked, kept = protect("Apply at https://forms.monash.edu/x. Then wait.", "zh")
    assert kept == ["https://forms.monash.edu/x"]


def test_monash_in_prose_is_still_kept_in_english():
    assert terms_in("Monash offers scholarships.", "zh") == [("Monash", "Monash")]


def test_a_stored_translation_gets_its_address_back():
    source = "Email servicedesk@monash.edu or visit www.monash.edu/mon2750-monash-guarantee."
    stored = "请发邮件至 servicedesk@Monash.edu 或访问 www.Monash.edu/mon2750-Monash-guarantee。"
    assert addresses_kept(source, stored) == (
        "请发邮件至 servicedesk@monash.edu 或访问 www.monash.edu/mon2750-monash-guarantee。"
    )


def test_priming_repairs_what_was_stored_before():
    engine = _engine(lambda text: "不该再问")
    engine.prime({"Go to www.monash.edu now.": "现在访问 www.Monash.edu。"})
    assert engine.text("Go to www.monash.edu now.") == "现在访问 www.monash.edu。"


def test_a_stored_translation_with_a_term_inside_its_address_is_translated_again():
    """2026-10-25: --refresh reused course S2010's stored sentence with
    forms.Monash.edu/选课注册-amendment in it, an address that does not exist."""
    source = "Submit https://forms.monash.edu/enrolment-amendment by Friday."
    engine = _engine(lambda text: text.replace("Submit", "请在周五前提交").replace(" by Friday.", "。"))
    engine.prime({source: "请在周五前提交 https://forms.Monash.edu/选课注册-amendment。"})
    assert "https://forms.monash.edu/enrolment-amendment" in engine.text(source)


def test_a_masked_translation_keeps_the_address_as_written():
    engine = _engine(lambda text: text.replace("Visit", "访问").replace(" for help.", "获取帮助。"))
    assert "https://www.monash.edu.my/its" in engine.text(
        "Visit https://www.monash.edu.my/its for help."
    )


# -- terms that are not terms everywhere -------------------------------------------


def test_a_course_of_action_is_not_a_degree():
    assert ("course of action", "行动方案") in terms_in("Choose a course of action.", "zh")
    assert all(agreed != "学位课程" for _, agreed in terms_in("Choose a course of action.", "zh"))


def test_off_campus_is_a_teaching_mode_only_in_the_handbook():
    assert not terms_in("Find off-campus accommodation near Sunway.", "zh")
    assert terms_in("Off-campus", "zh", scope=HANDBOOK) == [("Off-campus", "校外授课")]


def test_the_semester_break_keeps_its_break():
    assert terms_in("during the mid-semester break", "zh") == [
        ("mid-semester break", "学期中假期")
    ]
    assert terms_in("over the semester break", "zh") == [("semester break", "学期假期")]


def test_the_prompt_lets_a_scholarship_award_be_a_scholarship():
    assert "scholarship" in llm.SYSTEM_ZH and "not a prize" not in llm.SYSTEM_ZH


# -- the model -------------------------------------------------------------------


def test_an_abbreviation_the_source_never_had_is_rejected():
    assert not llm.acceptable_reply("TEXT:\nSubmit the LKM form.", "提交 LLM 表格。")
    assert llm.acceptable_reply("TEXT:\nSubmit the LKM form.", "提交 LKM 表格。")
    # Translating one away is fine; only inventing one is not.
    assert llm.acceptable_reply("TEXT:\nRead the FAQ.", "阅读常见问题。")
    # An agreed wording in the glossary may bring its own.
    glossary = "GLOSSARY:\n- weighted average mark = 加权平均分（WAM）\nTEXT:\nYour mark."
    assert llm.acceptable_reply(glossary, "你的加权平均分（WAM）。")


def test_the_default_model_is_the_one_that_read_best():
    assert llm.DEFAULT_MODEL == "glm-4.5-flash"
    assert llm.THINKING_MODELS.match(llm.DEFAULT_MODEL)


def test_a_reply_that_carries_the_prompt_is_rejected_even_with_a_glossary():
    prompt = "GLOSSARY:\n- Monash = Monash\nTEXT:\nYour School directly."
    assert not llm.acceptable_reply(prompt, "你学校直接组织。\n\nGLOSSARY:\n\nTEXT:\n别的")
    assert llm.acceptable_reply(prompt, "由你的学院直接组织。")


def test_a_stored_reply_with_the_prompt_in_it_is_not_reused():
    engine = _engine(lambda text: "由你的学院直接组织。")
    engine.prime({"Your School directly.": "你学校直接组织。\n\nGLOSSARY:\n\nTEXT:\n别的"})
    assert "GLOSSARY" not in engine.text("Your School directly.")


# -- a bold label at the start of a paragraph ----------------------------------------


def _spans(label, rest):
    return [{"text": label, "bold": True}, {"text": rest}]


@pytest.mark.parametrize("spans, expected", [
    (_spans("How to apply", " Visit: https://x.monash.edu"),
     ("How to apply", "Visit: https://x.monash.edu")),
    (_spans("Note:", " you must enrol first."), ("Note", "you must enrol first.")),
    (_spans("All grades", " must be counted."), None),
    (_spans("This is a whole bold sentence of its own, and it is long.", " Then."), None),
    ([{"text": "plain"}, {"text": " text"}], None),
])
def test_what_counts_as_a_label(spans, expected):
    from crawler.translate.run import labelled

    assert labelled(spans) == expected


def test_a_label_and_its_sentence_are_translated_apart_and_joined():
    from crawler.translate.run import translate_strings

    asked: list[str] = []
    answers = {"Eligibility": "申请条件", "Open to students across all Schools.": "所有学院学生均可申请。"}
    engine = _engine(lambda text: asked.append(text) or answers[text.removeprefix("TEXT:\n")])
    joined = "Eligibility Open to students across all Schools."
    out = translate_strings(engine, [joined], {joined: (
        "Eligibility", "Open to students across all Schools.")})
    assert out == {joined: "申请条件：所有学院学生均可申请。"}
    assert joined not in asked


def test_english_that_says_here_is_may_be_translated_as_yixia_shi():
    source = "TEXT:\nHere's what you need to know while you're on intermission."
    assert llm.acceptable_reply(source, "以下是你在休学期间需要了解的信息。")
    assert not llm.acceptable_reply("TEXT:\nRead this before you go.", "以下是翻译：出发前请阅读。")
