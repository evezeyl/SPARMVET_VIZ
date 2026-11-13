"""Every `polars_` action must equal the direct Polars call (W6, tests first, 2026-11-13).

Eve: "we need to know that the Polars action worked; polars_ actions are registered exactly as Polars; special
needs are separate modified actions." (`recipe_format_spec.md` DEC31 to DEC34, 7.5.1 rule 2).

Each case below is the definition of one future action: its name, the parameters it takes (the Polars names win,
N14; `columns` and `target_column` are ours and say where a method that works on an expression is applied), a
probe frame, and the direct Polars call whose result it must equal. Determinism is stated in the step, never
defaulted by the action (DEC34): `maintain_order`, `keep`, `seed`, `how` are written in every case.

State today: none of the actions exists, so every equality test is a strict xfail with the reason "not built".
The day an action is registered its mark fails and must be removed in that commit. Two tests are not xfail:
the direct Polars call of every case must run (a typo in a case would hide a real failure), and every case
must name a distinct action.

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
    Case("polars_pivot", BASE, {"on": "g", "index": "id", "values": "n", "aggregate_function": "first"},
         lambda lf: lf.collect().pivot(on="g", index="id", values="n", aggregate_function="first")),
    Case("polars_join", BASE, {"right_ingredient": "R", "on": "id", "how": "left", "maintain_order": "left_right", "__right_df__": RIGHT.lazy()},
         lambda lf: lf.join(RIGHT.lazy(), on="id", how="left", maintain_order="left_right")),
    Case("polars_sample", BASE, {"fraction": 0.5, "with_replacement": False, "shuffle": False, "seed": 1},
         lambda lf: lf.collect().sample(fraction=0.5, with_replacement=False, shuffle=False, seed=1)),
    Case("polars_describe", NUMS, {}, lambda lf: lf.collect().describe()),
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
        "unpivot", "pivot", "join", "sample", "describe", "cast", "fill_null", "fill_nan", "shift", "cum_sum",
        "cum_count", "interpolate", "round", "str_replace_all", "str_extract", "str_split", "str_strip_chars",
        "list_join", "list_slice", "dt_truncate", "coalesce", "sum_horizontal", "mean_horizontal", "min_horizontal",
        "max_horizontal", "all_horizontal", "any_horizontal",
    }
    assert {c.action.removeprefix("polars_") for c in CASES} == planned


# -- the equality tests: strict xfail until the action is registered -----------------------------

NOT_BUILT = "W6 not built: the action is not registered yet"


@pytest.mark.parametrize("case", [pytest.param(c, id=_id(c), marks=pytest.mark.xfail(strict=True, reason=NOT_BUILT)) for c in CASES])
def test_the_action_equals_the_direct_polars_call(case):
    action = AVAILABLE_WRANGLING_ACTIONS[case.action]
    got = eager(action(case.frame.lazy(), dict(case.spec)))
    expected = eager(case.polars(case.frame.lazy()))
    assert_frame_equal(got, expected)
