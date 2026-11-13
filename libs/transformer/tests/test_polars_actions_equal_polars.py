"""Every `polars_` action must equal the direct Polars call (W6, tests first, 2026-11-13).

Eve: "we need to know that the Polars action worked; polars_ actions are registered exactly as Polars; special
needs are separate modified actions." (`recipe_format_spec.md` DEC31 to DEC34, 7.5.1 rule 2).

Each case below is the definition of one future action: its name, the parameters it takes (the Polars names win,
N14; `columns` and `target_column` are ours and say where a method that works on an expression is applied), a
probe frame, and the direct Polars call whose result it must equal. Determinism is stated in the step, never
defaulted by the action (DEC34): `maintain_order`, `keep`, `seed`, `how` are written in every case.

State: the 37 actions are built (`transformer.actions.polars_calls`, W6 package 1) and every case passes. Three
more tests guard the cases themselves: the direct Polars call of every case must run (a typo would hide a real
failure), every case names a polars_ action, and the cases cover the planned list of 7.5.1. The last tests
check what the actions refuse: an unknown key, a missing required parameter, a wrong form, and a step that
would do nothing silently.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_polars_actions_equal_polars.py -q
"""
import datetime
from dataclasses import dataclass
from typing import Any, Callable

import polars as pl
import pytest
from polars.testing import assert_frame_equal

import transformer.actions  # noqa: F401
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS

NAN = float("nan")

BASE = pl.DataFrame({
    "id": ["a", "b", "c", "d"],
    "g": ["x", "x", "y", None],
    "n": [1, 2, 3, None],
    "f": [1.5, NAN, 2.5, None],
    "s": [" A ", "b", None, "c d"],
})
LISTS = pl.DataFrame({"id": ["a", "b"], "l": [["p", "q"], ["r"]]})
STRUCTS = pl.DataFrame({"id": [1, 2], "st": [{"u": 1, "v": "a"}, {"u": 2, "v": "b"}]})
DATES = pl.DataFrame({"d": [datetime.date(2022, 3, 15), datetime.date(2022, 4, 2)]})
BOOLS = pl.DataFrame({"a": [True, False, True], "b": [True, True, False]})
RIGHT = pl.DataFrame({"id": ["a", "b", "z"], "v": [10, 20, 30]})
NUMS = pl.DataFrame({"x": [1.0, 4.0, 2.0], "y": [3.0, None, 5.0]})


@dataclass
class Case:
    action: str
    frame: pl.DataFrame
    spec: dict
    polars: Callable[[pl.LazyFrame], Any]   # the direct Polars call, on a LazyFrame, returns a LazyFrame or a DataFrame


def eager(x):
    return x.collect() if isinstance(x, pl.LazyFrame) else x


