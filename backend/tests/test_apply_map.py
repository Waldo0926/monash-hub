"""Applying a map of renderings must never make a stored row worse."""
from __future__ import annotations

from app.knowledge.structure_zh import STRUCTURE_ZH
from app.models.translation import ContentTranslation

from crawler.translate.apply_map import acceptable, apply


def row(strings):
    return ContentTranslation(
        locale="zh", target_type="course", target_key="X", field="content",
        provenance="machine", data={"strings": strings}, translator="machine:argos+glossary",
    )


def test_a_good_rendering_replaces_the_stored_one():
    r = row({"You must complete ENG1005 (6 credit points)": "旧"})
    out = apply([r], {"You must complete ENG1005 (6 credit points)": "你必须完成 ENG1005（6 学分）"})
    assert out == {"rows": 1, "replaced": 1, "refused": 0}
    assert r.data["strings"]["You must complete ENG1005 (6 credit points)"].startswith("你必须")
    assert r.translator == "machine:google+glossary"


def test_a_rendering_that_lost_a_number_or_a_code_is_refused():
    assert not acceptable("Complete 24 credit points", "完成学分")
    assert not acceptable("Complete ENG1005", "完成该课程")
    assert acceptable("Complete 24 credit points", "完成 24 学分")


def test_a_known_wrong_word_is_refused():
    assert not acceptable("Breadth studies", "面包研究")
    assert not acceptable("Anything", "Zqa 残留")


def test_an_empty_or_unchanged_rendering_is_refused():
    assert not acceptable("Hello", "")
    assert not acceptable("Hello", "Hello")


def test_reviewed_wording_and_unknown_strings_are_left_alone():
    reviewed = next(iter(STRUCTURE_ZH))
    r = row({reviewed: "机翻", "Not in the map": "旧"})
    out = apply([r], {reviewed: "别的译文", "Something else": "其他"})
    assert out["replaced"] == 0 and out["rows"] == 0
    assert r.data["strings"][reviewed] == "机翻"
    assert r.translator == "machine:argos+glossary"


def test_failed_strings_can_be_added_to_one_shared_machine_row():
    from crawler.translate.apply_map import add_global

    class FakeDb:
        def __init__(self):
            self.added = []

        def scalar(self, _stmt):
            return None

        def add(self, row):
            self.added.append(row)

    db = FakeDb()
    count = add_global(db, {"Analyse the market (3 methods)": "分析市场（3 种方法）", "x": ""})
    assert count == 1
    row = db.added[0]
    assert row.target_type == "global" and row.target_key == "handbook"
    assert row.provenance == "machine" and row.field == "retried"
    assert row.data["strings"] == {"Analyse the market (3 methods)": "分析市场（3 种方法）"}
