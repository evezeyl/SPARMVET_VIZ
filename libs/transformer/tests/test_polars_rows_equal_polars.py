"""The ten `polars_` actions of the group "rows" equal the direct Polars call (tests first, Eve 2026-11-14).

Same design as `test_polars_actions_equal_polars.py` (each case: the action, its step, a probe frame, the direct Polars
call): `head`, `tail`, `slice`, `limit`, `top_k`, `bottom_k`, `reverse`, `gather_every`, `with_row_index`, `remove`.
They live in a file of their own so that the actions of the other groups can grow the main file without conflict.
`test_action_recipe_pairs.py` lists this file in `OWN_TESTS` for the ten actions.

What is checked:
  - the action gives the same rows, in the same order, with the same schema as the Polars call;
  - the 1:1:1 pair of every action (recipe + TSV) read through the real path equals the case (the file layer loses nothing);
  - what the actions refuse: a missing required parameter (`n`, `name`, `k`, `by`, `predicates`), an unknown key, a wrong
    form, an empty list of predicates, a formula that is not safe.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_polars_rows_equal_polars.py -q
"""
import polars as pl
import pytest
from polars.testing import assert_frame_equal

import transformer.actions  # noqa: F401
from transformer.actions.base import ACTION_SCHEMAS, AVAILABLE_WRANGLING_ACTIONS
from utils.errors import TransformationError

import test_action_recipe_pairs as pairs
import test_polars_actions_equal_polars as eq
from test_polars_actions_equal_polars import BASE, Case, eager

ROWS = ["head", "tail", "slice", "limit", "top_k", "bottom_k", "reverse", "gather_every", "with_row_index", "remove"]
TIES = pl.DataFrame({"id": ["a", "b", "c", "d", "e"], "k": [3, 1, 3, 2, 3], "u": [0, 1, 2, 3, 4]})

CASES = [
    Case("polars_head", BASE, {"n": 2}, lambda lf: lf.head(2)),
    Case("polars_tail", BASE, {"n": 2}, lambda lf: lf.tail(2)),
    Case("polars_limit", BASE, {"n": 3}, lambda lf: lf.limit(3)),
    Case("polars_slice", BASE, {"offset": 1, "length": 2}, lambda lf: lf.slice(1, 2)),
    Case("polars_slice", BASE, {"offset": -2}, lambda lf: lf.slice(-2)),                        # no length: to the end
    Case("polars_gather_every", BASE, {"n": 2, "offset": 0}, lambda lf: lf.gather_every(2, 0)),
    Case("polars_gather_every", BASE, {"n": 2, "offset": 1}, lambda lf: lf.gather_every(2, 1)),
    Case("polars_top_k", BASE, {"k": 2, "by": ["n"], "reverse": False}, lambda lf: lf.top_k(2, by=["n"], reverse=False)),
    Case("polars_top_k", TIES, {"k": 3, "by": ["k", "u"], "reverse": [False, True]}, lambda lf: lf.top_k(3, by=["k", "u"], reverse=[False, True])),
    Case("polars_bottom_k", BASE, {"k": 2, "by": ["n"], "reverse": False}, lambda lf: lf.bottom_k(2, by=["n"], reverse=False)),
    Case("polars_bottom_k", TIES, {"k": 2, "by": ["k", "u"], "reverse": True}, lambda lf: lf.bottom_k(2, by=["k", "u"], reverse=True)),
    Case("polars_reverse", BASE, {}, lambda lf: lf.reverse()),
    Case("polars_with_row_index", BASE, {"name": "row_no", "offset": 0}, lambda lf: lf.with_row_index("row_no", 0)),
    Case("polars_with_row_index", BASE, {"name": "row_no", "offset": 1}, lambda lf: lf.with_row_index("row_no", 1)),
    Case("polars_remove", BASE, {"predicates": ["pl.col('n') > 1"]}, lambda lf: lf.remove(pl.col("n") > 1)),
    Case("polars_remove", BASE, {"predicates": ["pl.col('n') > 1", "pl.col('g') == 'x'"]},
         lambda lf: lf.remove(pl.col("n") > 1, pl.col("g") == "x")),
]


def _id(case):
    return case.action + "-" + "-".join(f"{k}" for k in case.spec)


