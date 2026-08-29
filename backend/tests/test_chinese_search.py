"""Searching in Chinese.

The site reads as Chinese and the search box did not: 休学 returned nothing on a
site with a page about intermission. These tests are about the two mechanisms
that fix that, and about the one thing neither of them may do - stop English
working.
"""
from __future__ import annotations

import pytest
from app.models.handbook import Unit
from app.models.knowledge import OfficialPage, OfficialSource
from app.models.translation import OFFICIAL_PAGE, PUBLISHED, UNIT, ContentTranslation
from app.search import service
from app.search.chinese import expand, expanded_query, has_cjk
from app.search.reindex_zh import reindex_official, reindex_units

# --- what counts as a Chinese query ---------------------------------------

@pytest.mark.parametrize(
    "term,expected",
    [
        ("休学", True),
        ("census date", False),
        ("FIT1008", False),
        ("FIT1008 先修", True),
        ("", False),
        ("2026", False),
    ],
)
def test_cjk_detection(term, expected):
    assert has_cjk(term) is expected


# --- the glossary as a search index ---------------------------------------

@pytest.mark.parametrize(
    "term,english",
    [
        ("休学", "intermission"),
        ("学籍统计日是什么", "census date"),
        ("怎么申请特殊考虑", "special consideration"),
    ],
)
def test_a_chinese_term_expands_to_the_english_it_translates(term, english):
    """This is what makes Chinese search work on pages nobody translated.

    The reverse index is built from the glossary, so a term added for the
    translator becomes searchable the same day without a second list to keep.
    """
    assert english in expand(term)


def test_the_longest_run_wins():
    """Otherwise a term expands to itself and to a fragment inside it, and the
    fragment drags in every page that mentions the general subject."""
    found = expand("学籍统计日")
    assert "census date" in found
    assert len(found) == 1


def test_english_is_never_expanded():
    assert expand("census date") == []
    assert expanded_query("census date") == "census date"


def test_the_chinese_stays_in_the_expanded_query():
    """Stripping it would make a Chinese-only query empty, and an empty tsquery
    matches everything."""
    expanded = expanded_query("休学")
    assert "休学" in expanded
    assert "intermission" in expanded


# --- the indexed text -----------------------------------------------------

def _unit(db, code="FIT1008", title="Fundamentals of algorithms"):
    unit = Unit(
        unit_code=code, academic_year=2026, title=title, is_active=True,
        source_url=f"https://handbook.monash.edu/2026/units/{code}",
        content_hash=f"hash-{code}",
    )
    db.add(unit)
    db.commit()
    return unit


def _page(db, slug="intermission", title="Intermission (study leave)"):
    source = OfficialSource(key="monash-students", name="Monash", base_url="https://x.invalid")
    db.add(source)
    db.flush()
    page = OfficialPage(
        source_id=source.id, slug=slug, canonical_url=f"https://x.invalid/{slug}",
        title=title, category="enrolment", status="ok", tags=[],
    )
    db.add(page)
    db.commit()
    return page


def _translate(db, target_type, key, strings):
    db.add(ContentTranslation(
        locale="zh", target_type=target_type, target_key=key, field="body",
        status=PUBLISHED, data={"strings": strings},
    ))
    db.commit()


def test_reindex_copies_the_translation_onto_the_row(db):
    unit = _unit(db)
    _translate(db, UNIT, "FIT1008", {"Data structures and algorithms": "数据结构与算法"})

    changed, total = reindex_units(db)
    db.commit()
    assert (changed, total) == (1, 1)
    db.refresh(unit)
    assert "数据结构与算法" in unit.search_zh


def test_reindex_stores_no_english(db):
    """The English is already in search_vector; a second copy here would make
    search_zh match English queries and double-rank them."""
    unit = _unit(db)
    _translate(db, UNIT, "FIT1008", {
        "Data structures": "数据结构",
        "Assessment details may change.": "Assessment details may change.",
    })

    reindex_units(db)
    db.commit()
    db.refresh(unit)
    assert "数据结构" in unit.search_zh
    assert "Assessment" not in unit.search_zh


def test_reindex_is_idempotent(db):
    _unit(db)
    _translate(db, UNIT, "FIT1008", {"Algorithms": "算法"})

    assert reindex_units(db)[0] == 1
    db.commit()
    # Nothing changed upstream, so nothing is rewritten.
    assert reindex_units(db)[0] == 0


def test_reindex_clears_a_row_whose_translation_went_away(db):
    unit = _unit(db)
    unit.search_zh = "旧的译文"
    db.commit()

    reindex_units(db)
    db.commit()
    db.refresh(unit)
    assert unit.search_zh is None


def test_a_repeated_string_is_stored_once(db):
    page = _page(db)
    _translate(db, OFFICIAL_PAGE, "intermission", {
        "High distinction": "高分优秀", "HD": "高分优秀", "Grade": "高分优秀",
    })
    reindex_official(db)
    db.commit()
    db.refresh(page)
    assert page.search_zh.count("高分优秀") == 1


# --- searching ------------------------------------------------------------

def test_a_chinese_query_finds_a_unit_by_its_translation(db):
    _unit(db)
    _translate(db, UNIT, "FIT1008", {"Data structures and algorithms": "数据结构与算法"})
    reindex_units(db)
    db.commit()

    found, total = service.search_units(db, "数据结构", year=2026)
    assert total == 1
    assert found[0].unit_code == "FIT1008"


def test_a_chinese_query_finds_a_page_through_the_glossary_alone(db):
    """No translation stored at all - the expansion does the work.

    This is the case that matters most, because it covers every page nobody has
    got round to translating.
    """
    _page(db, slug="intermission", title="Intermission (study leave)")

    found, total = service.search_official(db, "休学")
    assert total == 1
    assert found[0].slug == "intermission"


def test_a_chinese_query_finds_a_page_by_its_translated_body(db):
    _page(db, slug="fees", title="Fees")
    _translate(db, OFFICIAL_PAGE, "fees", {
        "You may be eligible for a refund": "你可能有资格申请退款",
    })
    reindex_official(db)
    db.commit()

    found, total = service.search_official(db, "退款")
    assert total == 1
    assert found[0].slug == "fees"


def test_an_untranslated_unit_is_not_found_by_chinese_prose(db):
    """No translation and no glossary term means no match - not a guess."""
    _unit(db, code="FIT9999", title="Something nobody translated")

    _found, total = service.search_units(db, "数据结构", year=2026)
    assert total == 0


def test_english_search_still_works_unchanged(db):
    _unit(db, code="FIT1008", title="Fundamentals of algorithms")
    _translate(db, UNIT, "FIT1008", {"Algorithms": "算法"})
    reindex_units(db)
    db.commit()

    found, total = service.search_units(db, "algorithms", year=2026)
    assert total == 1
    assert found[0].unit_code == "FIT1008"


def test_a_unit_code_still_wins_over_everything(db):
    _unit(db, code="FIT1008")
    _unit(db, code="FIT2004", title="Algorithms and data structures")

    found, _total = service.search_units(db, "FIT1008", year=2026)
    assert found[0].unit_code == "FIT1008"


def test_a_chinese_query_does_not_break_the_empty_case(db):
    _unit(db)
    found, total = service.search_units(db, "", year=2026)
    assert total == 1 and len(found) == 1
