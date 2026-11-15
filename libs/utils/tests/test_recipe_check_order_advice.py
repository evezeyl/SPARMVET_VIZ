"""ST13 (advice, never blocks): a position action after a step that does not fix the row order (Eve, 2026-11-15, DECIDED 4).

`polars_head`, `polars_tail`, `polars_slice`, `polars_limit`, `polars_gather_every` and `polars_with_row_index` work on the
position of a row. The checker knows an order only from what the recipe states: `maintain_order` of `polars_sort`,
`polars_unique`, `polars_group_by` and `polars_join` (a recipe must write it, so it is always known). The advice is given when
the last of these steps before the position action does not keep the order (`maintain_order: false`, or `none` for a join).
It is silent when no such step comes before (the file order is the order), when the last one fixes the order, and
when a later fixing step intervenes. Ties of `polars_top_k` / `polars_bottom_k` are NOT covered: that wording waits for a test.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_recipe_check_order_advice.py -q
"""
import copy

import pytest

from utils.recipe_check import check_recipe
from test_recipe_check import CATALOGS, valid

POSITION = ["polars_head", "polars_tail", "polars_slice", "polars_limit", "polars_gather_every", "polars_with_row_index"]
CATALOG = {**CATALOGS, "actions": {**CATALOGS["actions"], **{name: {"context": ["t1", "t2"], "params": {}} for name in
           POSITION + ["polars_sort", "polars_unique", "polars_group_by", "polars_select"]}}}


def recipe(steps, tier="tier1"):
    raw = copy.deepcopy(valid())
    raw["data_schemas"]["A"]["wrangling"] = {"tier1": []}
    raw["data_schemas"]["A"]["wrangling"][tier] = steps
    return raw


def found(raw):
    return check_recipe(raw, "run", catalogs=CATALOG)


def advice_codes(raw):
    return [p.code for p in found(raw).advices]


def step(action, **more):
    return {"action": action, **more}


UNFIXED = [step("polars_sort", maintain_order=False), step("polars_unique", maintain_order=False), step("polars_group_by", maintain_order=False)]


@pytest.mark.parametrize("position", POSITION)
@pytest.mark.parametrize("before", UNFIXED, ids=lambda s: s["action"])
def test_a_position_action_after_a_step_that_does_not_keep_the_order_gets_the_advice(before, position):
    result = found(recipe([before, step(position)]))
    assert [p.code for p in result.advices] == ["ST13"], result.problems
    assert result.errors == [] or "ST13" not in [p.code for p in result.errors]
    advice = result.advices[0]
    assert advice.severity == "A" and before["action"] in advice.message and "maintain_order" in advice.fix and position in advice.message


@pytest.mark.parametrize("before", [step("polars_sort", maintain_order=True), step("polars_unique", maintain_order=True), step("polars_group_by", maintain_order=True)],
                         ids=lambda s: s["action"])
def test_no_advice_when_the_step_before_fixes_the_order(before):
    assert "ST13" not in advice_codes(recipe([before, step("polars_head")]))


def test_no_advice_when_nothing_before_touches_the_order():
    assert "ST13" not in advice_codes(recipe([step("polars_head")]))
    assert "ST13" not in advice_codes(recipe([step("polars_select"), step("polars_head")]))


def test_a_later_step_that_fixes_the_order_silences_the_advice_and_a_later_one_that_loses_it_brings_it_back():
    assert "ST13" not in advice_codes(recipe([step("polars_unique", maintain_order=False), step("polars_sort", maintain_order=True), step("polars_head")]))
    assert "ST13" in advice_codes(recipe([step("polars_sort", maintain_order=True), step("polars_unique", maintain_order=False), step("polars_head")]))


def test_the_advice_follows_into_tier_2_and_a_step_that_is_not_a_position_action_gets_none():
    raw = recipe([step("polars_unique", maintain_order=False)])
    raw["data_schemas"]["A"]["wrangling"]["tier2"] = [step("polars_head")]
    assert "ST13" in advice_codes(raw)
    assert "ST13" not in advice_codes(recipe([step("polars_unique", maintain_order=False), step("polars_select")]))


def test_a_join_that_does_not_keep_an_order_gets_the_advice_and_one_that_does_not():
    def with_join(order):
        raw = copy.deepcopy(valid())
        raw["joins"]["AB"]["steps"]["tier1"] = [{"action": "polars_join", "right_ingredient": "B", "on": "id", "how": "left", "maintain_order": order}]
        raw["joins"]["AB"]["steps"]["tier2"] = [step("polars_head")]
        return advice_codes(raw)
    assert "ST13" in with_join("none")
    assert "ST13" not in with_join("left_right") and "ST13" not in with_join("left")


def test_the_advice_never_blocks():
    result = found(recipe([step("polars_unique", maintain_order=False), step("polars_head")]))
    assert "ST13" in [p.code for p in result.advices] and "ST13" not in [p.code for p in result.errors]


def test_the_advice_is_not_written_for_the_ties_of_top_k_and_bottom_k():
    raw = recipe([step("polars_top_k"), step("polars_bottom_k")])
    assert "ST13" not in advice_codes(raw)
