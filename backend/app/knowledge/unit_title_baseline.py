"""Complete Simplified-Chinese baseline for 2026 Handbook unit titles.

``unit_titles_zh.json`` contains one translation for every distinct English
title in the production 2026 catalogue (4,212 source titles covering 5,228
unit records).  The baseline was generated with Google Translate on
2026-08-30, then checked for missing, shifted and known-bad renderings.  It is
still machine provenance: exact corrections in ``titles.ZH_TITLE_OVERRIDES``
are the human-reviewed layer and always win when translations are loaded.

Keeping the complete baseline in the repository makes the Chinese catalogue
deterministic.  A deploy never depends on a live translation request, and a
change to any title is visible in a pull-request diff.
"""
from __future__ import annotations

import json
from pathlib import Path

_PATH = Path(__file__).with_name("unit_titles_zh.json")
ZH_TITLE_BASELINE: dict[str, str] = json.loads(_PATH.read_text(encoding="utf-8"))

if len(ZH_TITLE_BASELINE) != 4212 or any(
    not key or not value for key, value in ZH_TITLE_BASELINE.items()
):
    raise ValueError("unit title baseline must contain 4,212 non-empty translations")
