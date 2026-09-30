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
