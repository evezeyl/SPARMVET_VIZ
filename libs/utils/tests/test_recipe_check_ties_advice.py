"""ST14 (advice, never blocks): every `polars_top_k` / `polars_bottom_k` step (D42, PROVISIONAL, Eve 2026-11-15).

The checker cannot know whether ties exist in the data, so the advice is given for every such step, in short: exactly k rows,
which tied rows are kept is not fixed, how to keep always the same rows, how to keep every tied row, NaN first.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_recipe_check_ties_advice.py -q
"""
import copy

import pytest

from utils.recipe_check import check_recipe
from test_recipe_check import CATALOGS, valid

CATALOG = {**CATALOGS, "actions": {**CATALOGS["actions"], **{n: {"context": ["t1", "t2"], "params": {}} for n in ("polars_top_k", "polars_bottom_k", "polars_head")}}}


def recipe(steps):
    raw = copy.deepcopy(valid())
    raw["data_schemas"]["A"]["wrangling"] = {"tier1": steps}
    return raw


@pytest.mark.parametrize("action", ["polars_top_k", "polars_bottom_k"])
def test_every_top_k_and_bottom_k_step_gets_the_advice(action):
    result = check_recipe(recipe([{"action": action}, {"action": action}]), "run", catalogs=CATALOG)
    found = [p for p in result.advices if p.code == "ST14"]
    assert len(found) == 2 and found[0].path.endswith("[1]") and found[1].path.endswith("[2]")
    advice = found[0]
    assert advice.severity == "A" and action in advice.message and "exactly k rows" in advice.message
    assert "polars_with_row_index" in advice.fix and "polars_rank" in advice.fix and "NaN" in advice.message
    assert "ST14" not in [p.code for p in result.errors]


def test_other_steps_get_no_tie_advice():
    result = check_recipe(recipe([{"action": "polars_head"}]), "run", catalogs=CATALOG)
    assert "ST14" not in [p.code for p in result.problems]


def test_the_advice_is_shown_to_the_author():
    from app.modules.data_analysis_recipe_validator import SHOWN_ADVICES
    assert "ST14" in SHOWN_ADVICES
