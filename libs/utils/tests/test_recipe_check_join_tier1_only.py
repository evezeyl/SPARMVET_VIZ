"""A `polars_join` that writes `validate` can only stand in tier 1 (ST05), so the plain validate message needs no tier-2 or tier-3 path.

The checker refuses a join action in any tier but tier1 (`recipe_check.py`, `steps()`:
`if tier in ("tier2", "tier3") and step.get("action") in tier1_only: self.add("ST05", ...)`; `TIER1_ONLY` of `utils.action_names`
holds JOIN, JOIN_ASOF and JOIN_WHERE). This pins the refusal for the three places a tier-2 or tier-3 list exists: the tier 2 of a join,
the tier 2 of a schema plotted directly, and the tier 3 of a plot. The engine side: only the assembler runs joins, and it runs tier 1.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_recipe_check_join_tier1_only.py -q
"""
import copy

import pytest

from utils.recipe_check import check_recipe
from test_recipe_check import CATALOGS, valid

JOIN = {"action": "polars_join", "right_ingredient": "B", "on": "id", "how": "left", "validate": "m:1"}


def codes(raw):
    return [p.code for p in check_recipe(raw, "run", catalogs=CATALOGS).problems]


def test_a_join_with_validate_in_tier2_of_a_join_is_refused():
    raw = copy.deepcopy(valid())
    raw["joins"]["AB"]["steps"]["tier2"] = [dict(JOIN)]
    assert "ST05" in codes(raw)


def test_a_join_with_validate_in_tier2_of_a_schema_is_refused():
    raw = copy.deepcopy(valid())
    raw["data_schemas"]["A"]["wrangling"]["tier2"] = [dict(JOIN)]
    assert "ST05" in codes(raw)


def test_a_join_with_validate_in_tier3_of_a_plot_is_refused():
    raw = copy.deepcopy(valid())
    raw["analysis_groups"]["g"]["plots"]["p"]["steps"] = {"tier3": [dict(JOIN)]}
    assert "ST05" in codes(raw)


def test_the_same_join_in_tier1_is_not_refused_for_its_tier():
    raw = copy.deepcopy(valid())
    raw["joins"]["AB"]["steps"]["tier1"] = [dict(JOIN)]
    assert "ST05" not in codes(raw)
