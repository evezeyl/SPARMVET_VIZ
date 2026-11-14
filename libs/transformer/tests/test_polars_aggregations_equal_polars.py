"""The table aggregations (`polars_sum` ... `polars_last`) equal the Polars call, and do what their descriptions say.

Eve, 2026-11-14: add the deferred Polars table aggregations; the engine follows Polars for missing values and NaN; the
description of each action says in one sentence what Polars does with a null and with a NaN, and a test proves that
sentence. What each action does to a text column is stated and tested the same way (no silent surprise).

What the tests prove:
  - every action equals the direct Polars call (same rows, same schema), with every option written (`ddof`, `quantile`,
    `interpolation`), and the direct call itself runs (a typo in a case would hide a failure);
  - the sentence of each description about null, NaN and text is true on a probe table (numbers in the test);
  - what the actions refuse: a missing `quantile`, a quantile that is not a number, an interpolation Polars does not know,
    a key that does not exist, a quantile outside 0 to 1 (Polars' own error);
  - the 1:1:1 pair of each action runs through the real path (ingestion with declared types, then the wrangler) and gives
    the Polars result on the ingested table;
  - the registry facts: the twelve are registered, wrap the `LazyFrame` method of the same name, are `exact`, and the
    parameters of the schema are the Polars ones.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_polars_aggregations_equal_polars.py -q
"""
import datetime as dt
import inspect
import math
from dataclasses import dataclass
from typing import Any, Callable

import polars as pl
import pytest
from polars.testing import assert_frame_equal

import transformer.actions  # noqa: F401
from transformer.actions.base import ACTION_SCHEMAS, AVAILABLE_WRANGLING_ACTIONS
from transformer.actions.polars_aggregations import AGGREGATIONS
from utils.errors import TransformationError

import test_action_recipe_pairs as pairs
import test_polars_actions_equal_polars as eq

NAN = float("nan")
BASE = eq.BASE            # id, g, n (Int64 with a null), f (Float64 with a NaN and a null), s (text with a null)


@dataclass
class Case:
    action: str
    spec: dict
    polars: Callable[[pl.LazyFrame], Any]


CASES = [
    Case("polars_sum", {}, lambda lf: lf.sum()),
    Case("polars_min", {}, lambda lf: lf.min()),
    Case("polars_max", {}, lambda lf: lf.max()),
    Case("polars_mean", {}, lambda lf: lf.mean()),
    Case("polars_median", {}, lambda lf: lf.median()),
    Case("polars_std", {"ddof": 1}, lambda lf: lf.std(ddof=1)),
    Case("polars_std", {"ddof": 0}, lambda lf: lf.std(ddof=0)),
    Case("polars_var", {"ddof": 1}, lambda lf: lf.var(ddof=1)),
    Case("polars_var", {"ddof": 0}, lambda lf: lf.var(ddof=0)),
    Case("polars_quantile", {"quantile": 0.5, "interpolation": "linear"}, lambda lf: lf.quantile(0.5, interpolation="linear")),
    Case("polars_quantile", {"quantile": 0.25, "interpolation": "lower"}, lambda lf: lf.quantile(0.25, interpolation="lower")),
    Case("polars_quantile", {"quantile": 0.9, "interpolation": "midpoint"}, lambda lf: lf.quantile(0.9, interpolation="midpoint")),
    Case("polars_count", {}, lambda lf: lf.count()),
    Case("polars_null_count", {}, lambda lf: lf.null_count()),
    Case("polars_first", {}, lambda lf: lf.first()),
    Case("polars_last", {}, lambda lf: lf.last()),
]


def _id(case: Case) -> str:
    return case.action + "-" + "-".join(f"{k}{v}" for k, v in case.spec.items())


def _run(action, spec, frame):
    return AVAILABLE_WRANGLING_ACTIONS[action](frame.lazy(), spec).collect()


def _one(action, spec, **columns):
    """The single row of an aggregation of a table made of the given columns, as a dict."""
    frame = pl.DataFrame({k: v for k, v in columns.items()})
    result = _run(action, spec, frame)
    assert result.height == 1
    return result.row(0, named=True)


# -- the cases are sound, and the set is complete --------------------------------------------------------------

