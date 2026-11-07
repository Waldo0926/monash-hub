"""Time boundaries and three-valued requisite logic, without a database."""
import pytest
from app.handbook.plan import Slot, _evaluate
from app.models.handbook import UnitRequisiteGroup, UnitRequisiteItem

S1 = "First semester"
S2 = "Second semester"


def rule(connector, *codes, children=()):
    return UnitRequisiteGroup(
        requisite_type="prerequisite", connector=connector,
        items=[UnitRequisiteItem(item_code=code) for code in codes],
        children=list(children),
    )


@pytest.mark.parametrize("period", [S1, S2, "Winter semester", "Full year"])
@pytest.mark.parametrize("target", ["Full year", "Full year extended"])
def test_same_year_units_have_not_finished_before_a_full_year_unit(period, target):
    assert not Slot(2026, period).finishes_before(Slot(2026, target))
    assert Slot(2025, period).finishes_before(Slot(2026, target))


def test_text_rule_is_unknown_even_when_its_referenced_unit_is_present():
    result = _evaluate(rule("TEXT", "AAA1001"), {"AAA1001": Slot(2026, S1)}, Slot(2026, S2))
    assert result.unverified and not result.satisfied and result.unmet is None


def test_unknown_or_alternative_does_not_prove_success_or_a_definite_gap():
    result = _evaluate(rule("OR", "BBB1001", children=[rule("TEXT")]), {}, Slot(2026, S2))
    assert result.unverified and not result.satisfied and result.unmet is None


def test_proven_or_alternative_is_enough_even_with_an_unknown_branch():
    result = _evaluate(
        rule("OR", "AAA1001", children=[rule("TEXT")]),
        {"AAA1001": Slot(2026, S1)}, Slot(2026, S2),
    )
    assert result.satisfied and not result.unverified


def test_and_keeps_both_a_proven_gap_and_an_unverified_requirement():
    result = _evaluate(rule("AND", "BBB1001", children=[rule("TEXT")]), {}, Slot(2026, S2))
    assert result.unverified and not result.satisfied
    assert result.unmet.flatten() == ["BBB1001"]


def test_known_nested_rules_still_report_their_missing_branch():
    result = _evaluate(
        rule("AND", children=[rule("OR", "AAA1001", "AAA1002"), rule("AND", "BBB1001")]),
        {"AAA1002": Slot(2026, S1)}, Slot(2026, S2),
    )
    assert not result.unverified
    assert result.unmet.flatten() == ["BBB1001"]


def test_unknown_condition_does_not_rescue_an_or_branch_with_a_proven_gap():
    result = _evaluate(
        rule("OR", "CCC1001", children=[rule("AND", "BBB1001", children=[rule("TEXT")])]),
        {}, Slot(2026, S2),
    )
    assert not result.satisfied and result.unverified
    assert result.unmet.connector == "OR"
    assert set(result.unmet.flatten()) == {"BBB1001", "CCC1001"}
