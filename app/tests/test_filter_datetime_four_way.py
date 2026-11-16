"""A date and time column keeps the same rows in the table, the plot, the bundle and the re-run, at every precision and zone
(reviewer 2026-11-15: ns digits were cut to microseconds and picked nothing; ms and time-zone columns gave raw Polars errors).

What the dialog lists (`value_choices`) is what is stored; it carries the full precision and the offset of the column; the three
views and the exported step read it back from the column's own unit and zone. Time and duration columns are offered with their own controls (test_filter_four_way_pickers.py).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_filter_datetime_four_way.py -q
"""
import datetime

import polars as pl
import pytest

import transformer.actions  # noqa: F401
from app.modules.t3_audit_engine import audited_frame
from app.tests.audit_nodes import filter_nodes, home_plot_data
from app.modules.t3_audit_engine import _apply_filter_rows, dialog_value, ops_for_column, value_choices
from blueprint_arch.t3_translator import translate_t3_node
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS
from utils.filter_values import FilterValueError

BASE = datetime.datetime(2020, 7, 1, 10, 30)


def frame(unit, zone=None):
    """Three rows a, b, c and one with no value; `b` has digits below the microsecond when the unit is ns."""
    ns = 7 if unit == "ns" else 0
    times = pl.Series("t", [BASE, BASE + datetime.timedelta(days=1), BASE + datetime.timedelta(days=2, microseconds=250000), None], dtype=pl.Datetime("us"))
    t = times.cast(pl.Datetime("ns")) + pl.Series([0, ns, 0, 0], dtype=pl.Int64).cast(pl.Duration("ns")) if ns else times
    t = t.cast(pl.Datetime(unit))
    if zone:
        t = t.dt.replace_time_zone(zone)
    return pl.DataFrame({"s": ["a", "b", "c", "d"], "n": [1, 2, 3, 4], "t": t})


def views(f, rows):
    def rerun():
        lf = f.lazy()
        for r in rows:
            for step in translate_t3_node({"node_type": "filter_row", "params": r}):
                lf = AVAILABLE_WRANGLING_ACTIONS[step["action"]](lf, {k: v for k, v in step.items() if k != "action"})
        return lf.collect()["s"].to_list()
    return {
        "table": _apply_filter_rows(f.lazy(), rows).collect()["s"].to_list(),
        "bundle": audited_frame(f.lazy(), filter_nodes(rows)).collect()["s"].to_list(),
        "plot": home_plot_data(f.lazy(), rows, {"mapping": {"x": "s", "y": "n"}, "layers": [{"name": "geom_col", "params": {}}]})["s"].to_list(),
        "re-run": rerun(),
    }


def agree(f, rows, expected):
    got = views(f, rows)
    assert got == {k: expected for k in got}, got


def picked(f, label_index, op):
    """The row the dialog writes when the user picks the label_index-th listed value."""
    lf = f.lazy()
    label = list(value_choices(lf, "t"))[label_index]
    chosen_op, value, _ = dialog_value(lf, "t", f.schema["t"], False, op, picked=[label])
    return {"column": "t", "op": chosen_op, "value": value, "dtype": str(f.schema["t"]), "na": "remove"}


CASES = [("ms", None), ("us", None), ("ns", None), ("us", "UTC"), ("ns", "Europe/Paris"), ("ms", "Europe/Paris")]


@pytest.mark.parametrize("unit, zone", CASES)
@pytest.mark.parametrize("op, index, expected", [
    ("in", 0, ["a"]), ("in", 1, ["b"]), ("not_in", 1, ["a", "c"]), ("not_in", 0, ["b", "c"]), ("in", 2, ["c"]),
])
def test_what_the_dialog_lists_keeps_the_same_rows_in_every_view(unit, zone, op, index, expected):
    f = frame(unit, zone)
    agree(f, [picked(f, index, op)], expected)


@pytest.mark.parametrize("zone", [None, "Europe/Paris"])
def test_nanoseconds_below_the_microsecond_are_in_the_label_and_read_back_exactly(zone):
    f = frame("ns", zone)
    labels = list(value_choices(f.lazy(), "t"))
    assert labels[1].startswith("2020-07-02 10:30:00.000000007")
    agree(f, [picked(f, 1, "in")], ["b"])
    # one nanosecond away is another value: nothing matches, and nothing else is kept
    other = {**picked(f, 1, "in"), "value": [labels[1].replace(".000000007", ".000000008")]}
    agree(f, [other], [])


@pytest.mark.parametrize("unit", ["ms", "us"])
def test_a_value_finer_than_the_column_unit_is_refused_not_cut(unit):
    f = frame(unit)
    finer = "2020-07-01 10:30:00.123456789"
    row = {"column": "t", "op": "eq", "value": [finer], "dtype": str(f.schema["t"]), "na": "remove"}
    with pytest.raises(FilterValueError) as exc:
        _apply_filter_rows(f.lazy(), [row]).collect()
    assert "finer" in str(exc.value) and finer in str(exc.value)