@pytest.mark.parametrize("case", CASES, ids=[_id(c) for c in CASES])
def test_the_direct_polars_call_of_the_case_runs(case):
    assert isinstance(case.polars(BASE.lazy()).collect(), pl.DataFrame)


def test_the_cases_cover_the_twelve_aggregations():
    assert {c.action.removeprefix("polars_") for c in CASES} == set(AGGREGATIONS) and len(AGGREGATIONS) == 12


# -- equality with Polars ----------------------------------------------------------------------------------

@pytest.mark.parametrize("case", CASES, ids=[_id(c) for c in CASES])
def test_the_action_equals_the_direct_polars_call(case):
    got = _run(case.action, dict(case.spec), BASE)
    assert_frame_equal(got, case.polars(BASE.lazy()).collect())


@pytest.mark.parametrize("case", CASES, ids=[_id(c) for c in CASES])
def test_the_action_equals_polars_on_a_frame_with_only_numbers(case):
    frame = pl.DataFrame({"a": [4.0, 1.0, 9.0, 2.0, 7.0], "b": [3, 3, 5, 8, 1]})
    assert_frame_equal(_run(case.action, dict(case.spec), frame), case.polars(frame.lazy()).collect())


# -- the registry facts --------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", AGGREGATIONS)
def test_each_action_wraps_the_lazyframe_method_of_the_same_name_exactly(name):
    schema = ACTION_SCHEMAS[f"polars_{name}"]
    assert schema["polars"] == "exact"
    assert schema["wraps"] == [{"lib": "polars", "attr_path": ["LazyFrame", name]}]
    polars_params = [p for p in inspect.signature(getattr(pl.LazyFrame, name)).parameters if p != "self"]
    assert list(schema["params"]) == polars_params          # no parameter hidden, none added
    assert "not_exposed" not in schema                       # nothing of the call is left out
    assert schema["description"].strip() and schema["yaml_example"].strip()


def test_the_polars_defaults_are_kept_and_not_restated():
    """ddof 1 and interpolation `nearest` are Polars' own defaults: absent in the step, Polars decides (DEC33)."""
    for name in ("polars_std", "polars_var"):
        assert not ACTION_SCHEMAS[name]["params"]["ddof"]["required"] and "default" not in ACTION_SCHEMAS[name]["params"]["ddof"]
    assert ACTION_SCHEMAS["polars_quantile"]["params"]["quantile"]["required"]
    assert not ACTION_SCHEMAS["polars_quantile"]["params"]["interpolation"]["required"]
    frame = pl.DataFrame({"x": [1.0, 2.0, 3.0, 4.0]})
    assert_frame_equal(_run("polars_std", {}, frame), frame.lazy().std().collect())
    assert_frame_equal(_run("polars_quantile", {"quantile": 0.5}, frame), frame.lazy().quantile(0.5).collect())
    assert _run("polars_quantile", {"quantile": 0.5}, frame)["x"][0] == 3.0                      # `nearest`, not 2.5 (linear)
    assert _run("polars_quantile", {"quantile": 0.5, "interpolation": "linear"}, frame)["x"][0] == 2.5


def test_the_interpolation_options_are_all_the_polars_ones():
    from polars._typing import QuantileMethod
    import typing
    options = ACTION_SCHEMAS["polars_quantile"]["params"]["interpolation"]["options"]
    assert options == list(typing.get_args(QuantileMethod)) and "equiprobable" in options
    frame = pl.DataFrame({"x": [1.0, 2.0, 3.0, 4.0]})
    for method in options:                                    # every option of the schema runs and equals Polars
        assert_frame_equal(_run("polars_quantile", {"quantile": 0.3, "interpolation": method}, frame),
                           frame.lazy().quantile(0.3, interpolation=method).collect())


def test_the_picker_places_them_with_the_other_aggregation():
    for name in AGGREGATIONS:
        assert ACTION_SCHEMAS[f"polars_{name}"]["category"] == "aggregation"
        assert ACTION_SCHEMAS[f"polars_{name}"]["context"] == ACTION_SCHEMAS["polars_group_by"]["context"]


# -- the sentence of each description about null, NaN and text is true ---------------------------------------------

