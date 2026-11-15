"""Inputs of the five time and join actions that Polars cannot take, refused with a plain message (ADR-104, Eve 2026-11-14).

No silent error, no silent wrong result, no crash that escapes. A Polars panic (`PanicException`) is a `BaseException`: it
passes every `except Exception`, so each case here is first shown to panic in Polars itself and then refused by the action
before Polars runs; the assembler also turns a panic that still gets through into a plain error naming the step.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_polars_time_joins_refusals.py -q
"""
import datetime
import random
import warnings

import polars as pl
import pytest
from polars.exceptions import PanicException
from polars.testing import assert_frame_equal

import transformer.actions  # noqa: F401
import transformer.data_assembler as assembler_module
from transformer.actions.base import ACTION_SCHEMAS, AVAILABLE_WRANGLING_ACTIONS
from transformer.actions.polars_time_joins import _not_ascending
from transformer.anchor import write_anchor
from transformer.data_assembler import DataAssembler
from utils.errors import TransformationError

D = datetime.date
DAYS = pl.DataFrame({"d": [D(2020, 1, n) for n in range(1, 6)], "v": [1, 2, 3, 4, 5]})
MOMENTS = pl.DataFrame({"d": [datetime.datetime(2020, 1, 1, h) for h in range(5)], "v": [1, 2, 3, 4, 5]})
NUMBERS = pl.DataFrame({"i": [1, 2, 3, 4], "v": [1, 2, 3, 4]})
AGG = {"s": "pl.col('v').sum()"}


def run(action, frame, spec):
    return AVAILABLE_WRANGLING_ACTIONS[action](frame.lazy(), spec).collect()


def dynamic(frame=DAYS, index="d", **more):
    return run("polars_group_by_dynamic", frame, {"index_column": index, "every": "1d", "closed": "left", "named_aggs": AGG, **more})


def rolling(frame=DAYS, index="d", **more):
    return run("polars_rolling", frame, {"index_column": index, "period": "2d", "closed": "right", "named_aggs": AGG, **more})


# -- 1. what Polars does (so the refusals are known to be needed) ------------------------------------------

@pytest.mark.parametrize("every", ["0d", "1ns"])
def test_polars_panics_on_a_zero_or_nanosecond_every_for_a_date_index(every):
    with pytest.raises(PanicException):
        DAYS.lazy().group_by_dynamic("d", every=every, closed="left").agg(s=pl.col("v").sum()).collect()


def test_polars_panics_on_a_zero_integer_every_and_on_an_empty_by_of_an_asof_join():
    with pytest.raises(PanicException):
        NUMBERS.lazy().group_by_dynamic("i", every="0i", closed="left").agg(s=pl.col("v").sum()).collect()
    with pytest.raises(PanicException):
        DAYS.lazy().join_asof(DAYS.lazy(), on="d", by=[]).collect()


# -- 2. zero and negative durations ----------------------------------------------------------------------

@pytest.mark.parametrize("every", ["0d", "0i", "-1d", "-3d", "1d-1d", "0mo"])
def test_dynamic_an_every_that_is_zero_or_negative_is_refused_before_polars_runs(every):
    frame = NUMBERS if every.endswith("i") else DAYS
    index = "i" if every.endswith("i") else "d"
    with pytest.raises(TransformationError, match="every") as caught:
        dynamic(frame, index, every=every)
    assert "positive" in str(caught.value) + caught.value.tip


@pytest.mark.parametrize("period", ["0d", "-1d"])
def test_dynamic_a_period_that_is_zero_or_negative_is_refused(period):
    with pytest.raises(TransformationError, match="period"):
        dynamic(every="2d", period=period)  # polars: period 0d gives an empty table, -1d panics


@pytest.mark.parametrize("period", ["0d", "-2d"])
def test_rolling_a_period_that_is_zero_or_negative_is_refused_in_plain_words(period):
    with pytest.raises(TransformationError, match="period") as caught:
        rolling(period=period)
    assert "positive" in str(caught.value) + caught.value.tip


def test_a_negative_or_zero_offset_is_valid_in_polars_and_is_kept():
    for offset in ("-1d", "0d", "1d"):
        out = dynamic(every="2d", offset=offset)
        assert_frame_equal(out, DAYS.lazy().group_by_dynamic("d", every="2d", offset=offset, closed="left").agg(s=pl.col("v").sum()).collect())
        assert_frame_equal(rolling(offset=offset), DAYS.lazy().rolling("d", period="2d", offset=offset, closed="right").agg(s=pl.col("v").sum()).collect())


def test_a_whole_number_window_zero_is_refused_too_and_a_positive_one_still_runs():
    with pytest.raises(TransformationError, match="period"):
        rolling(NUMBERS, "i", period="0i")
    assert rolling(NUMBERS, "i", period="2i").height == 4


# -- 3. a duration finer than a day on a Date index -----------------------------------------------------

