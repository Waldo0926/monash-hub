"""What a translation copies as written: long numbers, addresses, and not an apology.

The full audit of stored translations on 2026-10-26 found, next to the money
in the wrong currency (test_currency.py): February 2021 intake as 2022年2月,
July 2026 as 2027年7月, a Zoom meeting ID replaced by 很抱歉，我无法提供…,
a phone number left out, and links with the glossary inside their path.
"""
from __future__ import annotations

import pytest
from app.knowledge import translations
from app.knowledge.glossary import facts_kept, numbers_kept, refused
from app.models.translation import HUMAN, MACHINE, OFFICIAL_PAGE, PUBLISHED, ContentTranslation

from crawler.translate.engine import stored_ok
from crawler.translate.llm import faithful


@pytest.mark.parametrize("source, translated", [
    ("February 2021 intake", "2022年2月入学"),
    ("Commencing July 2026", "2027年7月开学"),
    ("Call +61 3 990 59987 after hours", "下班后请致电"),
    ("Meeting ID: 893 6793 6761", "会议号：893 6793"),
])
def test_a_changed_or_dropped_number_is_not_kept(source, translated):
    assert not numbers_kept(source, translated)
    assert not facts_kept(source, translated)


@pytest.mark.parametrize("source, translated", [
    ("February 2021 intake", "2021年2月入学"),
    ("Call +61 3 990 59987", "请致电 +61 3 9905 9987"),
    ("Meeting ID: 89367936761", "会议号：893 6793 6761"),
    ("over 45,000 students", "超过 45000 名学生"),
    ("2,000 words", "2,000 字"),
    ("worth 250 million", "价值 2.5 亿"),
    ("2 semesters and 24 credit points", "两个学期、24 学分"),
    ("Sat 28 Feb 2026, 10.30am", "2026年2月28日（星期六）上午10:30"),
    ("See FIT2004 and level 3", "见 FIT2004 和三年级"),
    ("published in China after the 1980s", "20 世纪 80 年代以后在中国出版"),
])
def test_the_same_numbers_are_kept(source, translated):
    assert numbers_kept(source, translated)


def test_the_models_apology_is_not_a_translation():
    assert refused("Meeting ID: 89367936761", "很抱歉，我无法提供该会议的链接。")
    assert refused("Next", "I'm sorry, I can't help with that.")
    assert refused("Next", "申し訳ありませんが、翻訳できません。")
    # The English apologising is translated as an apology.
    assert not refused("Sorry, this page cannot be found", "很抱歉，找不到此页面")
    # 无法 on its own is an ordinary word.
    assert not refused("If you cannot log in, contact ITS", "如果无法登录，请联系 ITS")
    # Monash's own apostrophe is curly, and its FAQ asks in the first person.
    assert not refused("I can’t log in to Moodle", "我无法登录 Moodle")
    assert not refused("I can't log in to Moodle", "我无法登录 Moodle")
    assert not refused("What if I couldn’t attend my exam?", "如果我无法参加考试怎么办？")
    assert not refused("I won’t be able to submit on time", "我无法按时提交")
    assert refused("Next", "I’m sorry, I can’t help with that.")


def test_an_address_with_the_glossary_in_its_path_is_not_kept():
    source = "Jobs at https://www.ajobthing.com/malaysia/jobs"
    assert not facts_kept(source, "工作机会见 https://www.ajobthing.com/马来西亚校区/jobs")
    assert facts_kept(source, "工作机会见 https://www.ajobthing.com/malaysia/jobs")
    # Only the case changed: put back on the way out, so not a lost address.
    assert facts_kept("See www.monash.edu/exams", "见 www.Monash.edu/exams")


def test_the_chat_models_reply_with_another_year_is_not_faithful():
    assert not faithful("February 2021 intake", "2022年2月入学", [])
    assert faithful("February 2021 intake", "2021年2月入学", [])


def test_a_stored_translation_that_lost_a_fact_is_translated_again():
    assert not stored_ok("Commencing July 2026", "2027年7月开学")
    assert not stored_ok("Meeting ID: 89367936761", "很抱歉，我无法提供该会议的链接。")
    assert stored_ok("Commencing July 2026", "2026年7月开学")


def test_a_machine_string_that_lost_a_fact_is_read_as_the_english():
    tr = translations.Translation("zh")
    strings = {"Commencing July 2026": "2027年7月开学", "Commencing July 2027": "2027年7月开学"}
    translations._apply(tr, ContentTranslation(
        locale="zh", target_type=OFFICIAL_PAGE, target_key="p", field="content",
        provenance=MACHINE, status=PUBLISHED, data={"strings": strings}))
    assert tr.string("Commencing July 2026") == "Commencing July 2026"
    assert tr.string("Commencing July 2027") == "2027年7月开学"
    person = translations.Translation("zh")
    translations._apply(person, ContentTranslation(
        locale="zh", target_type=OFFICIAL_PAGE, target_key="p", field="content",
        provenance=HUMAN, status=PUBLISHED, data={"strings": {"Call 1300 666 717": "请致电热线"}}))
    assert person.string("Call 1300 666 717") == "请致电热线"


def test_every_reviewed_translation_keeps_its_facts():
    from app.knowledge.translations_seed import TRANSLATION_SEEDS

    bad = [(en, zh) for seed in TRANSLATION_SEEDS for en, zh in seed.strings.items()
           if not facts_kept(en, zh)]
    assert bad == []


def test_malaysia_in_a_sentence_is_the_country():
    from app.knowledge.glossary import GENERAL, HANDBOOK, protect

    # Bank Negara Malaysia came out as 马来西亚校区的… on the student pass page.
    _masked, kept = protect("Pay through Bank Negara Malaysia approved banks", "zh", scope=GENERAL)
    assert "马来西亚" in kept and "马来西亚校区" not in kept
    _masked, kept = protect("Students at the Malaysia campus", "zh", scope=GENERAL)
    assert "马来西亚校区" in kept
    # Where a unit is taught, in the Handbook, it is the campus.
    _masked, kept = protect("Part C. Applied studies - Malaysia", "zh", scope=HANDBOOK)
    assert "马来西亚校区" in kept