def test_sum_skips_nulls_nan_makes_it_nan_text_gives_null_all_null_gives_zero():
    row = _one("polars_sum", {}, a=[1.0, None, 3.0], b=[1.0, NAN, 3.0], c=pl.Series([None, None, None], dtype=pl.Float64), t=["x", "y", None])
    assert row["a"] == 4.0                                    # the null is skipped
    assert math.isnan(row["b"])                               # a NaN makes the sum NaN
    assert row["c"] == 0.0                                    # only nulls: 0, not null
    assert row["t"] is None                                   # text: null, no error
    assert _one("polars_sum", {}, flag=[True, False, None, True])["flag"] == 2    # a Boolean column counts its true values


def test_min_and_max_skip_nulls_ignore_nan_and_order_text_by_byte_order():
    for action, expected in (("polars_min", (1.0, 1.0, "b", None)), ("polars_max", (3.0, 3.0, "c", None))):
        row = _one(action, {}, a=[1.0, None, 3.0], b=[1.0, NAN, 3.0], t=["c", "b", None], z=pl.Series([None, None, None], dtype=pl.Float64))
        assert (row["a"], row["b"], row["t"], row["z"]) == expected      # NaN ignored; only nulls give null
    assert math.isnan(_one("polars_min", {}, n=[NAN, NAN])["n"]) and math.isnan(_one("polars_max", {}, n=[NAN, NAN])["n"])   # only NaN gives NaN


def test_mean_skips_nulls_nan_makes_it_nan_text_gives_null():
    row = _one("polars_mean", {}, a=[1.0, None, 3.0], b=[1.0, NAN, 3.0], t=["x", "y", None])
    assert row["a"] == 2.0 and math.isnan(row["b"]) and row["t"] is None


def test_median_skips_nulls_counts_nan_as_larger_than_every_number_text_gives_null():
    row = _one("polars_median", {}, a=[1.0, None, 3.0], b=[1.0, NAN, 3.0], t=["x", "y", None])
    assert row["a"] == 2.0
    assert row["b"] == 3.0                                    # NaN is the largest value, the middle one is 3.0: it does not propagate
    assert math.isnan(_one("polars_median", {}, c=[1.0, 2.0, NAN, NAN])["c"])     # a NaN among the middle values gives NaN
    assert row["t"] is None


@pytest.mark.parametrize("action", ["polars_std", "polars_var"])
def test_std_and_var_skip_nulls_nan_makes_them_nan_too_few_values_give_null_text_gives_null(action):
    row = _one(action, {"ddof": 1}, a=[1.0, None, 3.0], b=[1.0, NAN, 3.0], one=[1.0, None, None], t=["x", "y", None])
    assert row["a"] == (math.sqrt(2.0) if action == "polars_std" else 2.0)      # the null is skipped: two values, ddof 1
    assert math.isnan(row["b"])
    assert row["one"] is None                                 # one value and ddof 1: nothing to divide by
    assert row["t"] is None
    # ddof is a real option: with ddof 0 one value has a spread of 0
    assert _one(action, {"ddof": 0}, one=[1.0, None, None])["one"] == 0.0


def test_ddof_changes_the_result_as_polars_does():
    frame = pl.DataFrame({"x": [1.0, 2.0, 3.0, 4.0]})
    assert _run("polars_var", {"ddof": 1}, frame)["x"][0] == pytest.approx(5 / 3)
    assert _run("polars_var", {"ddof": 0}, frame)["x"][0] == pytest.approx(1.25)


def test_quantile_skips_nulls_counts_nan_as_larger_than_every_number_text_and_boolean_give_null():
    row = _one("polars_quantile", {"quantile": 0.5, "interpolation": "linear"},
               a=[1.0, None, 3.0], b=[1.0, NAN, 3.0], t=["x", "y", None], flag=[True, False, None])
    assert row["a"] == 2.0
    assert row["b"] == 3.0                                    # sorted 1.0, 3.0, NaN: the middle is 3.0
    assert math.isnan(_one("polars_quantile", {"quantile": 0.5, "interpolation": "linear"}, c=[1.0, NAN, NAN, NAN])["c"])
    assert row["t"] is None and row["flag"] is None


def test_count_counts_values_that_are_not_null_and_counts_a_nan_in_every_type_of_column():
    row = _one("polars_count", {}, a=[1.0, None, 3.0], b=[1.0, NAN, 3.0], t=["x", "y", None], flag=[True, None, None])
    assert row == {"a": 2, "b": 3, "t": 2, "flag": 1}
    assert _run("polars_count", {}, pl.DataFrame({"a": [1.0, 2.0]})).schema["a"] == pl.UInt32


