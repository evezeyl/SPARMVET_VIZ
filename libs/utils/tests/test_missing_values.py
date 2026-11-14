"""count_missing and missing_sentences (NA-RULE-63, decided 2026-11-14)."""
import polars as pl
import pytest

from utils.missing_values import MissingCounts, count_missing, missing_sentences

NAN = float("nan")


def test_counts_null_and_nan_separately_in_a_float_column():
    df = pl.DataFrame({"x": [1.0, None, NAN, NAN, None, None]})
    assert count_missing(df, "x") == MissingCounts(null_rows=3, nan_rows=2)


def test_accepts_a_lazy_frame_and_gives_the_same_answer():
    df = pl.DataFrame({"x": [1.0, None, NAN]})
    assert count_missing(df.lazy(), "x") == count_missing(df, "x")


def test_non_float_columns_have_no_nan_rows():
    df = pl.DataFrame({"i": [1, None, 3], "t": ["a", None, "b"]})
    assert count_missing(df, "i") == MissingCounts(1, 0)
    assert count_missing(df, "t") == MissingCounts(1, 0)


def test_the_text_NA_and_the_empty_text_are_values():
    df = pl.DataFrame({"t": ["NA", "", None]})
    assert count_missing(df, "t") == MissingCounts(1, 0)


def test_nan_is_not_counted_as_missing_and_nothing_missing_gives_zero():
    assert count_missing(pl.DataFrame({"x": [NAN, 1.0]}), "x") == MissingCounts(0, 1)
    assert count_missing(pl.DataFrame({"x": [1.0, 2.0]}), "x") == MissingCounts(0, 0)


def test_empty_and_all_missing_frames():
    assert count_missing(pl.DataFrame({"x": pl.Series([], dtype=pl.Float64)}), "x") == MissingCounts(0, 0)
    assert count_missing(pl.DataFrame({"x": pl.Series([None, None], dtype=pl.Float64)}), "x") == MissingCounts(2, 0)
    assert count_missing(pl.DataFrame({"x": [None, None]}), "x") == MissingCounts(2, 0)


def test_unknown_column_is_an_error():
    with pytest.raises(KeyError):
        count_missing(pl.DataFrame({"x": [1]}), "y")


def test_sentences_for_remove_and_keep():
    c = MissingCounts(3, 2)
    r = missing_sentences("g", "gt", "remove", c)
    assert r.missing == "3 rows have no value in g: they are removed"
    assert r.nan == "2 rows have a failed calculation"
    assert r.warning is None
    k = missing_sentences("g", "gt", "keep", c)
    assert k.missing == "3 rows have no value in g: they are kept"
    assert k.nan == r.nan  # na does not touch NaN


def test_singular_and_nothing_to_say():
    s = missing_sentences("g", "eq", "remove", MissingCounts(1, 1))
    assert s.missing == "1 row has no value in g: it is removed"
    assert s.nan == "1 row has a failed calculation"
    z = missing_sentences("g", "ne", "remove", MissingCounts(0, 0))
    assert (z.missing, z.nan, z.warning) == (None, None, None)


@pytest.mark.parametrize("op", ["ne", "not_in"])
def test_warning_for_not_equal_and_none_of_when_the_column_has_missing_values(op):
    w = missing_sentences("g", op, "remove", MissingCounts(2, 0)).warning
    assert w and "g" in w and "na: keep" in w
    w_keep = missing_sentences("g", op, "keep", MissingCounts(2, 0)).warning
    assert w_keep and "kept" in w_keep


@pytest.mark.parametrize("op", ["eq", "in", "gt", "ge", "lt", "le", "between"])
def test_no_warning_for_the_other_operators(op):
    assert missing_sentences("g", op, "remove", MissingCounts(2, 0)).warning is None


def test_no_warning_without_missing_values_even_with_nan():
    assert missing_sentences("g", "ne", "remove", MissingCounts(0, 4)).warning is None


def test_na_must_be_keep_or_remove():
    with pytest.raises(ValueError):
        missing_sentences("g", "ne", "maybe", MissingCounts(1, 0))
