"""count_missing and missing_sentences (NA-RULE-63, decided 2026-11-14)."""
import polars as pl
import pytest

from utils.missing_values import (COUNTS_FAILED, MissingCounts, count_missing, dialog_lines, dialog_missing_lines,
                                  missing_sentences, na_choice_texts)

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


@pytest.mark.parametrize("op, words", [("ne", "not equal"), ("not_in", "none of")])
def test_warning_for_not_equal_and_none_of_names_the_tick_in_both_states(op, words):
    off = missing_sentences("g", op, "remove", MissingCounts(2, 0)).warning
    assert off == f"'{words}' also removes the rows with no value in g. Tick the box above to keep them."
    on = missing_sentences("g", op, "keep", MissingCounts(2, 0)).warning
    assert on == "The rows with no value in g are kept because the box is ticked."


@pytest.mark.parametrize("op", ["ne", "not_in"])
@pytest.mark.parametrize("na", ["keep", "remove"])
def test_no_recipe_or_library_word_in_any_text_a_home_user_reads(op, na):
    banned = ("Polars", "polars", "na:", "NaN", "null", "recipe")
    s = missing_sentences("g", op, na, MissingCounts(2, 3))
    for line in dialog_missing_lines("g", op, na, MissingCounts(2, 3)) + [s.missing, s.nan, s.warning,
                                                                           *na_choice_texts("not equal")]:
        assert not any(w in line for w in banned), line
    assert not any(w in line for w in banned for line in [COUNTS_FAILED])


def test_the_tick_of_the_warning_is_true_in_both_states_it_never_says_does_not_keep_next_to_kept():
    on = missing_sentences("g", "ne", "keep", MissingCounts(1, 0)).warning
    assert "does not keep" not in on and "removes" not in on


@pytest.mark.parametrize("op", ["eq", "in", "gt", "ge", "lt", "le", "between"])
def test_no_warning_for_the_other_operators(op):
    assert missing_sentences("g", op, "remove", MissingCounts(2, 0)).warning is None


def test_no_warning_without_missing_values_even_with_nan():
    assert missing_sentences("g", "ne", "remove", MissingCounts(0, 4)).warning is None


def test_na_must_be_keep_or_remove():
    with pytest.raises(ValueError):
        missing_sentences("g", "ne", "maybe", MissingCounts(1, 0))


def test_the_failed_calculation_line_says_the_choice_does_not_change_them():
    lines = dialog_missing_lines("g", "eq", "remove", MissingCounts(1, 2))
    assert lines == ["1 row has no value in g: it is removed",
                     "2 rows have a failed calculation: this choice does not change them."]
    one = dialog_missing_lines("g", "eq", "remove", MissingCounts(0, 1))
    assert one == ["No row has a missing value in g.",
                   "1 row has a failed calculation: this choice does not change it."]


def test_the_help_line_is_true_for_every_operator():
    label, help_ = na_choice_texts("greater than")
    assert label == "Keep the rows with no value in this column"
    assert help_ == ("With 'greater than', a row with no value does not match. "
                     "Tick: these rows are kept anyway. Untick: they are removed.")


def test_dialog_lines_gives_the_counts_of_the_table():
    df = pl.DataFrame({"x": [1.0, None, NAN]})
    assert dialog_lines(df, "x", "gt", "remove").lines == dialog_missing_lines("x", "gt", "remove", MissingCounts(1, 1))
    assert dialog_lines(df, "x", "gt", "remove").warning is None
    assert dialog_lines(df, "x", "ne", "remove").warning == missing_sentences("x", "ne", "remove", MissingCounts(1, 1)).warning


def test_dialog_lines_says_so_and_logs_when_the_counts_cannot_be_computed(caplog):
    with caplog.at_level("ERROR"):
        assert dialog_lines(pl.DataFrame({"x": [1.0]}), "nope", "gt", "remove").lines == [COUNTS_FAILED]
    assert COUNTS_FAILED == "The counts could not be computed."
    assert any("nope" in r.getMessage() for r in caplog.records)


def test_dialog_lines_without_a_table_says_so_and_logs(caplog):
    with caplog.at_level("ERROR"):
        assert dialog_lines(None, "x", "gt", "remove").lines == [COUNTS_FAILED]
    assert caplog.records