@pytest.mark.parametrize("case", CASES, ids=[_id(c) for c in CASES])
def test_the_direct_polars_call_of_the_case_runs(case):
    assert isinstance(eager(case.polars(case.frame.lazy())), pl.DataFrame)


def test_the_cases_cover_the_ten_row_actions():
    assert {c.action.removeprefix("polars_") for c in CASES} == set(ROWS)
    assert all(f"polars_{r}" in AVAILABLE_WRANGLING_ACTIONS for r in ROWS)


@pytest.mark.parametrize("case", CASES, ids=[_id(c) for c in CASES])
def test_the_action_equals_the_direct_polars_call(case):
    got = eager(AVAILABLE_WRANGLING_ACTIONS[case.action](case.frame.lazy(), dict(case.spec)))
    assert_frame_equal(got, eager(case.polars(case.frame.lazy())))


def test_remove_keeps_the_rows_where_the_test_is_null():
    """Polars: remove drops the rows where the predicate is true; a null predicate keeps the row (a filter would drop it)."""
    got = eager(AVAILABLE_WRANGLING_ACTIONS["polars_remove"](BASE.lazy(), {"predicates": ["pl.col('n') > 1"]}))
    assert got["id"].to_list() == ["a", "d"]                  # d has n null: kept
    assert eager(BASE.lazy().filter(~(pl.col("n") > 1)))["id"].to_list() == ["a"]


def test_the_row_actions_change_something_on_the_probe():
    for case in CASES:
        got = eager(AVAILABLE_WRANGLING_ACTIONS[case.action](case.frame.lazy(), dict(case.spec)))
        assert not got.equals(case.frame), f"{_id(case)} returned the table unchanged"


# -- the pair of every action: file -> ingestion -> wrangler, equal to the case -----------------------------------

@pytest.mark.parametrize("action", ["polars_" + r for r in ROWS])
def test_the_pair_of_the_action_equals_the_polars_call(action, monkeypatch):
    monkeypatch.chdir(pairs.ROOT)
    ingested, got, used = pairs._run(action)
    assert_frame_equal(ingested, BASE)                        # the TSV, the declared types and null_values lose nothing
    assert used == [action]
    pair_spec = {k: v for k, v in pairs._recipe(action)["tier1"]["steps"][0].items() if k != "action"}
    assert_frame_equal(got, eager(AVAILABLE_WRANGLING_ACTIONS[action](BASE.lazy(), pair_spec)))
    assert not got.equals(BASE)


# -- what the actions refuse (never a silent no-op, DEC36) ------------------------------------------------------

def _run(action, spec, frame=BASE):
    return eager(AVAILABLE_WRANGLING_ACTIONS[action](frame.lazy(), spec))


@pytest.mark.parametrize("action, spec, missing", [
    ("polars_head", {}, "n"), ("polars_tail", {}, "n"), ("polars_limit", {}, "n"),
    ("polars_slice", {"length": 2}, "offset"), ("polars_gather_every", {}, "n"),
    ("polars_top_k", {"by": ["n"]}, "k"), ("polars_top_k", {"k": 2}, "by"),
    ("polars_bottom_k", {"by": ["n"]}, "k"), ("polars_bottom_k", {"k": 2}, "by"),
    ("polars_with_row_index", {}, "name"), ("polars_remove", {}, "predicates"),
])
def test_a_missing_required_parameter_fails_and_names_it(action, spec, missing):
    with pytest.raises(TransformationError, match=missing):
        _run(action, spec)


@pytest.mark.parametrize("action, spec", [
    ("polars_head", {"n": 1}), ("polars_reverse", {}), ("polars_top_k", {"k": 1, "by": ["n"]}),
    ("polars_with_row_index", {"name": "i"}), ("polars_remove", {"predicates": ["pl.col('n') > 1"]}),
])
def test_an_unknown_key_fails_and_names_the_step(action, spec):
    with pytest.raises(TransformationError, match=f"{action}.*zz"):
        _run(action, {**spec, "zz": 1})


def test_a_wrong_form_fails():
    with pytest.raises(TransformationError):
        _run("polars_head", {"n": [1, 2]})
    with pytest.raises(TransformationError):
        _run("polars_top_k", {"k": 1, "by": "n"})                       # a column list is a list
    with pytest.raises(TransformationError):
        _run("polars_remove", {"predicates": "pl.col('n') > 1"})        # a list of formulas, not one text


