"""The replace_values action: replace a listed set of values, keep the rest (issue #22).

Polars 1.0 deprecated .replace()'s `default` parameter in favour of .replace_strict() --
these tests pin the result of the fix (replace_strict) to be identical to the old
(deprecated) .replace() behaviour: values in the mapping are replaced, everything else
is kept as-is, nulls stay null, for both string and categorical columns.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_replace_values.py -q
"""
import warnings

import polars as pl
import pytest

from transformer.actions.cleaning.core import action_replace_values


def run(values, dtype, to_replace, new_value, columns=("v",)):
    frame = pl.DataFrame({"v": pl.Series(values, dtype=dtype)}).lazy()
    spec = {"columns": list(columns), "to_replace": to_replace, "new_value": new_value}
    return action_replace_values(frame, spec).collect()


def test_replaces_listed_values_keeps_the_rest_string_column():
    out = run(["ND", "Unknown", "O157", None], pl.String, ["ND", "Unknown"], "Not Typed")
    assert out["v"].to_list() == ["Not Typed", "Not Typed", "O157", None]


def test_replaces_listed_values_keeps_the_rest_categorical_column():
    out = run(["ND", "Unknown", "O157", None], pl.Categorical, ["ND", "Unknown"], "Not Typed")
    assert out["v"].to_list() == ["Not Typed", "Not Typed", "O157", None]


def test_no_match_in_column_leaves_every_value_unchanged():
    out = run(["a", "b", "c"], pl.String, ["ND", "Unknown"], "Not Typed")
    assert out["v"].to_list() == ["a", "b", "c"]


def test_multiple_columns_are_all_replaced():
    frame = pl.DataFrame({
        "serotype": pl.Series(["ND", "O157"], dtype=pl.Categorical),
        "st_type": pl.Series(["Unknown", "ST131"], dtype=pl.Categorical),
    }).lazy()
    spec = {"columns": ["serotype", "st_type"], "to_replace": ["ND", "Unknown"], "new_value": "Not Typed"}
    out = action_replace_values(frame, spec).collect()
    assert out["serotype"].to_list() == ["Not Typed", "O157"]
    assert out["st_type"].to_list() == ["Not Typed", "ST131"]


def test_does_not_raise_the_polars_replace_deprecation_warning():
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        run(["ND", "O157"], pl.String, ["ND"], "Not Typed")


def test_to_replace_must_be_a_list():
    frame = pl.DataFrame({"v": ["a"]}).lazy()
    with pytest.raises(ValueError, match="to_replace"):
        action_replace_values(frame, {"columns": ["v"], "to_replace": "ND", "new_value": "x"}).collect()


# ── Edge cases ──────────────────────────────────────────────────────────────

def test_empty_to_replace_list_is_a_no_op():
    out = run(["a", "b", None], pl.String, [], "Not Typed")
    assert out["v"].to_list() == ["a", "b", None]


def test_duplicate_values_in_to_replace_collapse_harmlessly():
    # {old: new for old in to_replace} naturally de-dupes identical keys.
    out = run(["ND", "O157"], pl.String, ["ND", "ND", "ND"], "Not Typed")
    assert out["v"].to_list() == ["Not Typed", "O157"]


def test_every_distinct_value_in_the_column_is_covered():
    out = run(["a", "b", "a"], pl.String, ["a", "b"], "Z")
    assert out["v"].to_list() == ["Z", "Z", "Z"]


def test_column_of_all_nulls_stays_all_nulls():
    out = run([None, None, None], pl.String, ["a", "b"], "Z")
    assert out["v"].to_list() == [None, None, None]


def test_empty_frame_does_not_raise():
    out = run([], pl.String, ["a"], "Z")
    assert out["v"].to_list() == []


def test_new_value_none_replaces_matched_values_with_null():
    out = run(["a", "b", None], pl.String, ["a"], None)
    assert out["v"].to_list() == [None, "b", None]


def test_new_value_collides_with_an_existing_untouched_value():
    # Replacing "ND" with "O157", a value that already occurs naturally elsewhere
    # in the column, must not disturb the already-O157 row.
    out = run(["ND", "O157", "H7"], pl.String, ["ND"], "O157")
    assert out["v"].to_list() == ["O157", "O157", "H7"]


def test_missing_columns_key_defaults_to_no_columns_and_is_a_no_op():
    frame = pl.DataFrame({"v": ["a", "b"]}).lazy()
    out = action_replace_values(frame, {"to_replace": ["a"], "new_value": "Z"}).collect()
    assert out["v"].to_list() == ["a", "b"]
