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
import yaml

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
    assert run("polars_top_k", frame, k=2, by=["v"])["id"].to_list() == ["b", "a"]
    assert run("polars_bottom_k", frame, k=2, by=["v"])["v"].to_list() == [7.0, 7.0]  # the NaN is not among the 2 smallest


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
def test_the_description_holds_only_what_was_established_by_running(name):
    text = ACTION_SCHEMAS[name]["description"]
    for needed in ("keeps at most `k` rows: exactly `k` when the table has `k` rows or more", "same value as the `k`-th row", "Polars does not promise which ones", "no value",
                   "Suggestion: to always keep the same rows", "polars_with_row_index", "last column of `by`",
                   "Suggestion: to keep every row that ties with the `k` best", "polars_rank (method min)", "more than `k` rows"):
        assert needed in text, needed
    assert text.count("Suggestion:") == 2
    for removed in ("not the input order", "small table", "streaming", "differ from run to run", "first tied rows", "do not rely on it"):
        assert removed not in text, removed  # claims that the reviewer's runs did not support, or the old wording


def _suggestion_steps(name):
    """The two suggestions of the example, read back from its comments: ([row index step], [rank step, filter step])."""
    blocks, current = [], None
    for line in ACTION_SCHEMAS[name]["yaml_example"].splitlines():
        if line.startswith("# Suggestion"):
            current = []
            blocks.append(current)
        elif line.startswith("#   ") and current is not None:
            current.append(line[4:])
    return [yaml.safe_load("\n".join(block)) for block in blocks]


@pytest.mark.parametrize("name", ["polars_top_k", "polars_bottom_k"])
def test_the_example_holds_the_two_suggestions_as_steps_that_do_what_the_text_says(name):
    row_index, rank_and_filter = _suggestion_steps(name)
    step = yaml.safe_load("\n".join(l for l in ACTION_SCHEMAS[name]["yaml_example"].splitlines() if not l.startswith("#")))[0]
    # a table with ties at the cut: values 9, 7, 7, 7, 5 and k = 3; `identity` is the value, `sample_row` the row number
    table = pl.DataFrame({"id": list("abcde"), "identity": [9, 7, 7, 7, 5]})
    step = {**step, "k": 3}
    kept = []
    for _ in range(5):
        numbered = table.lazy()
        for s in row_index:
            numbered = ACTIONS[s["action"]](numbered, {k: v for k, v in s.items() if k != "action"})
        out = ACTIONS[name](numbered, {k: v for k, v in step.items() if k != "action"}).collect()
        kept.append(out["id"].to_list())
    assert all(k == kept[0] for k in kept) and len(kept[0]) == 3  # same rows on every run, exactly k rows
    best = ["a", "b", "c"] if name == "polars_top_k" else ["e", "b", "c"]
    assert kept[0] == best  # the first tied rows of the table, as the example says
    ranked = table.lazy()
    for s in rank_and_filter:
        s = {**s, "value": 3} if s["action"] == "modif_filter" else s  # the 10 of the example is k
        ranked = ACTIONS[s["action"]](ranked, {k: v for k, v in s.items() if k != "action"})
    out = ranked.collect()
    expected = ["a", "b", "c", "d"] if name == "polars_top_k" else ["e", "b", "c", "d"]
    assert sorted(out["id"].to_list()) == sorted(expected) and out.height > 3  # every row tied with the 3 best: more than k rows


def test_the_nan_sentence_is_right_for_each_action():
    top, bottom = ACTION_SCHEMAS["polars_top_k"]["description"], ACTION_SCHEMAS["polars_bottom_k"]["description"]
    assert "comes first, and last if `reverse` is true for that column" in top and "comes last, and first if" not in top
    assert "comes last, and first if `reverse` is true for that column" in bottom and "comes first, and last if" not in bottom


@pytest.mark.parametrize("name, place, other", [("polars_top_k", "first", "last"), ("polars_bottom_k", "last", "first")])
def test_reverse_puts_the_nan_on_the_other_side(name, place, other):
    frame = pl.DataFrame({"id": list("abcd"), "v": [9.0, NAN, 7.0, 7.0]})
    plain = run(name, frame, k=4, by=["v"], reverse=False)["id"].to_list()
    reverse = run(name, frame, k=4, by=["v"], reverse=True)["id"].to_list()
    assert (plain[0] == "b") if place == "first" else (plain[-1] == "b")
    assert (reverse[-1] == "b") if place == "first" else (reverse[0] == "b")
    assert f"comes {place}, and {other} if `reverse` is true for that column" in ACTION_SCHEMAS[name]["description"]


def test_the_nan_position_is_what_the_description_says():
    frame = pl.DataFrame({"id": list("abcd"), "v": [9.0, NAN, 7.0, 7.0]})
    assert run("polars_top_k", frame, k=4, by=["v"])["id"].to_list()[0] == "b"
    assert run("polars_bottom_k", frame, k=4, by=["v"])["id"].to_list()[-1] == "b"


@pytest.mark.parametrize("name", ["polars_top_k", "polars_bottom_k"])
def test_a_table_with_fewer_rows_than_k_comes_back_whole(name):
    assert run(name, TIED.head(3), k=10, by=["v"]).height == 3


@pytest.mark.parametrize("name, reverse, place", [("polars_top_k", [True, False], "last"), ("polars_top_k", [False, True], "first"),
                                                  ("polars_bottom_k", [True, False], "first"), ("polars_bottom_k", [False, True], "last")])
def test_with_a_list_the_nan_side_follows_the_reverse_entry_of_the_column_that_holds_it(name, reverse, place):
    frame = pl.DataFrame({"id": list("abcd"), "v": [9.0, NAN, 7.0, 7.0], "w": [1, 1, 1, 1]})
    ids = run(name, frame, k=4, by=["v", "w"], reverse=reverse)["id"].to_list()
    assert (ids[0] == "b") if place == "first" else (ids[-1] == "b")


@pytest.mark.parametrize("name, values, best", [("polars_top_k", [9, 8, 7, 7, 5], ["a", "b", "c", "d"]),
                                                ("polars_bottom_k", [1, 2, 3, 3, 5], ["a", "b", "c", "d"])])
def test_the_rank_suggestion_keeps_the_kth_value_and_every_row_tied_with_it(name, values, best):
    """Ranks are 1, 2, 3, 3, 5 for k = 3: a filter `lt` instead of `le` would drop the 3rd value and its tie."""
    _, rank_and_filter = _suggestion_steps(name)
    ranked = pl.DataFrame({"id": list("abcde"), "identity": values}).lazy()
    for s in rank_and_filter:
        s = {**s, "value": 3} if s["action"] == "modif_filter" else s
        ranked = ACTIONS[s["action"]](ranked, {k: v for k, v in s.items() if k != "action"})
    assert sorted(ranked.collect()["id"].to_list()) == best
