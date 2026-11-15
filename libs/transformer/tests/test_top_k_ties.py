"""What `polars_top_k` / `polars_bottom_k` really do with ties, NaN and missing values, pinned (D42, Eve 2026-11-15; Polars 1.40.1, RUN).

Each statement of the description is pinned here by a run:
  - exactly k rows come back; tied rows at the cut are cut too (not all of them kept);
  - a NaN counts as the largest value and comes first in top_k;
  - rows with no value (null) fill the k rows when the real values run out;
  - a row number as the last `by` column keeps always the same rows (the first tied rows in table order);
  - `polars_sort` with `maintain_order` then `polars_head` gives the same rows;
  - `polars_rank` with method `min` and a filter keeps every row tied with the k best (more than k rows).
The description must not say the kept tied rows are "not the input order" (on small tables Polars keeps the first ones).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_top_k_ties.py -q
"""
import polars as pl
import pytest

import transformer.actions  # noqa: F401
from transformer.actions.base import ACTION_SCHEMAS, AVAILABLE_WRANGLING_ACTIONS as ACTIONS

NAN = float("nan")
TIED = pl.DataFrame({"id": list("abcde"), "v": [9, 7, 7, 7, 5]})


def run(action, frame, **spec):
    return ACTIONS[action](frame.lazy(), spec).collect()


@pytest.mark.parametrize("name", ["polars_top_k", "polars_bottom_k"])
def test_exactly_k_rows_come_back_when_rows_are_tied_at_the_cut(name):
    out = run(name, TIED, k=3, by=["v"])
    assert out.height == 3
    assert run("polars_top_k", TIED, k=3, by=["v"])["v"].to_list() == [9, 7, 7]  # one of the three 7s is left out


def test_a_nan_comes_first_in_top_k_and_last_in_bottom_k():
    frame = pl.DataFrame({"id": list("abcd"), "v": [9.0, NAN, 7.0, 7.0]})
    top = run("polars_top_k", frame, k=2, by=["v"])
    assert top["id"].to_list() == ["b", "a"]
    assert run("polars_bottom_k", frame, k=2, by=["v"])["v"].to_list() == [7.0, 7.0]


def test_rows_with_no_value_fill_the_k_rows_when_the_real_values_run_out():
    frame = pl.DataFrame({"id": list("abc"), "v": [None, None, 5]})
    out = run("polars_top_k", frame, k=2, by=["v"])
    assert out.height == 2 and 5 in out["v"].to_list() and out["v"].null_count() == 1
    many = pl.DataFrame({"id": list("abcde"), "v": [9, None, 7, None, 7]})
    assert run("polars_top_k", many, k=3, by=["v"])["v"].to_list() == [9, 7, 7]  # a null is skipped while real values last


def test_a_row_number_as_the_last_by_column_keeps_the_first_tied_rows_in_table_order():
    numbered = run("polars_with_row_index", TIED, name="row_no")
    out = run("polars_top_k", numbered, k=3, by=["v", "row_no"], reverse=[False, True])
    assert out["id"].to_list() == ["a", "b", "c"]


def test_a_stable_sort_then_head_keeps_the_same_rows():
    out = run("polars_head", run("polars_sort", TIED, by=["v"], descending=True, maintain_order=True), n=3)
    assert out["id"].to_list() == ["a", "b", "c"]


def test_rank_with_method_min_and_a_filter_keeps_every_row_tied_with_the_k_best():
    ranked = run("polars_rank", TIED, columns=["v"], method="min", descending=True, target_column="r")
    kept = run("modif_filter", ranked, column="r", op="le", value=3, na="remove")
    assert kept["id"].to_list() == ["a", "b", "c", "d"]  # four rows for k = 3: all the 7s


@pytest.mark.parametrize("name", ["polars_top_k", "polars_bottom_k"])
def test_the_description_states_what_is_true_and_not_the_old_claim(name):
    text = ACTION_SCHEMAS[name]["description"]
    assert "not the input order" not in text
    for needed in ("exactly `k` rows", "not fixed", "streaming", "NaN", "no value", "row number", "polars_sort", "polars_head", "polars_rank", "min"):
        assert needed in text, needed
