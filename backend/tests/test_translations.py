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
        "method": "human",
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


def test_a_link_survives_translation(gpa_blocks):
    tr = translations.Translation("zh")
    tr.strings = {
        "You can view your latest GPA in the Web Enrolment System (WES) at any time.":
            "你随时可以在选课系统（WES）里查看最新的 GPA。"
    }
    items = [
        item
        for block in translations.translate_blocks(gpa_blocks, tr)
        if block["type"] == "list"
        for item in block["items"]
    ]
    translated = next(i for i in items if "".join(s["text"] for s in i).startswith("你随时"))
    assert any(s.get("url", "").startswith("https://my.monash.edu") for s in translated)


def test_the_outline_and_the_headings_cannot_disagree(gpa_blocks):
    tr = translations.Translation("zh")
    tr.strings = {"Methodology": "计算方法"}
    blocks = translations.translate_blocks(gpa_blocks, tr)
    outline = translations.translated_headings(blocks)

    assert "计算方法" in [h["text"] for h in outline]
    assert [h["text"] for h in outline] == [b["text"] for b in blocks if b["type"] == "heading"]


def test_nothing_is_touched_when_there_are_no_strings(gpa_blocks):
    assert translations.translate_blocks(gpa_blocks, translations.Translation("zh")) is gpa_blocks