@pytest.mark.parametrize("key", ["every", "period", "offset"])
@pytest.mark.parametrize("text", ["6h", "36h", "90m", "1ns"])
def test_dynamic_a_duration_finer_than_a_day_on_a_date_index_is_refused(key, text):
    more = {"every": "2d"} if key != "every" else {}
    with pytest.raises(TransformationError, match=f"{key} '{text}'.*finer than a day") as caught:
        dynamic(**{**more, key: text})
    assert "Datetime" in caught.value.tip


@pytest.mark.parametrize("key", ["period", "offset"])
@pytest.mark.parametrize("text", ["6h", "36h", "90m", "1ns"])
def test_rolling_a_duration_finer_than_a_day_on_a_date_index_is_refused(key, text):
    more = {} if key == "period" else {"period": "2d"}
    with pytest.raises(TransformationError, match=f"{key} '{text}'.*finer than a day"):
        rolling(**{**more, key: text})


def test_a_duration_in_hours_is_fine_on_a_datetime_index_and_days_and_weeks_months_on_a_date_index():
    assert dynamic(MOMENTS, every="2h").height == 3
    assert rolling(MOMENTS, period="90m").height == 5
    assert dynamic(every="1w").height == 1 and dynamic(every="1mo").height == 1 and rolling(period="1w").height == 5


# -- 4. an empty `by` of the as-of join -------------------------------------------------------------------

def asof(**more):
    return run("polars_join_asof", DAYS, {"right_ingredient": "R", "on": "d", "strategy": "backward", "__right_df__": DAYS.lazy(), **more})


@pytest.mark.parametrize("more", [{"by": []}, {"by_left": [], "by_right": []}])
def test_asof_an_empty_by_is_refused_in_plain_words(more):
    with pytest.raises(TransformationError, match="by") as caught:
        asof(**more)
    assert "is empty" in str(caught.value) and "leave it out" in str(caught.value)


def test_asof_a_non_empty_by_still_works():
    frame = DAYS.with_columns(g=pl.lit("a"))
    out = run("polars_join_asof", frame, {"right_ingredient": "R", "on": "d", "by": ["g"], "strategy": "backward", "__right_df__": frame.lazy()})
    assert out.height == 5


# -- 5. the same rule for a text tolerance as for a number -----------------------------------------------

@pytest.mark.parametrize("tolerance", ["-2d", "-1w"])
def test_asof_a_negative_text_tolerance_is_refused_like_a_negative_number(tolerance):
    with pytest.raises(TransformationError, match="negative"):
        asof(tolerance=tolerance)
    with pytest.raises(TransformationError, match="negative"):
        run("polars_join_asof", NUMBERS, {"right_ingredient": "R", "on": "i", "strategy": "backward", "tolerance": -2, "__right_df__": NUMBERS.lazy()})


def test_asof_a_zero_or_positive_text_tolerance_still_works():
    assert asof(tolerance="0d").height == 5 and asof(tolerance="3d").height == 5


# -- 6. a step that cannot act ---------------------------------------------------------------------------

def test_rank_with_no_column_is_refused_and_does_not_return_the_table_unchanged():
    with pytest.raises(TransformationError, match="columns"):
        run("polars_rank", DAYS, {"columns": [], "method": "min"})


@pytest.mark.parametrize("action", ["polars_group_by_dynamic", "polars_rolling"])
def test_a_window_action_without_any_aggregation_is_refused(action):
    spec = {"index_column": "d", "closed": "left", "named_aggs": {}, ("every" if action.endswith("dynamic") else "period"): "2d"}
    with pytest.raises(TransformationError, match="named_aggs"):
        run(action, DAYS, spec)


# -- 7. predicates that compare columns of different types -----------------------------------------------

def where(left, right, predicates):
    return run("modif_join_where", left, {"right_ingredient": "R", "predicates": predicates, "__right_df__": right.lazy()})


def test_where_a_date_against_a_datetime_is_refused_like_an_integer_against_a_float():
    left = pl.DataFrame({"d": [D(2020, 1, 1), D(2020, 1, 3)]})
    right = pl.DataFrame({"lo": [datetime.datetime(2020, 1, 2)]})
    assert left.lazy().join_where(right.lazy(), pl.col("d") >= pl.col("lo")).collect().height == 1, "Polars accepts it and promotes the date"
    with pytest.raises(TransformationError, match="cannot compare Date with Datetime") as caught:
        where(left, right, ["pl.col('d') >= pl.col('lo')"])
    assert "polars_cast" in caught.value.tip and "input_fields" in caught.value.tip


def test_where_two_different_integer_widths_are_refused_and_equal_types_work():
    left = pl.DataFrame({"a": pl.Series([1, 5], dtype=pl.Int32)})
    right = pl.DataFrame({"b": pl.Series([2], dtype=pl.Int64)})
    with pytest.raises(TransformationError, match="cannot compare Int32 with Int64"):
        where(left, right, ["pl.col('a') >= pl.col('b')"])
    assert where(left.with_columns(pl.col("a").cast(pl.Int64)), right, ["pl.col('a') >= pl.col('b')"]).height == 1


