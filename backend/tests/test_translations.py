"""Translations of source content.

What is being pinned here is mostly what the feature refuses to do: guess at a
string it has no translation for, and keep quiet when the English it was
translated from has moved on.
"""
from __future__ import annotations

import pytest
from app.knowledge import translations
from app.knowledge.cleaner import clean_page
from app.models.translation import GLOBAL, OFFICIAL_PAGE, PUBLISHED, ContentTranslation


def _store(db, **kwargs):
    row = ContentTranslation(locale="zh", status=PUBLISHED, **kwargs)
    db.add(row)
    db.commit()
    return row


# --- lookup ---------------------------------------------------------------

def test_english_never_looks_anything_up(db):
    _store(db, target_type=OFFICIAL_PAGE, target_key="gpa", field="title", text="平均绩点")
    assert not translations.load(db, "en", OFFICIAL_PAGE, "gpa")
    assert not translations.load(db, None, OFFICIAL_PAGE, "gpa")


def test_an_untranslated_string_stays_in_english(db):
    _store(
        db, target_type=OFFICIAL_PAGE, target_key="gpa", field="body",
        data={"strings": {"Grade": "成绩等级"}},
    )
    tr = translations.load(db, "zh", OFFICIAL_PAGE, "gpa")
    assert tr.string("Grade") == "成绩等级"
    assert tr.string("Withdrawn fail") == "Withdrawn fail"


def test_a_page_overrides_the_shared_boilerplate(db):
    _store(
        db, target_type=GLOBAL, target_key="handbook", field="strings",
        data={"strings": {"Results": "成绩"}},
    )
    _store(
        db, target_type=OFFICIAL_PAGE, target_key="results", field="body",
        data={"strings": {"Results": "成绩公布"}},
    )
    tr = translations.load(db, "zh", OFFICIAL_PAGE, "results")
    assert tr.string("Results") == "成绩公布"


def test_prose_is_translated_paragraph_by_paragraph(db):
    """The Handbook's stock paragraphs repeat; the unit's own do not."""
    _store(
        db, target_type=GLOBAL, target_key="handbook", field="strings",
        data={"strings": {"Active learning - stock paragraph.": "主动学习 —— 固定段落。"}},
    )
    tr = translations.load(db, "zh", "unit", "FIT1008")
    source = "Active learning - stock paragraph.\n\nSomething written for this unit."
    assert tr.field("teaching_approach", source) == (
        "主动学习 —— 固定段落。\n\nSomething written for this unit."
    )


def test_load_many_is_one_query_for_many_targets(db):
    _store(db, target_type=OFFICIAL_PAGE, target_key="gpa", field="title", text="平均绩点")
    _store(db, target_type=OFFICIAL_PAGE, target_key="wam", field="title", text="加权平均分")

    found = translations.load_many(db, "zh", OFFICIAL_PAGE, ["gpa", "wam", "fees"])
    assert found["gpa"].field("title", "GPA") == "平均绩点"
    assert found["wam"].field("title", "WAM") == "加权平均分"
    # A target with nothing stored still gets an entry, so callers never KeyError.
    assert found["fees"].field("title", "Fees") == "Fees"


# --- staleness ------------------------------------------------------------

def test_a_string_map_written_against_older_english_is_not_flagged(db):
    """A changed sentence stops matching; it does not silently mistranslate.

    Whole-field translations do go quietly out of date, so those are still
    flagged - see the test below. Warning on string maps as well put a "may be
    out of date" banner on every page the extractor had ever touched.
    """
    from app.models.translation import OFFICIAL_PAGE, PUBLISHED, ContentTranslation

    db.add(
        ContentTranslation(
            locale="zh", target_type=OFFICIAL_PAGE, target_key="fees", field="content",
            status=PUBLISHED, source_hash="hash-when-translated",
            data={"strings": {"Fees": "学费"}},
        )
    )
    db.commit()

    tr = translations.load(db, "zh", OFFICIAL_PAGE, "fees", source_hash="a-different-hash")
    assert tr.stale is False
    assert tr.string("Fees") == "学费"


