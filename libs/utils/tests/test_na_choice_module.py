"""The choice `na` (NA-RULE-63 part 2, decided 2026-11-14): read, preselected by operator, applied to a condition."""
import polars as pl
import pytest

NAN = float("nan")


from utils.missing_values import keep_missing
from utils.na_choice import default_na, na_of, with_na


def test_a_row_without_na_is_remove_because_that_is_what_it_always_did():
    assert na_of({"column": "x", "op": "ne", "value": 1}) == "remove"
    assert na_of({}) == "remove" and na_of(None) == "remove"


def test_na_keep_and_remove_are_read_and_anything_else_is_refused():
    assert na_of({"na": "keep"}) == "keep" and na_of({"na": "remove"}) == "remove"
    with pytest.raises(ValueError, match="keep"):
        na_of({"na": "maybe"})


@pytest.mark.parametrize("op, expected", [
    ("ne", "keep"), ("not_in", "keep"),
    ("eq", "remove"), ("in", "remove"), ("gt", "remove"), ("ge", "remove"), ("lt", "remove"), ("le", "remove"),
    ("between", "remove"),
])
def test_the_tick_is_preselected_by_operator(op, expected):
    assert default_na(op) == expected


def test_with_na_writes_the_choice_and_leaves_the_original_alone():
    old = {"column": "x", "op": "eq", "value": 1}
    assert with_na(old) == {**old, "na": "remove"} and "na" not in old
    assert with_na({**old, "na": "keep"})["na"] == "keep"


def test_keep_missing_adds_only_the_null_rows():
    df = pl.DataFrame({"x": [1.0, None, NAN]})
    cond = pl.col("x") == 1.0
    assert df.filter(keep_missing(cond, "x", "remove"))["x"].to_list() == [1.0]
    kept = df.filter(keep_missing(cond, "x", "keep"))["x"].to_list()
    assert kept[0] == 1.0 and kept[1] is None and len(kept) == 2   # the NaN row is not added
    with pytest.raises(ValueError):
        keep_missing(cond, "x", "maybe")
