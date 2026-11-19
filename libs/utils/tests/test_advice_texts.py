"""Every advice text of the recipe checker has the same shape (ADVICE-TEXTS-1, Eve 2026-11-15, PROVISIONAL).

The message says what happens, in one or two short plain sentences. Every remedy is a separate sentence that starts with
"Suggestion:", so that the user chooses. The advice never blocks a recipe. `top_k` / `bottom_k` (ST14) is a warning: its
message starts with "Warning:" and it is an advice (severity "A"), never an error.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_advice_texts.py -q
"""
import copy
import re

import pytest

from utils.recipe_check import check_recipe
from test_recipe_check import CATALOGS, valid
from test_recipe_check_order_advice import CATALOG as ORDER_CATALOG, recipe as order_recipe, step as order_step
from test_recipe_check_sum_advice import CATALOG as SUM_CATALOG, recipe as sum_recipe
from test_recipe_check_ties_advice import CATALOG as TIES_CATALOG, recipe as ties_recipe

SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z`'])")


def sentences(text):
    return [s for s in SENTENCE_END.split(text.strip()) if s]


def without(raw, *path):
    node = raw
    for key in path[:-1]:
        node = node[key]
    del node[path[-1]]
    return raw


def set_description(raw, text):
    raw["joins"]["AB"]["description"] = text
    return raw


def float_key():
    raw = valid()
    raw["data_schemas"]["A"]["input_fields"]["id"]["type"] = "Float64"
    raw["data_schemas"]["B"]["input_fields"]["id"]["type"] = "Float64"
    return raw


def self_join():
    raw = valid()
    raw["joins"]["AB"]["tier1"]["steps"][0]["right_ingredient"] = "A"
    return raw


# code -> (the recipe that gets the advice, the catalogs it needs)
CASES = {
    "I02": (lambda: without(valid(), "info", "description"), CATALOGS),
    "S04": (lambda: without(valid(), "data_schemas", "A", "description"), CATALOGS),
    "J03": (lambda: without(valid(), "joins", "AB", "description"), CATALOGS),
    "G02": (lambda: without(valid(), "analysis_groups", "g", "description"), CATALOGS),
    "P02": (lambda: without(valid(), "analysis_groups", "g", "plots", "p", "description"), CATALOGS),
    "J12": (self_join, CATALOGS),
    "D01": (lambda: set_description(valid(), "The join ... (issue"), CATALOGS),
    "J13": (float_key, CATALOGS),
    "ST13": (lambda: order_recipe([order_step("polars_sort", maintain_order=False), order_step("polars_head")]), ORDER_CATALOG),
    "ST14": (lambda: ties_recipe([{"action": "polars_top_k"}]), TIES_CATALOG),
    "ST15": (lambda: sum_recipe([{"action": "polars_sum"}]), SUM_CATALOG),
}


def advices(code):
    build, catalogs = CASES[code]
    return [p for p in check_recipe(copy.deepcopy(build()), "run", catalogs=catalogs).advices if p.code == code]


@pytest.mark.parametrize("code", sorted(CASES))
def test_the_advice_is_found_and_never_an_error(code):
    found = advices(code)
    assert found and all(p.severity == "A" for p in found)


@pytest.mark.parametrize("code", sorted(CASES))
def test_the_message_says_what_happens_and_holds_no_remedy(code):
    for p in advices(code):
        assert "Suggestion" not in p.message
        assert len(sentences(p.message)) <= (4 if code == "ST14" else 2), (code, p.message)


@pytest.mark.parametrize("code", sorted(CASES))
def test_every_remedy_starts_with_suggestion(code):
    for p in advices(code):
        assert p.fix.startswith("Suggestion: "), (code, p.fix)
        for part in sentences(p.fix):
            assert part.startswith("Suggestion: "), (code, part)


def test_the_tie_advice_reads_as_a_warning_and_gives_both_remedies():
    p = advices("ST14")[0]
    assert p.message.startswith("Warning: ") and p.severity == "A"
    assert len(re.findall("Suggestion:", p.fix)) == 2
    assert "polars_with_row_index" in p.fix and "last `by` column" in p.fix
    assert "polars_rank" in p.fix and "`min`" in p.fix and "more than k rows" in p.fix


def test_the_shape_check_can_fail():
    """The shape rules reject a remedy in the old form and a message with a remedy in it."""
    class Old:
        fix, message = "write it (spec section 13)", "The plot has no description. Suggestion: write it."
    assert not Old.fix.startswith("Suggestion: ") and "Suggestion" in Old.message
    assert len(sentences("One. Two. Three.")) == 3 and len(sentences("A `x` rule. It holds.")) == 2


def test_the_float64_remedy_of_st15_says_what_it_costs():
    p = advices("ST15")[0]
    assert "Int64" in p.fix and "Float64" in p.fix and "15 to 16 exact digits" in p.fix and "lose their last digits" in p.fix
