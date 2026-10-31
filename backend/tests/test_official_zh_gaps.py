"""The Chinese written for the guide sentences the machine pass could not do.

No database: the seed list itself is what the deploy writes, so checking it is
enough to know each sentence keeps its facts and lands in a row of its own.
"""
from __future__ import annotations

import re

from app.knowledge.glossary import facts_kept
from app.knowledge.official_zh_gaps import OFFICIAL_ZH_GAPS
from app.knowledge.translations_seed import TRANSLATION_SEEDS
from app.models.translation import CURATED, OFFICIAL_PAGE

HAN = re.compile(r"[一-鿿]")


def test_every_rendering_keeps_its_facts_and_is_chinese():
    bad = [(slug, en) for slug, strings in OFFICIAL_ZH_GAPS.items()
           for en, zh in strings.items()
           if not facts_kept(en, zh) or not HAN.search(zh)]
    assert bad == []


def test_money_keeps_its_currency():
    # The reason most of these failed: $ read as 澳元, RM as 令吉.
    for strings in OFFICIAL_ZH_GAPS.values():
        for en, zh in strings.items():
            assert en.count("$") == zh.count("$"), en
            assert len(re.findall(r"\bRM\s?\d", en)) == len(re.findall(r"RM\s?\d", zh)), en


def test_each_guide_gets_its_own_curated_row():
    rows = {(s.target_key, s.field): s for s in TRANSLATION_SEEDS
            if s.locale == "zh" and s.target_type == OFFICIAL_PAGE}
    for slug, strings in OFFICIAL_ZH_GAPS.items():
        row = rows[(slug, "gaps")]
        assert row.provenance == CURATED
        assert row.strings == strings
        # A guide with a hand-written body keeps it as a row of its own, and
        # nothing here re-translates a sentence a person already wrote.
        body = rows.get((slug, "body"))
        if body is not None:
            assert not set(strings) & set(body.strings)
