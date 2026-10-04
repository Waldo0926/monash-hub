"""The reviewed wording for degree structure, and what keeps it from rotting.

Every case here is a sentence that was on the live site: the offline model
rendered *Breadth studies* as 面包研究 and *Robotics and mechatronics
engineering* as five different nonsense words on one page. The table has to
stay free of that kind of word, and the engine has to use it before the model.
"""
from __future__ import annotations

import re
import threading

import pytest
from app.knowledge import structure
from app.knowledge.structure_zh import STRUCTURE_ZH

from crawler.translate.engine import Translator

# Wrong words this table exists to get rid of. None may appear in a value.
WRONG = re.compile(
    "面包|中子|中医药|中杂技|中程器|惩罚|互联网档案馆|存檔|维基|兹卡|纪律|单元|溪流"
)


def test_the_bakery_is_gone():
    assert STRUCTURE_ZH["Part B. Breadth studies"] == "B 部分。通识课程（Breadth studies）"
    assert STRUCTURE_ZH["First year engineering breadth studies"].endswith("（Breadth studies）")


def test_mechatronics_is_mechatronics_everywhere_it_is_named():
    named = {k: v for k, v in STRUCTURE_ZH.items() if "mechatronics" in k.lower()}
    assert named, "the table no longer mentions mechatronics at all"
    for english, chinese in named.items():
        assert "机电一体化" in chinese, english


def test_no_value_carries_a_known_wrong_word():
    bad = {k: v for k, v in STRUCTURE_ZH.items() if WRONG.search(v)}
    assert bad == {}


def test_every_key_is_the_english_as_stored():
    """Keys are looked up after ``strip()``; one with spaces at the edge could
    never match. An empty value would hide the English behind a blank."""
    for english, chinese in STRUCTURE_ZH.items():
        assert english == english.strip(), repr(english)
        assert chinese.strip(), repr(english)


def test_a_sentence_addressed_to_the_student_uses_one_pronoun():
    assert [k for k, v in STRUCTURE_ZH.items() if "您" in v] == []


def test_credit_is_not_a_loan():
    """"You will receive credit for the following unit" was 您将获得…的贷款."""
    credit = STRUCTURE_ZH["You will receive credit for the following unit:"]
    assert "学分减免" in credit and "贷款" not in credit


@pytest.mark.parametrize(
    ("english", "chinese"),
    [
        ("Part A. Core studies", "A 部分。核心课程"),
        ("Part B. Breadth studies", "B 部分。通识课程（Breadth studies）"),
        ("Part 2. Discipline studies", "第 2 部分。学科课程"),
        ("Part C. Applied studies - Malaysia", "C 部分。应用课程 - 马来西亚校区"),
        ("Part A. Specialist studies (24 or 36 credit points)",
         "A 部分。专业方向课程（24 或 36 学分）"),
        ("Level 8 - Bachelor Honours Degree", "第 8 级 - 荣誉学士学位"),
        ("Level 7 - Bachelor Degree / Level 9 - Master's Degree (Extended)",
         "第 7 级 - 学士学位 / 第 9 级 - 硕士学位（延伸型）"),
        ("3000 words", "3000 字"),
        ("(3,000 words)", "（3,000 字）"),
        ("2 - Quiz / Test", "2 - 小测 / 测验"),
    ],
)
def test_a_label_with_a_known_shape_is_composed(english, chinese):
    assert structure.compose(english, "zh") == chinese


@pytest.mark.parametrize(
    "english",
    [
        "Part B. Underwater basketry",      # a title nobody has reviewed
        "Part. Core studies",
        "Level 11 - Galactic Doctorate",
        "Part A. Core studies - Atlantis",  # a suffix that is not in the table
        "Essay (2000 words)",               # not a shape this reads
    ],
)
def test_an_unknown_piece_is_left_to_the_translator(english):
    assert structure.compose(english, "zh") is None


def test_only_chinese_is_composed():
    assert structure.compose("Part A. Core studies", "ja") is None


def _engine(stub):
    engine = Translator.__new__(Translator)
    engine.locale = "zh"
    engine._cache = {}
    engine._renderings = {}
    engine._lock = threading.Lock()
    engine._translate = stub
    return engine


def test_a_reviewed_string_never_reaches_the_model():
    calls = []
    engine = _engine(lambda text: calls.append(text) or "面包研究")
    assert engine.text("Part B. Breadth studies") == "B 部分。通识课程（Breadth studies）"
    assert engine.text("Robotics and mechatronics engineering") == "机器人与机电一体化工程"
    assert calls == []