def test_a_translation_of_text_that_has_changed_is_flagged(db):
    _store(
        db, target_type=OFFICIAL_PAGE, target_key="gpa", field="title",
        text="平均绩点", source_hash="hash-when-translated",
    )

    current = translations.load(db, "zh", OFFICIAL_PAGE, "gpa", source_hash="hash-when-translated")
    assert current.stale is False
    assert current.meta() == {
        "locale": "zh",
        "stale": False,
        "unofficial": True,
        "machine": False,
        "reviewed": True,
    }

    moved_on = translations.load(db, "zh", OFFICIAL_PAGE, "gpa", source_hash="monash-edited-it")
    # Still shown - a slightly old translation beats nothing - but not silently.
    assert moved_on.field("title", "GPA") == "平均绩点"
    assert moved_on.stale is True


def test_the_shared_boilerplate_never_goes_stale(db):
    """It has no upstream page to drift from, so flagging it would be noise."""
    _store(
        db, target_type=GLOBAL, target_key="handbook", field="strings",
        data={"strings": {"Grade": "成绩等级"}},
    )
    tr = translations.load(db, "zh", OFFICIAL_PAGE, "gpa", source_hash="anything")
    assert tr.stale is False


# --- applying to blocks ---------------------------------------------------

@pytest.fixture
def gpa_blocks(official_html):
    return clean_page(official_html("gpa-tabbed"), url="u")["blocks"]


def _paragraphs(blocks):
    return [
        "".join(s["text"] for s in b["spans"]) for b in blocks if b["type"] == "paragraph"
    ]


def test_a_table_is_translated_cell_by_cell(gpa_blocks):
    tr = translations.Translation("zh")
    tr.strings = {
        "Grades and their GPA grade value": "各成绩等级对应的 GPA 数值",
        "Grade": "成绩等级",
        "GPA grade value": "GPA 数值",
        "High distinction": "High distinction（最高优等）",
    }
    table = next(
        b for b in translations.translate_blocks(gpa_blocks, tr)
        if b["type"] == "table" and b["columns"][0] == "成绩等级"
    )
    assert table["caption"] == "各成绩等级对应的 GPA 数值"
    assert table["columns"] == ["成绩等级", "GPA 数值"]
    assert table["rows"][0] == ["High distinction（最高优等）", "4.0"]
    # No entry for "Credit", so it is left alone rather than approximated.
    assert table["rows"][1] == ["Credit", "2.0"]


def test_a_paragraph_is_translated_as_one_sentence_not_span_by_span(gpa_blocks):
    """The English breaks mid-sentence at every <strong>; Chinese does not."""
    english = next(p for p in _paragraphs(gpa_blocks) if p.startswith("For example"))
    tr = translations.Translation("zh")
    tr.strings = {english: "举例来说……"}

    assert "举例来说……" in _paragraphs(translations.translate_blocks(gpa_blocks, tr))


def _one_list(spans):
    return [{"type": "list", "ordered": False, "items": [spans]}]


def _translated_item(spans, strings):
    tr = translations.Translation("zh")
    tr.strings = strings
    blocks = translations.translate_blocks(_one_list(spans), tr)
    return blocks[0]["items"][0]


def test_a_run_that_is_all_link_keeps_it():
    item = _translated_item(
        [{"text": "Check your census date", "url": "https://monash.edu/census"}],
        {"Check your census date": "查看你的 census date（学籍统计日）"},
    )
    assert item == [
        {"text": "查看你的 census date（学籍统计日）", "url": "https://monash.edu/census"}
    ]


def test_a_link_on_a_few_words_does_not_swallow_the_paragraph():
    """The reported bug: a paragraph blue from end to end, opening a mail client.

    A single mailto on an address inside a long paragraph was being carried by
    the whole translated paragraph, so clicking anywhere in it sent mail.
    """
    english = (
        "If the module freezes, you need to email servicedesk@monash.edu "
        "with the subject line CUP merge required."
    )
    item = _translated_item(
        [
            {"text": "If the module freezes, you need to email "},
            {"text": "servicedesk@monash.edu", "url": "mailto:servicedesk@monash.edu"},
            {"text": " with the subject line CUP merge required."},
        ],
        {english: "如果模块卡住，请发邮件到 servicedesk@monash.edu，主题写 CUP merge required。"},
    )
    linked = [s for s in item if s.get("url")]
    assert [s["text"] for s in linked] == ["servicedesk@monash.edu"]
    assert "".join(s["text"] for s in item).startswith("如果模块卡住")