def test_null_count_counts_only_nulls_a_nan_is_not_a_null_in_every_type_of_column():
    row = _one("polars_null_count", {}, a=[1.0, None, 3.0], b=[1.0, NAN, 3.0], t=["x", None, None], flag=[True, None, False])
    assert row == {"a": 1, "b": 0, "t": 2, "flag": 1}


def test_first_and_last_take_the_row_as_it_is_and_do_not_skip_a_null():
    frame = pl.DataFrame({"a": [None, 2.0, 3.0], "t": ["x", "y", None]})
    assert _run("polars_first", {}, frame).row(0, named=True) == {"a": None, "t": "x"}        # a null in the first row stays null
    assert _run("polars_last", {}, frame).row(0, named=True) == {"a": 3.0, "t": None}


def test_first_and_last_of_an_empty_table_give_no_row():
    """The one aggregation that does not return a row on an empty table (the others give 0 or null): stated in the description."""
    empty = pl.DataFrame({"a": pl.Series([], dtype=pl.Float64)})
    assert _run("polars_first", {}, empty).height == 0 and _run("polars_last", {}, empty).height == 0
    assert _run("polars_sum", {}, empty)["a"].to_list() == [0.0]
    assert _run("polars_count", {}, empty)["a"].to_list() == [0]
    assert _run("polars_mean", {}, empty)["a"].to_list() == [None]


def test_a_text_column_stays_in_the_result_and_keeps_its_name_and_type():
    """No error and no dropped column: the maker sees a null in the text column (the description says so)."""
    frame = pl.DataFrame({"n": [1, 2], "t": ["x", "y"]})
    for action in ("polars_sum", "polars_mean", "polars_median", "polars_std", "polars_var"):
        out = _run(action, {}, frame)
        assert out.columns == ["n", "t"] and out["t"].to_list() == [None] and out.schema["t"] == pl.String
    out = _run("polars_quantile", {"quantile": 0.5}, frame)
    assert out["t"].to_list() == [None]


@pytest.mark.parametrize("name", AGGREGATIONS)
def test_each_description_names_what_polars_does_with_a_null(name):
    text = ACTION_SCHEMAS[f"polars_{name}"]["description"]
    assert "null" in text and ("NaN" in text or name in ("count", "null_count", "first", "last")), text
    if name not in ("count", "null_count", "first", "last"):
        assert "text" in text, text           # what happens to a text column is said


# -- what the actions refuse ---------------------------------------------------------------------------------

def test_quantile_is_required():
    with pytest.raises(TransformationError, match="quantile"):
        _run("polars_quantile", {}, BASE)


@pytest.mark.parametrize("bad", ["0.5", True, [0.5]])
def test_a_quantile_that_is_not_a_number_is_refused(bad):
    with pytest.raises(TransformationError, match="quantile"):
        _run("polars_quantile", {"quantile": bad}, BASE)


@pytest.mark.parametrize("bad", [-0.1, 1.5])
def test_a_quantile_outside_zero_to_one_fails_with_polars_error(bad):
    with pytest.raises(Exception, match="between 0.0 and 1.0"):
        _run("polars_quantile", {"quantile": bad}, BASE)


def test_an_interpolation_polars_does_not_know_is_refused():
    with pytest.raises(TransformationError, match="interpolation"):
        _run("polars_quantile", {"quantile": 0.5, "interpolation": "bad"}, BASE)


@pytest.mark.parametrize("action", ["polars_std", "polars_var"])
def test_ddof_must_be_a_number(action):
    with pytest.raises(TransformationError, match="ddof"):
        _run(action, {"ddof": "one"}, BASE)


@pytest.mark.parametrize("name", AGGREGATIONS)
def test_an_unknown_key_is_refused_and_names_the_step(name):
    spec = {"quantile": 0.5} if name == "quantile" else {}
    with pytest.raises(TransformationError, match=f"polars_{name}.*columns"):
        _run(f"polars_{name}", {**spec, "columns": ["n"]}, BASE)       # a whole-table aggregation takes no column list


# -- the 1:1:1 pairs: the real path, then Polars on the ingested table ----------------------------------------------

