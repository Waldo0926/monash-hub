"""Money in translations: the amount and its currency are not the model's to change.

The Malaysia printing page charges "RM1.10 per page / per side". The chat model
published that as 每页/每面 1.10 澳元: the right number, so the number check
passed it, in Australian dollars.
"""
from __future__ import annotations

import threading

import pytest
from app.knowledge import translations
from app.knowledge.glossary import currencies_kept, protect, restore
from app.models.translation import HUMAN, MACHINE, OFFICIAL_PAGE, PUBLISHED, ContentTranslation

from crawler.translate.engine import Translator, stored_ok
from crawler.translate.llm import faithful


@pytest.mark.parametrize("source, translated", [
    ("RM1.10 per page / per side", "每页/每面 1.10 澳元"),
    ("RM1.10 per page / per side", "每页/每面 1.10 元"),
    ("RM1.10 per page / per side", "每页/每面 1.10 美元"),
    ("The fee is RM 300", "费用为 300 澳元"),
    ("Fees are in MYR", "费用以澳元计"),
    ("A$50 on a prepaid card", "预付卡 50 令吉"),
    ("up to $50 on a prepaid card", "预付卡最多 50 美元"),
    # A Malaysia fee table with the currency in its header, given Australian dollars.
    ("Master of Digital Business 66,960 (full course)", "数字商务硕士 66,960澳元（全日制）"),
])
def test_another_currency_or_none_is_not_kept(source, translated):
    assert not currencies_kept(source, translated)


@pytest.mark.parametrize("source, translated", [
    ("RM1.10 per page / per side", "每页/每面 RM1.10"),
    ("i.e. RM 0.16 for double sided", "即双面黑白 RM 0.16"),
    ("The Special Pass fee of RM300", "RM300 特别准证费用"),
    ("up to $50 on a prepaid card", "预付卡最多 50 澳元"),
    ("up to $50 on a prepaid card", "预付卡最多 $50"),
    ("Paid in ringgit", "以令吉支付"),
    ("Amenities Fee (RM)", "设施费（林吉特）"),
    ("despite the billions of dollars invested through foreign aid", "尽管投入了数十亿美元的外国援助"),
    # Not money: a room, a university, a company, a word, a number with no currency.
    ("Room RM2 at RMIT", "RMIT 的 RM2 室"),
    ("Intelligence Analyst, S-RM", "情报分析师，S-RM"),
    ("a move towards de-dollarisation", "走向去美元化"),
    ("WES will continue to show withdrawn units for aud", "WES 会继续显示已退的课程"),
    ("Print 20 pages", "打印 20 页"),
])
def test_the_same_currency_is_kept(source, translated):
    assert currencies_kept(source, translated)


def test_an_amount_never_reaches_the_model():
    masked, kept = protect("A4 Colour costs RM1.10 per page", "zh")
    assert "RM1.10" not in masked and "1.10" not in masked
    assert "RM1.10" in restore(masked, kept)
    masked, kept = protect("a fee of RM 45,000 and A$50", "zh")
    assert "45,000" not in masked and "50" not in masked
    assert {"RM 45,000", "A$50"} <= set(kept)
    masked, kept = protect("at least $13 billion per year", "zh")
    assert kept == ["$13 billion"]


def test_the_chat_models_reply_in_another_currency_is_not_faithful():
    assert not faithful("RM1.10 per page / per side", "每页/每面 1.10 澳元", [])
    assert faithful("RM1.10 per page / per side", "每页/每面 RM1.10", [])


def _engine(reply):
    engine = Translator.__new__(Translator)
    engine.locale, engine._cache, engine._renderings = "zh", {}, {}
    engine._lock = threading.Lock()
    engine._translate = lambda text: reply(text)
    return engine


def test_a_translation_in_another_currency_is_left_in_english():
    # Whatever the model does with the placeholder, 澳元 next to it is not used.
    out = _engine(lambda text: text.replace("per page / per side", "每页/每面") + " 澳元").text(
        "RM1.10 per page / per side"
    )
    assert out is None


def test_a_stored_translation_in_another_currency_is_translated_again():
    assert not stored_ok("RM1.10 per page / per side", "每页/每面 1.10 澳元")
    assert stored_ok("RM1.10 per page / per side", "每页/每面 RM1.10")
    engine = _engine(lambda text: "不该用到")
    engine.prime({"RM1.10 per page / per side": "每页/每面 1.10 澳元"})
    assert "RM1.10 per page / per side" not in engine._cache


def test_a_machine_string_in_another_currency_is_read_as_the_english():
    tr = translations.Translation("zh")
    strings = {"RM1.10 per page / per side": "每页/每面 1.10 澳元",
               "RM0.08 per page / per side": "每页/每面 RM0.08"}
    translations._apply(tr, ContentTranslation(
        locale="zh", target_type=OFFICIAL_PAGE, target_key="p", field="content",
        provenance=MACHINE, status=PUBLISHED, data={"strings": strings}))
    assert tr.string("RM1.10 per page / per side") == "RM1.10 per page / per side"
    assert tr.string("RM0.08 per page / per side") == "每页/每面 RM0.08"


def test_a_persons_wording_is_not_second_guessed():
    tr = translations.Translation("zh")
    translations._apply(tr, ContentTranslation(
        locale="zh", target_type=OFFICIAL_PAGE, target_key="p", field="content",
        provenance=HUMAN, status=PUBLISHED, data={"strings": {"Pay A$50": "支付 50 澳币"}}))
    assert tr.string("Pay A$50") == "支付 50 澳币"


def test_every_reviewed_translation_keeps_its_currency():
    from app.knowledge.translations_seed import TRANSLATION_SEEDS

    bad = [(en, zh) for seed in TRANSLATION_SEEDS for en, zh in seed.strings.items()
           if not currencies_kept(en, zh)]
    assert bad == []