def test_a_composed_label_never_reaches_the_model():
    calls = []
    engine = _engine(lambda text: calls.append(text) or "错")
    # Not in the table by name, but a known title in a known shape.
    assert engine.text("Part D. Free elective studies (12 or 24 credit points)") == (
        "D 部分。自由选修课程（12 或 24 学分）"
    )
    assert calls == []


def test_each_line_of_a_list_is_looked_up_on_its_own():
    engine = _engine(lambda text: "错")
    text = "• Curating\n• drawing"
    assert engine.text(text) == "• 策展\n• 素描"


def test_curated_wording_is_not_presented_as_a_checked_translation():
    """Nobody who reads Chinese has read this table, so a page that uses it is
    still machine work. It must beat the machine without earning the word
    "checked"."""
    from app.knowledge.translations import Translation, _apply
    from app.models.translation import CURATED, ContentTranslation

    translation = Translation("zh")
    _apply(
        translation,
        ContentTranslation(
            locale="zh", target_type="global", target_key="handbook", field="structure",
            provenance=CURATED, data={"strings": {"Part B. Breadth studies": "B 部分。通识课程"}},
        ),
    )
    assert translation.machine is True
    assert translation.reviewed is False
    # ...and it wins over a machine rendering of a whole field containing it.
    assert "Part B. Breadth studies" in translation.human_strings


def test_a_person_still_beats_curated_wording():
    from app.knowledge.translations import Translation, _apply
    from app.models.translation import CURATED, HUMAN, MACHINE, ContentTranslation

    def row(provenance, text):
        return ContentTranslation(
            locale="zh", target_type="unit", target_key="X", field="content",
            provenance=provenance, data={"strings": {"Minor": text}},
        )

    translation = Translation("zh")
    rank = {MACHINE: 0, CURATED: 1, HUMAN: 2}
    for candidate in sorted((row(MACHINE, "小型"), row(HUMAN, "辅修"), row(CURATED, "辅修专业")),
                            key=lambda r: rank[r.provenance]):
        _apply(translation, candidate)
    assert translation.string("Minor") == "辅修"


def test_a_unit_item_without_its_own_translation_takes_the_unit_title():
    from app.api.v1.courses import _name_units

    containers = [{
        "items": [
            {"code": "ACW1020", "type": "unit", "name": "Accounting in business",
             "name_translated": False},
            {"code": "BFW1001", "type": "unit", "name": "金融学基础", "name_translated": True},
            {"code": "A1", "type": "major", "name": "Accountancy", "name_translated": False},
        ],
        "containers": [],
    }]
    units = {"ACW1020": {"title": "商业会计"}, "BFW1001": {"title": "别的"}}
    _name_units(containers, units)
    names = [i["name"] for i in containers[0]["items"]]
    assert names == ["商业会计", "金融学基础", "Accountancy"]


def test_the_b2026_rule_paragraphs_have_reviewed_wording():
    assert STRUCTURE_ZH["You must complete the following units."] == "你必须完成以下课程。"
    key = next(k for k in STRUCTURE_ZH if k.startswith("In choosing your units, you must ensure"))
    assert "第 3 级" in STRUCTURE_ZH[key]


def test_a_reply_that_echoes_the_prompt_is_not_a_translation():
    from crawler.translate.llm import acceptable_reply

    assert not acceptable_reply("Next", "GLOSSARY:\n\nTEXT:\nNext")
    assert acceptable_reply("Next", "下一页")


def test_a_stored_prompt_echo_is_not_shown_to_the_reader():
    from app.knowledge.translations import Translation, _apply
    from app.models.translation import MACHINE, ContentTranslation

    row = ContentTranslation(
        locale="zh", target_type="official_page", target_key="hurdles", field="body",
        provenance=MACHINE, data={"strings": {"Next": "GLOSSARY:\n\nTEXT:\nNext", "Back": "返回"}},
    )
    translation = Translation("zh")
    _apply(translation, row)
    assert translation.string("Next") == "Next"
    assert translation.string("Back") == "返回"


def test_assessment_names_use_the_string_table_but_numbered_labels_are_left_to_the_page():
    from app.api.serializers import _assessment_name
    from app.knowledge.translations import Translation

    tr = Translation("zh")
    tr.strings["Analytical exercise"] = "分析练习"
    tr.strings["1 - Written"] = "1 - 书面考核"
    assert _assessment_name("Analytical exercise", tr) == "分析练习"
    assert _assessment_name("1 - Written", tr) == "1 - Written"
    assert _assessment_name(None, tr) is None


def test_names_found_untranslated_on_the_degree_pages_have_wording():
    for english in ("Artificial intelligence", "Strategic marketing", "Business environment",
                    "Arts study abroad"):
        assert STRUCTURE_ZH[english], english