CASES = [
    # -- the frame methods ---------------------------------------------------------------------
    Case("polars_select", BASE, {"exprs": ["id", "n"]}, lambda lf: lf.select("id", "n")),
    Case("polars_drop", BASE, {"columns": ["g"], "strict": True}, lambda lf: lf.drop("g", strict=True)),
    Case("polars_with_columns", BASE, {"named_exprs": {"n2": "pl.col('n') * 2"}}, lambda lf: lf.with_columns(n2=pl.col("n") * 2)),
    Case("polars_rename", BASE, {"mapping": {"id": "key"}, "strict": True}, lambda lf: lf.rename({"id": "key"}, strict=True)),
    Case("polars_unique", BASE, {"subset": ["g"], "keep": "first", "maintain_order": True},
         lambda lf: lf.unique(subset=["g"], keep="first", maintain_order=True)),
    Case("polars_sort", BASE, {"by": ["n"], "descending": False, "nulls_last": False, "maintain_order": True},
         lambda lf: lf.sort(["n"], descending=False, nulls_last=False, maintain_order=True)),
    Case("polars_drop_nulls", BASE, {"subset": ["n"]}, lambda lf: lf.drop_nulls(subset=["n"])),
    Case("polars_drop_nans", BASE, {"subset": ["f"]}, lambda lf: lf.drop_nans(subset=["f"])),
    Case("polars_explode", LISTS, {"columns": ["l"]}, lambda lf: lf.explode(["l"])),
    Case("polars_unnest", STRUCTS, {"columns": ["st"]}, lambda lf: lf.unnest(["st"])),
    Case("polars_unpivot", BASE, {"on": ["n", "f"], "index": ["id"], "variable_name": "var", "value_name": "val"},
         lambda lf: lf.unpivot(on=["n", "f"], index=["id"], variable_name="var", value_name="val")),
    Case("polars_pivot", BASE, {"on": ["g"], "index": ["id"], "values": ["n"], "aggregate_function": "first"},
         lambda lf: lf.collect().pivot(on=["g"], index=["id"], values=["n"], aggregate_function="first")),
    Case("polars_join", BASE, {"right_ingredient": "R", "on": ["id"], "how": "left", "maintain_order": "left_right", "__right_df__": RIGHT.lazy()},
         lambda lf: lf.join(RIGHT.lazy(), on=["id"], how="left", maintain_order="left_right")),
    Case("polars_sample", BASE, {"fraction": 0.5, "with_replacement": False, "shuffle": False, "seed": 1},
         lambda lf: lf.collect().sample(fraction=0.5, with_replacement=False, shuffle=False, seed=1)),
    Case("polars_describe", NUMS, {}, lambda lf: lf.collect().describe()),
    Case("polars_group_by", BASE, {"by": ["g"], "maintain_order": True, "named_aggs": {"n": "pl.col('id').count()", "total": "pl.col('n').sum()"}},
         lambda lf: lf.group_by(["g"], maintain_order=True).agg(n=pl.col("id").count(), total=pl.col("n").sum())),
    # -- one expression applied to the listed columns ---------------------------------------------
    Case("polars_cast", BASE, {"columns": ["n"], "dtype": "Float64", "strict": True},
         lambda lf: lf.with_columns(pl.col("n").cast(pl.Float64, strict=True))),
    Case("polars_fill_null", BASE, {"columns": ["n"], "value": 0}, lambda lf: lf.with_columns(pl.col("n").fill_null(0))),
    Case("polars_fill_null", BASE, {"columns": ["n"], "strategy": "forward"}, lambda lf: lf.with_columns(pl.col("n").fill_null(strategy="forward"))),
    Case("polars_fill_nan", BASE, {"columns": ["f"], "value": 0.0}, lambda lf: lf.with_columns(pl.col("f").fill_nan(0.0))),
    Case("polars_shift", BASE, {"columns": ["n"], "n": 1}, lambda lf: lf.with_columns(pl.col("n").shift(1))),
    Case("polars_cum_sum", BASE, {"columns": ["n"], "reverse": False}, lambda lf: lf.with_columns(pl.col("n").cum_sum(reverse=False))),
    Case("polars_cum_count", BASE, {"columns": ["n"], "reverse": False}, lambda lf: lf.with_columns(pl.col("n").cum_count(reverse=False))),
    Case("polars_interpolate", NUMS, {"columns": ["y"], "method": "linear"}, lambda lf: lf.with_columns(pl.col("y").interpolate(method="linear"))),
    Case("polars_round", NUMS, {"columns": ["x"], "decimals": 1}, lambda lf: lf.with_columns(pl.col("x").round(1))),
    Case("polars_str_replace_all", BASE, {"columns": ["s"], "pattern": "b", "value": "B", "literal": False},
         lambda lf: lf.with_columns(pl.col("s").str.replace_all("b", "B", literal=False))),
    Case("polars_str_extract", BASE, {"columns": ["s"], "pattern": "(\\w)", "group_index": 1},
         lambda lf: lf.with_columns(pl.col("s").str.extract("(\\w)", group_index=1))),
    Case("polars_str_split", BASE, {"columns": ["s"], "by": " ", "inclusive": False},
         lambda lf: lf.with_columns(pl.col("s").str.split(" ", inclusive=False))),
    Case("polars_str_splitn", BASE, {"columns": ["s"], "by": " ", "n": 2, "target_column": "parts"},
         lambda lf: lf.with_columns(pl.col("s").str.splitn(" ", 2).alias("parts"))),
    Case("polars_str_strip_chars", BASE, {"columns": ["s"], "characters": None},
         lambda lf: lf.with_columns(pl.col("s").str.strip_chars(None))),
    Case("polars_list_join", LISTS, {"columns": ["l"], "separator": "-", "ignore_nulls": True},
         lambda lf: lf.with_columns(pl.col("l").list.join("-", ignore_nulls=True))),
    Case("polars_list_slice", LISTS, {"columns": ["l"], "offset": 0, "length": 1},
         lambda lf: lf.with_columns(pl.col("l").list.slice(0, 1))),
    Case("polars_dt_truncate", DATES, {"columns": ["d"], "every": "1mo"}, lambda lf: lf.with_columns(pl.col("d").dt.truncate("1mo"))),
    # -- one function over several columns, written to a target column --------------------------------
    Case("polars_coalesce", BASE, {"exprs": ["g", "s"], "target_column": "g"}, lambda lf: lf.with_columns(pl.coalesce("g", "s").alias("g"))),
    Case("polars_sum_horizontal", NUMS, {"exprs": ["x", "y"], "ignore_nulls": True, "target_column": "t"},
         lambda lf: lf.with_columns(pl.sum_horizontal("x", "y", ignore_nulls=True).alias("t"))),
    Case("polars_mean_horizontal", NUMS, {"exprs": ["x", "y"], "ignore_nulls": True, "target_column": "t"},
         lambda lf: lf.with_columns(pl.mean_horizontal("x", "y", ignore_nulls=True).alias("t"))),
    Case("polars_min_horizontal", NUMS, {"exprs": ["x", "y"], "target_column": "t"}, lambda lf: lf.with_columns(pl.min_horizontal("x", "y").alias("t"))),
    Case("polars_max_horizontal", NUMS, {"exprs": ["x", "y"], "target_column": "t"}, lambda lf: lf.with_columns(pl.max_horizontal("x", "y").alias("t"))),
    Case("polars_all_horizontal", BOOLS, {"exprs": ["a", "b"], "target_column": "t"}, lambda lf: lf.with_columns(pl.all_horizontal("a", "b").alias("t"))),
    Case("polars_any_horizontal", BOOLS, {"exprs": ["a", "b"], "target_column": "t"}, lambda lf: lf.with_columns(pl.any_horizontal("a", "b").alias("t"))),
]