def test_where_the_type_rule_looks_inside_and_or_and_leaves_a_literal_alone():
    left = pl.DataFrame({"d": [D(2020, 1, 1)], "n": [1]})
    right = pl.DataFrame({"lo": [datetime.datetime(2020, 1, 2)], "m": [1]})
    with pytest.raises(TransformationError, match="cannot compare Date with Datetime"):
        where(left, right, ["(pl.col('n') == pl.col('m')) & (pl.col('d') <= pl.col('lo'))"])
    assert where(left, right, ["pl.col('n') == pl.col('m')", "pl.col('n') > 0", "pl.col('m') < 10"]).height == 1


# -- 8. the registry field -------------------------------------------------------------------------------

def test_the_joins_carry_the_field_of_polars_join_and_the_windows_the_field_of_polars_group_by():
    field = {name: ACTION_SCHEMAS[name]["polars"] for name in ACTION_SCHEMAS if name.startswith("polars_")}
    assert field["polars_join_asof"] == field["polars_join"] == "exact"
    assert ACTION_SCHEMAS["modif_join_where"]["polars"] == "modified" and field.get("modif_join_where") is None
    assert field["polars_group_by_dynamic"] == field["polars_rolling"] == field["polars_group_by"] == "wrapper"


# -- 9. the safety net of the assembler ------------------------------------------------------------------

def _assemble_with(monkeypatch, error):
    def panicking(lf, step):
        raise error

    monkeypatch.setattr(assembler_module, "get_action_function", lambda name: panicking)
    left = pl.LazyFrame({"t": [1, 2]})
    return DataAssembler({"L": left}, recipe_id="demo", join_id="J").assemble([{"action": "polars_sort", "by": ["t"]}])


def test_a_polars_panic_in_a_step_becomes_a_plain_error_that_names_the_step(monkeypatch):
    with pytest.raises(TransformationError) as caught:
        _assemble_with(monkeypatch, PanicException("attempt to divide by zero"))
    text = f"{caught.value} {caught.value.tip}"
    assert "polars_sort" in text and "step 0" in text and "Polars stopped" in text and "divide by zero" in text
    assert "PanicException" not in str(caught.value).split("Polars stopped")[0]


@pytest.mark.parametrize("error", [KeyboardInterrupt(), SystemExit(3)])
def test_an_interrupt_or_an_exit_is_not_caught_by_the_safety_net(monkeypatch, error):
    with pytest.raises(type(error)):
        _assemble_with(monkeypatch, error)


def test_a_polars_panic_that_shows_when_the_plan_runs_is_caught_where_the_plan_is_written(tmp_path):
    """The asof panic with `by: []`, reached with the action's own refusal bypassed: the plan runs in write_anchor, and the net holds."""
    frame = DAYS.lazy()
    unguarded = frame.join_asof(frame, on="d", by=[], strategy="backward")
    with pytest.raises(TransformationError, match="Polars stopped") as caught:
        write_anchor(unguarded, tmp_path / "t1.parquet", decision_hash="k")
    assert "t1.parquet" in str(caught.value) and "report it" in caught.value.tip


def test_the_anchor_writer_still_writes_and_lets_an_interrupt_pass(tmp_path, monkeypatch):
    assert write_anchor(DAYS.lazy(), tmp_path / "ok.parquet", decision_hash="k").collect().height == 5

    def interrupted(self, *args, **kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr(pl.LazyFrame, "collect", interrupted)
    with pytest.raises(KeyboardInterrupt):
        write_anchor(DAYS.lazy(), tmp_path / "x.parquet", decision_hash="k")


# -- 10. the own sortedness check equals the Polars check where Polars makes one (why `check_sortedness` is never switched off) --

def test_the_own_sortedness_check_says_what_polars_says_without_by_so_the_polars_check_can_stay_on():
    rng = random.Random(1)
    values = [None, float("nan"), 1.0, 2.0, 3.0, -1.0]
    different = []
    for _ in range(400):
        key = [rng.choice(values) for _ in range(rng.randint(1, 5))]
        frame = pl.DataFrame({"t": pl.Series(key, dtype=pl.Float64)}).lazy()
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                frame.join_asof(frame, on="t").collect()
            polars_refuses = False
        except pl.exceptions.PolarsError:
            polars_refuses = True
        if _not_ascending(frame, "t") != polars_refuses:
            different.append(key)
    assert not different


def test_the_old_name_polars_join_where_is_not_registered_and_the_new_name_is():
    """No alias and no shim (Eve, 2026-11-15): the engine does not know the old name."""
    assert "polars_join_where" not in AVAILABLE_WRANGLING_ACTIONS and "polars_join_where" not in ACTION_SCHEMAS
    assert "modif_join_where" in AVAILABLE_WRANGLING_ACTIONS
