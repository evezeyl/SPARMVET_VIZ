"""A join of a table with itself is a warning, never an error (D-0183, D-0050, D-0099).

Eve 2026-11-16: "No error in Polars, then no error for us; a warning / caution is good." and "A self-join (a table joined with
itself, the anti-join on the same key included) gives a warning, never an error." Polars reports nothing for it, and the result
of an anti-join of a table with itself is not always empty: it is the rows whose key is missing, because a missing key never matches.

One function decides (`utils.join_keys.self_join`), one function writes the text (`self_join_text`); the checker (J12, before any
data is read) and the build (with the row numbers, `libs/transformer/tests/test_self_join_build.py`) ask the same two. This file
tests the rule, the text and the checker. Every case with the real catalogs is in `app/tests/test_every_self_join_gets_a_message.py`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_self_join_rule.py -q
"""
import re

import pytest

from utils import action_names
from utils.recipe_check import check_recipe
from utils.join_keys import JOIN_ACTIONS, self_join, self_join_text
from test_recipe_check import CATALOGS, valid

# the catalog of the unit tests knows only `how: left` and `inner`; a self-join of any kind is written with the real list
ALL_HOW = {**CATALOGS, "actions": {**CATALOGS["actions"], "polars_join": {**CATALOGS["actions"]["polars_join"], "params": {
    **CATALOGS["actions"]["polars_join"]["params"],
    "how": {"widget": "enum", "options": ["left", "inner", "semi", "anti", "full", "cross", "right"], "required": True},
    "nulls_equal": {"widget": "bool", "required": False}}}}}


def check(raw):
    return check_recipe(raw, "run", catalogs=ALL_HOW)

SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z`'])")


def join(right="A", how="anti", **keys):
    return {"action": action_names.JOIN, "right_ingredient": right, "how": how, **({"on": ["id"]} if not keys else keys)}


# -- the rule itself ----------------------------------------------------------------------------

def test_the_anti_join_of_the_base_table_on_the_same_key_is_a_self_join_and_the_table_itself():
    found = self_join("A", [], join())
    assert found["table"] == "A" and found["how"] == "anti" and found["same_key"] and found["base_itself"]
    assert found["left_keys"] == found["right_keys"] == ["id"] and found["key_columns"] == (["id"], ["id"])


@pytest.mark.parametrize("how", ["left", "inner", "semi", "anti", "full", "cross", "right"])
def test_every_kind_of_join_with_the_base_table_is_a_self_join(how):
    assert self_join("A", [], join(how=how)) is not None


def test_the_default_how_of_polars_join_is_left():
    assert self_join("A", [], {k: v for k, v in join().items() if k != "how"})["how"] == "left"


def test_a_join_with_another_table_is_not_a_self_join():
    assert self_join("A", [], join(right="B")) is None


def test_a_table_joined_by_an_earlier_step_is_held_by_the_table_being_joined():
    found = self_join("A", [join(right="B", how="left")], join(right="B"))
    assert found is not None and found["table"] == "B" and not found["base_itself"]


def test_other_key_columns_are_a_self_join_too():
    """Before D-0183 this got no message at all."""
    found = self_join("A", [], join(how="left", left_on=["parent"], right_on=["id"]))
    assert found is not None and not found["same_key"] and found["key_columns"] == (["parent"], ["id"])


@pytest.mark.parametrize("action", sorted(JOIN_ACTIONS))
def test_every_join_step_of_the_engine_is_covered(action):
    assert self_join("A", [], {"action": action, "right_ingredient": "A", "on": ["id"]}) is not None


def test_the_join_actions_are_the_three_that_name_a_right_table():
    assert set(JOIN_ACTIONS) == {action_names.JOIN, action_names.JOIN_ASOF, action_names.JOIN_WHERE}


def test_a_step_that_is_not_a_join_is_never_a_self_join():
    assert self_join("A", [], {"action": action_names.FILTER, "right_ingredient": "A"}) is None
    assert self_join("A", [], {"action": action_names.JOIN}) is None   # no right table: J05 says so


def test_the_as_of_join_counts_its_by_columns_as_key_columns():
    step = {"action": action_names.JOIN_ASOF, "right_ingredient": "A", "on": ["t"], "by": ["site"], "strategy": "backward"}
    found = self_join("A", [], step)
    assert found["key_columns"] == (["t", "site"], ["t", "site"]) and found["how"] is None and not found["base_itself"]


def test_a_join_on_conditions_has_no_key_columns():
    found = self_join("A", [], {"action": action_names.JOIN_WHERE, "right_ingredient": "A", "predicates": ["pl.col('x') > 1"]})
    assert found["key_columns"] == ([], []) and not found["same_key"]


def test_the_same_key_written_as_left_on_and_right_on_is_the_same_key():
    assert self_join("A", [], join(left_on="id", right_on="id"))["same_key"]


def test_an_unquoted_on_is_read_like_the_checker_reads_it():
    step = {"action": action_names.JOIN, "right_ingredient": "A", "how": "anti", True: ["id"]}
    assert self_join("A", [], step)["same_key"]


@pytest.mark.parametrize("keys", [{"on": 5}, {"on": [1, 2]}, {"left_on": ["a"], "right_on": [{"x": 1}]}])
def test_a_key_that_is_not_a_name_never_raises_and_is_not_decided_here(keys):
    assert self_join("A", [], {"action": action_names.JOIN, "right_ingredient": "A", "how": "anti", **keys}) is None


def test_composite_keys_in_another_order_are_not_the_same_key():
    found = self_join("A", [], join(left_on=["a", "b"], right_on=["b", "a"]))
    assert found is not None and not found["same_key"] and not found["base_itself"]


# -- when the table at the step is still the base table itself ------------------------------------

@pytest.mark.parametrize("before", [
    {"action": action_names.HEAD, "n": 3},
    {"action": action_names.REMOVE, "predicates": ["pl.col('v') < 2"]},
    {"action": action_names.FILTER},
    {"action": action_names.WITH_COLUMNS, "named_exprs": {"double": "pl.col('v') * 2"}},
    {"action": action_names.RENAME, "mapping": {"v": "value"}},
    join(right="B", how="left"),
], ids=["head", "remove", "filter", "with_columns another column", "rename another column", "left join of B"])
def test_a_step_that_removes_rows_or_writes_other_columns_keeps_the_table_itself(before):
    assert self_join("A", [before], join())["base_itself"]


@pytest.mark.parametrize("before", [
    {"action": action_names.WITH_COLUMNS, "named_exprs": {"id": "pl.col('id').str.to_uppercase()"}},
    {"action": action_names.RENAME, "mapping": {"id": "key"}},
    {"action": action_names.RENAME, "mapping": {"other": "id"}},
    {"action": action_names.WITH_COLUMNS, "named_exprs": "not a mapping"},
    {"action": action_names.RENAME},
    join(right="B", how="full"),
    join(right="B", how="right"),
    "not a step",
], ids=["writes the key", "renames the key", "renames onto the key", "unreadable with_columns", "unreadable rename", "full join", "right join", "no step"])
def test_after_a_step_that_may_give_other_keys_it_is_a_self_join_but_not_the_table_itself(before):
    found = self_join("A", [before], join())
    assert found is not None and not found["base_itself"]


# -- the text: one function writes it ------------------------------------------------------------

def sentences(text):
    return [s for s in SENTENCE_END.split(text.strip()) if s]


def test_the_anti_join_text_says_the_true_thing_about_the_rows():
    what, fix = self_join_text(self_join("A", [], join()))
    assert "keeps only the rows whose key is missing" in what and "a missing key never matches" in what
    assert "If no row has a missing key, the result is empty" in what
    assert "no row that has a key" not in what   # the sentence of the error that D-0183 replaced
    assert fix.startswith("Suggestion:") and fix.count("Suggestion:") == 2


def test_with_nulls_equal_a_missing_key_matches_and_the_text_says_so():
    step = join(nulls_equal=True, on=["id"])
    what, _ = self_join_text(self_join("A", [], step))
    assert "keeps no row" in what and "a missing key included" in what and "never matches" not in what


@pytest.mark.parametrize("step", [join(how="left"), join(how="inner"), join(how="semi"), join(how="anti", left_on=["p"], right_on=["id"]),
                                  {"action": action_names.JOIN_ASOF, "right_ingredient": "A", "on": ["t"]},
                                  {"action": action_names.JOIN_WHERE, "right_ingredient": "A", "predicates": ["x"]}])
def test_every_text_has_the_shape_what_happens_then_suggestions(step):
    what, fix = self_join_text(self_join("A", [], step))
    assert "Suggestion" not in what and len(sentences(what)) <= 2   # how the two become one sentence: test_with_fix_one_period.py
    assert fix.startswith("Suggestion: ") and all(part.startswith("Suggestion: ") for part in sentences(fix))


def test_the_numbers_of_the_build_are_one_last_sentence():
    found = self_join("A", [], join())
    what, _ = self_join_text(found, {"before": 5, "after": 1, "missing_left": 1, "missing_right": 1})
    assert "Rows before the join: 5; rows after: 1; rows with a missing key in ['id']: 1 in the table at this step and 1 in 'A'" in what
    assert what.startswith(self_join_text(found)[0] + ". ")


def test_a_join_on_conditions_gives_rows_before_and_after_only():
    found = self_join("A", [], {"action": action_names.JOIN_WHERE, "right_ingredient": "A", "predicates": ["x"]})
    what, _ = self_join_text(found, {"before": 5, "after": 7, "missing_left": None, "missing_right": None})
    assert what.endswith("Rows before the join: 5; rows after: 7") and "missing key" not in what


# -- the checker: J12 for every self-join, never an error ----------------------------------------

def codes(raw, code):
    return [p for p in check(raw).problems if p.code == code]


def recipe(**step):
    raw = valid()
    raw["joins"]["AB"]["tier1"]["steps"][0].update(right_ingredient="A", **step)
    return raw


def test_the_anti_join_of_a_table_with_itself_is_an_advice_and_the_recipe_still_passes():
    raw = recipe(how="anti")
    problems = codes(raw, "J12")
    assert len(problems) == 1 and problems[0].severity == "A" and problems[0].path == "joins.AB.tier1.steps[1]"
    assert "keeps only the rows whose key is missing" in problems[0].message
    assert problems[0].fix.startswith("Suggestion:")
    assert check(raw).ok and check(raw).errors == []


def test_no_code_of_the_checker_is_called_j15_any_more():
    import utils.recipe_check as recipe_check
    assert "J15" not in open(recipe_check.__file__).read()
    assert all(p.code != "J15" for p in check(recipe(how="anti")).problems)


@pytest.mark.parametrize("how", ["anti", "left", "inner", "semi", "full", "cross"])
def test_no_self_join_is_refused_whatever_the_kind(how):
    assert check(recipe(how=how)).ok


def test_a_self_join_on_other_keys_is_advised_too():
    raw = valid()
    raw["data_schemas"]["A"]["input_fields"]["parent"] = {"type": "String"}
    step = raw["joins"]["AB"]["tier1"]["steps"][0]
    step.pop("on")
    step.update(right_ingredient="A", left_on="parent", right_on="id", how="left")
    problems = codes(raw, "J12")
    assert len(problems) == 1 and "left key ['parent'] and the right key ['id']" in problems[0].message
    assert check(raw).ok


def test_the_advice_is_given_once_when_a_step_before_may_change_the_key():
    raw = recipe(how="anti")
    raw["joins"]["AB"]["tier1"]["steps"].insert(0, {"action": action_names.WITH_COLUMNS, "named_exprs": {"id": "pl.col('id')"}})
    assert len(codes(raw, "J12")) == 1


def test_a_join_with_another_table_gets_no_advice():
    assert codes(valid(), "J12") == []