def _id(case: Case) -> str:
    extra = ""
    if case.action == "polars_fill_null":
        extra = "-strategy" if "strategy" in case.spec else "-value"
    return case.action + extra


# -- not xfail: the cases themselves must be sound ----------------------------------------------

@pytest.mark.parametrize("case", CASES, ids=[_id(c) for c in CASES])
def test_the_direct_polars_call_of_the_case_runs(case):
    """A typo in a case would make its equality test fail for the wrong reason forever."""
    result = eager(case.polars(case.frame.lazy()))
    assert isinstance(result, pl.DataFrame)


def test_every_action_name_is_a_polars_action_name():
    assert all(c.action.startswith("polars_") for c in CASES)


def test_the_cases_cover_the_planned_polars_actions():
    """The 7.5.1 list of actions that become polars_<name> (the deferred gaps are not in it)."""
    planned = {
        "select", "drop", "with_columns", "rename", "unique", "sort", "drop_nulls", "drop_nans", "explode", "unnest",
        "unpivot", "pivot", "join", "sample", "describe", "group_by", "str_splitn", "cast", "fill_null", "fill_nan", "shift", "cum_sum",
        "cum_count", "interpolate", "round", "str_replace_all", "str_extract", "str_split", "str_strip_chars",
        "list_join", "list_slice", "dt_truncate", "coalesce", "sum_horizontal", "mean_horizontal", "min_horizontal",
        "max_horizontal", "all_horizontal", "any_horizontal",
    }
    assert {c.action.removeprefix("polars_") for c in CASES} == planned


# -- the equality tests --------------------------------------------------------------------------

@pytest.mark.parametrize("case", CASES, ids=[_id(c) for c in CASES])
def test_the_action_equals_the_direct_polars_call(case):
    action = AVAILABLE_WRANGLING_ACTIONS[case.action]
    got = eager(action(case.frame.lazy(), dict(case.spec)))
    expected = eager(case.polars(case.frame.lazy()))
    assert_frame_equal(got, expected)


# -- what the actions refuse (never a silent no-op, DEC36) ------------------------------------------

def _run(action, spec, frame=BASE):
    return eager(AVAILABLE_WRANGLING_ACTIONS[action](frame.lazy(), spec))


def test_an_unknown_key_fails_and_names_the_step():
    from utils.errors import TransformationError
    with pytest.raises(TransformationError, match="polars_drop.*zz"):
        _run("polars_drop", {"columns": ["g"], "zz": 1})


def test_a_missing_required_parameter_fails():
    from utils.errors import TransformationError
    with pytest.raises(TransformationError, match="maintain_order"):
        _run("polars_sort", {"by": ["n"]})                       # the order rule must be written (DEC34)
    with pytest.raises(TransformationError, match="seed"):
        _run("polars_sample", {"fraction": 0.5})
    with pytest.raises(TransformationError, match="decimals"):
        _run("polars_round", {"columns": ["f"]}, NUMS)
    with pytest.raises(TransformationError, match="maintain_order"):
        _run("polars_group_by", {"by": ["g"], "named_aggs": {"n": "pl.len()"}})      # the order of the groups is written
    with pytest.raises(TransformationError, match="n"):
        _run("polars_str_splitn", {"columns": ["s"], "by": " "})                   # how many parts is written


