"""Folding a query into the form the index is written in.

Two things students type that the index never contains:

**Full-width characters.** A Chinese input method left in full-width mode
types ＦＩＴ２００４ and ending punctuation like ？. The unit code pattern only
accepts ASCII on purpose, so ＦＩＴ２００４ found no unit, and the same IME
habit turns "census date" into ｃｅｎｓｕｓ ｄａｔｅ. NFKC turns all of it
back into ASCII before anything else reads the query.

**Traditional characters.** Students from Hong Kong, Taiwan and Macau write
簽證 and 畢業, and every Chinese string we hold - the search synonyms, the
glossary, the translated pages - is Simplified. A character-level map is
enough for search: 簽證 becomes 签证 and matches. Converting a sentence for
display would need phrase rules (OpenCC has them); matching does not.

The same fold is applied to both sides wherever a query is compared with a
curated word list, so a Japanese keyword like 試験 is folded the same way as
the Japanese query it has to meet.
"""
from __future__ import annotations

import re
import unicodedata
from functools import lru_cache

from app.search.t2s_data import SIMPLIFIED, TRADITIONAL

_T2S = str.maketrans(TRADITIONAL, SIMPLIFIED)
_SPACES = re.compile(r"\s+")


@lru_cache(maxsize=4096)
def fold(text: str | None) -> str:
    """``text`` in half-width, Simplified form, with single spaces.

    Case is left alone: callers that care already lower-case, and a unit code
    is upper-cased where it is extracted.
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text).translate(_T2S)
    return _SPACES.sub(" ", text).strip()