FIRST_CASE = {}
for _c in CASES:
    FIRST_CASE.setdefault(_c.action, _c)


@pytest.mark.parametrize("action", [f"polars_{n}" for n in AGGREGATIONS])
def test_the_pair_gives_the_polars_result_on_the_ingested_table(action, monkeypatch):
    monkeypatch.chdir(pairs.ROOT)
    case = FIRST_CASE[action]
    ingested, got, used = pairs._run(action)
    assert_frame_equal(ingested, BASE)                        # the file layer loses nothing
    assert used == [action]
    assert_frame_equal(got, case.polars(BASE.lazy()).collect())


@pytest.mark.parametrize("action", [f"polars_{n}" for n in AGGREGATIONS])
def test_the_pair_recipe_writes_every_option_of_the_step(action):
    step = pairs._recipe(action)["wrangling"]["tier1"][0]
    assert step == {"action": action, **FIRST_CASE[action].spec}


# -- the types a recipe maker must know (ADR-104: no silent surprise), each sentence of a description proved ---------

D1, D2 = dt.date(2020, 1, 1), dt.date(2020, 1, 2)
TYPES = {
    "int": pl.Series([], dtype=pl.Int64), "float": pl.Series([], dtype=pl.Float64), "text": pl.Series([], dtype=pl.String),
    "bool": pl.Series([], dtype=pl.Boolean), "date": pl.Series([], dtype=pl.Date), "datetime": pl.Series([], dtype=pl.Datetime),
    "duration": pl.Series([], dtype=pl.Duration), "categorical": pl.Series([], dtype=pl.Categorical),
}
CALLS = [(c.action, c.spec) for c in CASES]


@pytest.mark.parametrize("action,spec", CALLS, ids=[_id(c) for c in CASES])
@pytest.mark.parametrize("kind", list(TYPES))
def test_no_aggregation_panics_on_an_empty_table_of_any_type(action, spec, kind):
    """A Polars panic is a BaseException: it must never reach the caller (only the Date quantile panics; it is a plain error)."""
    frame = pl.DataFrame({"x": TYPES[kind]})
    try:
        _run(action, dict(spec), frame)
    except TransformationError:
        assert action == "polars_quantile" and kind == "date"       # the one refusal, and only that one
    except Exception as exc:  # noqa: BLE001 - nothing else may be raised
        pytest.fail(f"{action} on an empty {kind} column raised {type(exc).__name__}: {exc}")


@pytest.mark.parametrize("interpolation", ["nearest", "linear"])
def test_quantile_of_a_date_column_of_an_empty_table_is_a_plain_error(interpolation):
    frame = pl.DataFrame({"d": pl.Series([], dtype=pl.Date), "n": pl.Series([], dtype=pl.Int64)})
    with pytest.raises(TransformationError) as info:
        _run("polars_quantile", {"quantile": 0.5, "interpolation": interpolation}, frame)
    assert isinstance(info.value, Exception)                          # not a BaseException that passes `except Exception`
    assert "polars_quantile" in str(info.value) and "Date" in str(info.value) and "no rows" in str(info.value)
    assert info.value.tip                                              # and how to fix it


def test_quantile_of_a_date_column_with_rows_and_of_an_empty_table_without_a_date_still_work():
    assert _run("polars_quantile", {"quantile": 0.5, "interpolation": "linear"}, pl.DataFrame({"d": [D1, D2]}))["d"][0] == dt.datetime(2020, 1, 1, 12)
    assert _run("polars_quantile", {"quantile": 0.5}, pl.DataFrame({"n": pl.Series([], dtype=pl.Int64)}))["n"].to_list() == [None]


@pytest.mark.parametrize("action", ["polars_std", "polars_var"])
@pytest.mark.parametrize("ddof", [-1, -3, -0.5])
def test_a_negative_ddof_is_refused_with_a_plain_message(action, ddof):
    with pytest.raises(TransformationError, match=f"{action}.*ddof.*negative") as info:
        _run(action, {"ddof": ddof}, BASE)
    assert info.value.tip


@pytest.mark.parametrize("action", ["polars_std", "polars_var"])
def test_a_ddof_of_zero_and_a_large_ddof_are_not_refused(action):
    assert _run(action, {"ddof": 0}, pl.DataFrame({"x": [1.0, 2.0]})).height == 1
    assert _run(action, {"ddof": 5}, pl.DataFrame({"x": [1.0, 2.0]}))["x"].to_list() == [None]