# -- time zone: one reading everywhere

def test_a_text_without_a_zone_is_read_in_the_zone_of_the_column_everywhere():
    f = frame("us", "Europe/Paris")
    row = {"column": "t", "op": "eq", "value": ["2020-07-01 10:30:00"], "dtype": str(f.schema["t"]), "na": "remove"}
    agree(f, [row], ["a"])  # 10:30 Paris time, not 10:30 UTC


def test_an_offset_text_is_the_same_instant_in_the_zone_of_the_column():
    """What the old dialog stored for a time-zone column: str of the Python value, with the offset of that day (+02:00 in July)."""
    f = frame("us", "Europe/Paris")
    row = {"column": "t", "op": "in", "value": ["2020-07-01 10:30:00+02:00"], "dtype": str(f.schema["t"]), "na": "remove"}
    agree(f, [row], ["a"])
    utc = {**row, "value": ["2020-07-01 08:30:00+00:00"]}
    agree(f, [utc], ["a"])


def test_a_scalar_equal_on_a_time_zone_column_has_no_raw_error():
    f = frame("us", "UTC")
    for op, expected in (("eq", ["a"]), ("ne", ["b", "c"])):
        row = {"column": "t", "op": op, "value": "2020-07-01 10:30:00+00:00", "dtype": str(f.schema["t"]), "na": "remove"}
        got = views(f, [row])
        assert got["table"] == got["bundle"] == got["plot"] == got["re-run"] == expected, got


def test_an_offset_on_a_column_without_a_zone_is_refused_in_plain_words_in_every_view():
    f = frame("us")
    row = {"column": "t", "op": "eq", "value": ["2020-07-01 10:30:00+02:00"], "dtype": str(f.schema["t"]), "na": "remove"}
    with pytest.raises(FilterValueError) as exc:
        _apply_filter_rows(f.lazy(), [row]).collect()
    assert "no time zone" in str(exc.value) and "2020-07-01 10:30:00+02:00" in str(exc.value)
    step = translate_t3_node({"node_type": "filter_row", "params": row})[0]
    with pytest.raises(Exception) as rerun:
        AVAILABLE_WRANGLING_ACTIONS["modif_filter"](f.lazy(), {k: v for k, v in step.items() if k != "action"}).collect()
    assert "no time zone" in str(rerun.value)


def test_an_unreadable_text_is_a_plain_error_in_the_table():
    f = frame("us")
    row = {"column": "t", "op": "eq", "value": ["31/01/2020"], "dtype": str(f.schema["t"]), "na": "remove"}
    with pytest.raises(FilterValueError):
        _apply_filter_rows(f.lazy(), [row]).collect()


# -- time and duration are offered since FILTER-PICKERS-1; a column of another type is refused in plain words

@pytest.mark.parametrize("dtype", [pl.Binary, pl.List(pl.Int64)])
def test_a_column_of_another_type_is_not_offered(dtype):
    assert ops_for_column(dtype, False) == []


def test_a_filter_on_a_binary_column_is_a_plain_error_in_every_view():
    f = pl.DataFrame({"s": ["a", "b"], "n": [1, 2], "t": pl.Series([b"x", b"y"], dtype=pl.Binary)})
    row = {"column": "t", "op": "in", "value": ["x"], "dtype": "Binary", "na": "remove"}
    with pytest.raises(FilterValueError) as exc:
        _apply_filter_rows(f.lazy(), [row]).collect()
    assert "not offered" in str(exc.value)
    recipe = {"plots": {"p": {"mapping": {"x": "s", "y": "n"}, "layers": [{"name": "geom_col", "params": {}}], "filters": [row]}}}
    with pytest.raises(Exception) as plot:
        VizFactory().render(f.lazy(), recipe, "p")
    assert "ComputeError" not in str(plot.value) and "InvalidOperation" not in str(plot.value)
    step = {"column": "t", "op": "in", "value": ["x"], "na": "remove"}
    with pytest.raises(Exception) as rerun:
        AVAILABLE_WRANGLING_ACTIONS["modif_filter"](f.lazy(), step).collect()
    assert "InvalidOperation" not in str(rerun.value)


@pytest.mark.parametrize("zone", [None, "Europe/Paris"])
def test_a_scalar_equal_keeps_the_nanoseconds_too(zone):
    f = frame("ns", zone)
    suffix = "+02:00" if zone else ""
    for op, expected in (("eq", ["b"]), ("ne", ["a", "c"])):
        row = {"column": "t", "op": op, "value": f"2020-07-02 10:30:00.000000007{suffix}", "dtype": str(f.schema["t"]), "na": "remove"}
        agree(f, [row], expected)
