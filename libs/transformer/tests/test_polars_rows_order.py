"""The order rules of the row actions (ADR-090, the same input gives the same rows in the same order).

The actions of the group "rows" work on positions or ranks, so what they return depends on the order of the table at
that step. The rule of each one is stated in its description; this file checks the rule on data large enough that a
random order would show, several runs each:

  polars_head, polars_limit  the first n rows of the table, in the table order
  polars_tail                the last n rows, in the table order
  polars_slice               the rows from offset, in the table order
  polars_gather_every        every n-th row from offset, in the table order
  polars_reverse             exactly the table read from the end
  polars_with_row_index      the number is the position in the table order (0, 1, 2, ...)
  polars_remove              the rows that stay keep their order
  polars_top_k, bottom_k     ordered by the values of `by`; among tied rows Polars keeps none in a promised way, so a
                             recipe that needs a fixed result ends `by` with a unique column: then the result is exact
  after a polars_sort with maintain_order, every position rule gives one result, run after run

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_polars_rows_order.py -q
"""
import random

import polars as pl
import pytest

import transformer.actions  # noqa: F401
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS as ACTIONS

N = 40_000
RUNS = 5


@pytest.fixture(scope="module")
def data():
    rng = random.Random(3)
    return pl.DataFrame({"row_id": list(range(N)), "tie": [rng.randrange(5) for _ in range(N)], "v": [rng.randrange(1000) for _ in range(N)]})


def ids(lf):
    return lf.collect()["row_id"].to_list()


def test_head_limit_tail_slice_gather_every_follow_the_table_order(data):
    rows = list(range(N))
    for _ in range(RUNS):
        assert ids(ACTIONS["polars_head"](data.lazy(), {"n": 7})) == rows[:7]
        assert ids(ACTIONS["polars_limit"](data.lazy(), {"n": 7})) == rows[:7]
        assert ids(ACTIONS["polars_tail"](data.lazy(), {"n": 7})) == rows[-7:]
        assert ids(ACTIONS["polars_slice"](data.lazy(), {"offset": 100, "length": 5})) == rows[100:105]
        assert ids(ACTIONS["polars_slice"](data.lazy(), {"offset": -3})) == rows[-3:]
        assert ids(ACTIONS["polars_gather_every"](data.lazy(), {"n": 1000, "offset": 3})) == rows[3::1000]


def test_reverse_is_exactly_the_table_read_from_the_end(data):
    for _ in range(RUNS):
        assert ids(ACTIONS["polars_reverse"](data.lazy(), {})) == list(range(N))[::-1]


def test_reverse_twice_is_the_identity(data):
    once = ACTIONS["polars_reverse"](data.lazy(), {})
    assert ids(ACTIONS["polars_reverse"](once, {})) == list(range(N))


def test_with_row_index_numbers_the_rows_in_the_table_order(data):
    reversed_lf = ACTIONS["polars_reverse"](data.lazy(), {})
    for _ in range(RUNS):
        out = ACTIONS["polars_with_row_index"](reversed_lf, {"name": "pos", "offset": 0}).collect()
        assert out["pos"].to_list() == list(range(N))
        assert out["row_id"].to_list() == list(range(N))[::-1]          # the number follows the order at this step


def test_remove_keeps_the_order_of_the_rows_that_stay(data):
    ties = data["tie"].to_list()
    expected = [i for i in range(N) if not ties[i] == 2]
    for _ in range(RUNS):
        assert ids(ACTIONS["polars_remove"](data.lazy(), {"predicates": ["pl.col('tie') == 2"]})) == expected


def test_after_a_stable_sort_the_position_rules_give_one_result(data):
    ties = data["tie"].to_list()
    ordered = sorted(range(N), key=lambda i: ties[i])                   # Python's sort is stable
    for _ in range(RUNS):
        sorted_lf = ACTIONS["polars_sort"](data.lazy(), {"by": ["tie"], "maintain_order": True})
        assert ids(ACTIONS["polars_head"](sorted_lf, {"n": 50})) == ordered[:50]
        assert ids(ACTIONS["polars_tail"](sorted_lf, {"n": 50})) == ordered[-50:]


def test_top_k_and_bottom_k_with_a_unique_last_key_are_exact(data):
    ties = data["tie"].to_list()
    by_largest = sorted(range(N), key=lambda i: (-ties[i], i))           # largest tie first, the row number breaks the tie
    by_smallest = sorted(range(N), key=lambda i: (ties[i], i))
    for _ in range(RUNS):
        top = ids(ACTIONS["polars_top_k"](data.lazy(), {"k": 50, "by": ["tie", "row_id"], "reverse": [False, True]}))
        bottom = ids(ACTIONS["polars_bottom_k"](data.lazy(), {"k": 50, "by": ["tie", "row_id"], "reverse": [False, False]}))
        assert top == by_largest[:50]
        assert bottom == by_smallest[:50]


def test_top_k_with_tied_values_is_reproducible_run_after_run_but_only_by_the_values_it_promises(data):
    """What Polars promises for ties is the values, not the rows: the values are checked, the rows are only repeatable here."""
    runs = [ids(ACTIONS["polars_top_k"](data.lazy(), {"k": 50, "by": ["tie"]})) for _ in range(RUNS)]
    assert all(r == runs[0] for r in runs)
    assert set(data["tie"].to_list()[i] for i in runs[0]) == {4}
    assert len(set(runs[0])) == 50