def test_a_scalar_where_a_list_is_needed_fails():
    from utils.errors import TransformationError
    with pytest.raises(TransformationError):
        _run("polars_select", {"exprs": "id"})


def test_the_old_spellings_of_a_column_key_are_not_guessed():
    from utils.errors import TransformationError
    with pytest.raises(TransformationError, match="columns"):
        _run("polars_drop", {"column": "g"})


def test_a_missing_column_fails_instead_of_being_ignored():
    with pytest.raises(Exception, match="nope"):
        _run("polars_select", {"exprs": ["id", "nope"]})
    with pytest.raises(Exception, match="nope"):
        _run("polars_drop", {"columns": ["nope"], "strict": True})


def test_both_value_and_strategy_of_fill_null_are_refused():
    from utils.errors import TransformationError
    with pytest.raises(TransformationError):
        _run("polars_fill_null", {"columns": ["n"], "value": 0, "strategy": "forward"})
    with pytest.raises(TransformationError):
        _run("polars_fill_null", {"columns": ["n"]})


def test_a_target_column_needs_exactly_one_column():
    from utils.errors import TransformationError
    with pytest.raises(TransformationError, match="target_column"):
        _run("polars_cast", {"columns": ["n", "f"], "dtype": "Float64", "target_column": "x"})


def test_a_formula_that_is_not_polars_fails_and_says_so():
    from utils.errors import TransformationError
    with pytest.raises(TransformationError):
        _run("polars_with_columns", {"named_exprs": {"x": "1 +"}})


@pytest.mark.parametrize("formula", [
    "__import__('os').system('echo hacked')",
    "pl.col('n').map_elements(lambda v: v)",
    "pl.read_csv('/etc/passwd')",
    "().__class__.__bases__[0].__subclasses__()",
    "open('/etc/passwd').read()",
])
def test_a_formula_that_could_run_code_or_read_files_is_refused(formula):
    """The three formula sites run only checked formulas (W3, `utils.formula_check`); here the polars_with_columns site."""
    from utils.errors import TransformationError
    with pytest.raises(TransformationError, match="refused"):
        _run("polars_with_columns", {"named_exprs": {"x": formula}})


def test_the_old_mutate_site_refuses_the_same_formulas():
    from utils.errors import TransformationError
    with pytest.raises(Exception, match="refused|Failed"):
        AVAILABLE_WRANGLING_ACTIONS["mutate"](BASE.lazy(), {"column": "x", "expression": "__import__('os').system('echo hacked')"}).collect()


# -- Eve, 2026-11-13 (Q1): a cast never truncates silently; a truncation is written in the recipe ----------

def test_a_cast_to_integer_that_would_drop_decimals_fails_and_names_the_value():
    from utils.errors import TransformationError
    frame = pl.DataFrame({"year": [2022.0, 2022.5, None]})
    with pytest.raises(TransformationError, match=r"year.*2022\.5"):
        _run("polars_cast", {"columns": ["year"], "dtype": "Int64", "strict": True}, frame)


def test_a_cast_of_whole_floats_to_integer_equals_polars():
    frame = pl.DataFrame({"year": [2022.0, 2023.0, None]})
    got = _run("polars_cast", {"columns": ["year"], "dtype": "Int64", "strict": True}, frame)
    assert_frame_equal(got, frame.with_columns(pl.col("year").cast(pl.Int64)))


def test_a_decimal_loss_written_in_the_recipe_is_possible():
    """The maker who wants to drop decimals says so with a step of its own (round, then cast)."""
    frame = pl.DataFrame({"year": [2022.0, 2022.5]})
    rounded = _run("polars_round", {"columns": ["year"], "decimals": 0}, frame)
    got = _run("polars_cast", {"columns": ["year"], "dtype": "Int64", "strict": True}, rounded)
    assert got["year"].to_list() == [2022, 2022]            # half_to_even: 2022.5 -> 2022, a visible step


def test_a_cast_that_loses_nothing_is_unchanged_for_other_types():
    frame = pl.DataFrame({"n": [1, 2], "s": ["1", "2"]})
    assert _run("polars_cast", {"columns": ["n"], "dtype": "Float64", "strict": True}, frame)["n"].dtype == pl.Float64
    assert _run("polars_cast", {"columns": ["s"], "dtype": "Int64", "strict": True}, frame)["s"].to_list() == [1, 2]