def test_mean_median_quantile_of_a_date_column_give_a_datetime():
    frame = pl.DataFrame({"d": [D1, D2]})
    for action, spec in (("polars_mean", {}), ("polars_median", {}), ("polars_quantile", {"quantile": 0.5, "interpolation": "linear"})):
        out = _run(action, spec, frame)
        assert out.schema["d"] == pl.Datetime("us") and out["d"][0] == dt.datetime(2020, 1, 1, 12), action


def test_std_and_var_of_a_date_datetime_or_duration_column_give_null():
    frame = pl.DataFrame({"d": [D1, D2], "dtm": [dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 2)], "dur": [dt.timedelta(1), dt.timedelta(2)]})
    for action in ("polars_std", "polars_var"):
        assert _run(action, {"ddof": 1}, frame).row(0) == (None, None, None), action


def test_sum_of_a_date_or_datetime_column_gives_null_and_of_a_duration_column_gives_the_total():
    frame = pl.DataFrame({"d": [D1, D2], "dtm": [dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 2)], "dur": [dt.timedelta(1), dt.timedelta(2)]})
    assert _run("polars_sum", {}, frame).row(0) == (None, None, dt.timedelta(3))


def test_min_and_max_of_text_compare_by_byte_order_capital_letters_first():
    frame = pl.DataFrame({"t": ["a", "B", "c"]})
    assert _run("polars_min", {}, frame)["t"][0] == "B"               # alphabetical order would give "a"
    assert _run("polars_max", {}, frame)["t"][0] == "c"


def test_categorical_and_list_columns_give_null_for_sum_and_mean_and_a_list_gives_null_for_min():
    frame = pl.DataFrame({"c": pl.Series(["a", "b"], dtype=pl.Categorical), "l": [[1], [2]]})
    for action in ("polars_sum", "polars_mean", "polars_median"):
        assert _run(action, {}, frame).row(0) == (None, None), action
    assert _run("polars_min", {}, frame).row(0)[1] is None and _run("polars_max", {}, frame).row(0)[1] is None


def test_the_result_types_change_as_the_descriptions_say():
    ints = pl.DataFrame({"i": [1, 2]})
    assert _run("polars_mean", {}, ints).schema["i"] == pl.Float64 and _run("polars_mean", {}, ints)["i"][0] == 1.5
    flags = pl.DataFrame({"b": [True, False, True]})
    assert _run("polars_sum", {}, flags).schema["b"] == pl.UInt32 and _run("polars_sum", {}, flags)["b"][0] == 2
    assert _run("polars_count", {}, flags).schema["b"] == pl.UInt32
    assert _run("polars_mean", {}, flags)["b"][0] == pytest.approx(2 / 3)
    assert _run("polars_median", {}, pl.DataFrame({"b": [True, False]}))["b"][0] == 0.5


def test_sum_of_a_64_bit_integer_column_beyond_the_range_wraps_around_without_error():
    """Pinned: the action stays exactly Polars. The description tells the recipe maker to convert to a float first."""
    out = _run("polars_sum", {}, pl.DataFrame({"i": [2**63 - 1, 1]}))
    assert out["i"][0] == -(2**63)
    assert _run("polars_sum", {}, pl.DataFrame({"i": pl.Series([2**63 - 1, 1], dtype=pl.Float64)}))["i"][0] == pytest.approx(2.0**63)
    assert "64-bit" in ACTION_SCHEMAS["polars_sum"]["description"] and "float" in ACTION_SCHEMAS["polars_sum"]["description"]


def test_the_descriptions_carry_the_sentences_proved_above():
    d = {n: ACTION_SCHEMAS[f"polars_{n}"]["description"] for n in AGGREGATIONS}
    assert "byte order" in d["min"] and "byte order" in d["max"] and "alphabetical" not in d["min"].replace("not alphabetical", "")
    assert "Datetime" in d["mean"] and "Datetime" in d["median"] and "Datetime" in d["quantile"]
    assert "Duration" in d["std"] and "Duration" in d["var"] and "negative" in d["std"] and "negative" in d["var"]
    assert "Date" in d["sum"] and "unsigned integer" in d["sum"] and "fraction" in d["mean"]