def test_a_link_whose_words_cannot_be_found_is_dropped_not_moved():
    """A link on the wrong words is worse than no link.

    The anchor here is a third of the sentence and its Chinese is nowhere in the
    translation, so there is no honest place to put it.
    """
    english = "You can view your latest GPA in the Web Enrolment System (WES) at any time."
    item = _translated_item(
        [
            {"text": "You can view your latest GPA in the "},
            {"text": "Web Enrolment System (WES)", "url": "https://my.monash.edu"},
            {"text": " at any time."},
        ],
        {english: "你随时可以在选课系统里查看最新的 GPA。"},
    )
    assert item == [{"text": "你随时可以在选课系统里查看最新的 GPA。"}]


def test_the_outline_and_the_headings_cannot_disagree(gpa_blocks):
    tr = translations.Translation("zh")
    tr.strings = {"Methodology": "计算方法"}
    blocks = translations.translate_blocks(gpa_blocks, tr)
    outline = translations.translated_headings(blocks)

    assert "计算方法" in [h["text"] for h in outline]
    assert [h["text"] for h in outline] == [b["text"] for b in blocks if b["type"] == "heading"]


def test_nothing_is_touched_when_there_are_no_strings(gpa_blocks):
    assert translations.translate_blocks(gpa_blocks, translations.Translation("zh")) is gpa_blocks


# --- machine and human side by side ----------------------------------------

def test_a_checked_translation_wins_over_a_machine_one(db):
    """Both can exist for one target. The one a person wrote is what shows."""
    from app.knowledge import translations
    from app.models.translation import HUMAN, MACHINE, OFFICIAL_PAGE, PUBLISHED, ContentTranslation

    for provenance, text in ((MACHINE, "人口普查日期"), (HUMAN, "课程退选截止日")):
        db.add(
            ContentTranslation(
                locale="zh",
                target_type=OFFICIAL_PAGE,
                target_key="census-dates",
                field="content",
                provenance=provenance,
                status=PUBLISHED,
                data={"strings": {"census date": text}},
            )
        )
    db.commit()

    tr = translations.load(db, "zh", OFFICIAL_PAGE, "census-dates")
    assert tr.string("census date") == "课程退选截止日"
    # And the page says both things happened to it.
    assert tr.meta() == {
        "locale": "zh",
        "stale": False,
        "unofficial": True,
        "machine": True,
        "reviewed": True,
    }


def test_a_machine_only_page_says_so(db):
    from app.knowledge import translations
    from app.models.translation import MACHINE, OFFICIAL_PAGE, PUBLISHED, ContentTranslation

    db.add(
        ContentTranslation(
            locale="zh",
            target_type=OFFICIAL_PAGE,
            target_key="fees",
            field="content",
            provenance=MACHINE,
            status=PUBLISHED,
            data={"strings": {"Fees": "学费"}},
        )
    )
    db.commit()

    meta = translations.load(db, "zh", OFFICIAL_PAGE, "fees").meta()
    assert meta["machine"] is True
    assert meta["reviewed"] is False


def test_machine_strings_fill_the_gaps_a_person_left(db):
    """The mixed case: a few paragraphs checked, the rest translated."""
    from app.knowledge import translations
    from app.models.translation import HUMAN, MACHINE, OFFICIAL_PAGE, PUBLISHED, ContentTranslation

    db.add(
        ContentTranslation(
            locale="zh", target_type=OFFICIAL_PAGE, target_key="wam", field="content",
            provenance=MACHINE, status=PUBLISHED,
            data={"strings": {"What is WAM?": "什么是 WAM？", "How it is used": "机器译文"}},
        )
    )
    db.add(
        ContentTranslation(
            locale="zh", target_type=OFFICIAL_PAGE, target_key="wam", field="content",
            provenance=HUMAN, status=PUBLISHED,
            data={"strings": {"How it is used": "人工校对过的译文"}},
        )
    )
    db.commit()

    tr = translations.load(db, "zh", OFFICIAL_PAGE, "wam")
    assert tr.string("How it is used") == "人工校对过的译文"
    assert tr.string("What is WAM?") == "什么是 WAM？"