def test_an_empty_list_of_predicates_fails_instead_of_removing_nothing():
    with pytest.raises(TransformationError, match="predicates"):
        _run("polars_remove", {"predicates": []})


@pytest.mark.parametrize("action", ["polars_top_k", "polars_bottom_k"])
def test_the_ranking_of_a_missing_column_gives_the_plain_message(action):
    with pytest.raises(TransformationError, match=rf"step {action}: column 'nope' is not in the table") as err:
        _run(action, {"k": 1, "by": ["id", "nope"]})
    assert "plan" not in str(err.value).lower() and "\n" not in str(err.value)


@pytest.mark.parametrize("predicate, kind", [("pl.col('n')", "Int64"), ("pl.col('id')", "String"), ("pl.col('n') + 1", "Int64"), ("pl.lit(1)", "Int32")])
def test_a_predicate_that_is_not_true_or_false_is_refused_and_nothing_is_removed(predicate, kind):
    with pytest.raises(TransformationError, match=r"step polars_remove: the predicate .* is not a true/false condition") as err:
        _run("polars_remove", {"predicates": [predicate]})
    assert "pl.col('a') > 0" in (err.value.tip or "") or "pl.col('a') > 0" in str(err.value)


def test_a_second_predicate_that_is_not_boolean_is_also_refused():
    with pytest.raises(TransformationError, match="not a true/false condition"):
        _run("polars_remove", {"predicates": ["pl.col('n') > 1", "pl.col('id')"]})


def test_a_predicate_on_a_missing_column_gives_the_plain_message():
    with pytest.raises(TransformationError, match=r"step polars_remove: column 'nope' is not in the table") as err:
        _run("polars_remove", {"predicates": ["pl.col('nope') > 0"]})
    assert "\n" not in str(err.value)


def test_the_description_says_a_predicate_is_a_true_false_condition():
    assert "true/false condition" in ACTION_SCHEMAS["polars_remove"]["description"]


def test_a_row_index_over_an_existing_column_fails():
    with pytest.raises(Exception, match="id"):
        _run("polars_with_row_index", {"name": "id"})


@pytest.mark.parametrize("formula", [
    "__import__('os').system('echo hacked')", "pl.col('n').map_elements(lambda v: v)", "pl.read_csv('/etc/passwd')",
    "open('/etc/passwd').read()", "pl.col('n') >",
])
def test_a_predicate_that_could_run_code_or_is_not_polars_is_refused(formula):
    with pytest.raises(TransformationError):
        _run("polars_remove", {"predicates": [formula]})


# -- the schema ---------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("action", ["polars_" + r for r in ROWS])
def test_the_schema_has_description_example_wraps_and_the_polars_method_of_the_same_name(action):
    schema = ACTION_SCHEMAS[action]
    assert schema["description"].strip() and schema["yaml_example"].strip()
    assert schema["wraps"] == [{"lib": "polars", "attr_path": ["LazyFrame", action.removeprefix("polars_")]}]
    assert schema["polars"] in ("exact", "wrapper")


def test_the_required_parameters_are_the_decided_ones():
    required = {a: sorted(k for k, d in ACTION_SCHEMAS[a]["params"].items() if d["required"]) for a in ["polars_" + r for r in ROWS]}
    assert required == {
        "polars_head": ["n"], "polars_tail": ["n"], "polars_limit": ["n"], "polars_slice": ["offset"],
        "polars_gather_every": ["n"], "polars_top_k": ["by", "k"], "polars_bottom_k": ["by", "k"], "polars_reverse": [],
        "polars_with_row_index": ["name"], "polars_remove": ["predicates"],
    }


def test_the_remove_schema_gives_a_reason_for_the_keyword_form_it_does_not_expose():
    assert ACTION_SCHEMAS["polars_remove"]["not_exposed"]["constraints"].strip()


def test_eq_module_is_untouched_by_this_file():
    """The ten actions are not cases of the main file: its coverage test keeps its own list."""
    assert not {c.action for c in eq.CASES} & {"polars_" + r for r in ROWS}
