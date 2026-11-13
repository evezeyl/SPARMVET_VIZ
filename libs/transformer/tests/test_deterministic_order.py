"""The same input must give the same output, in the same row order (reproducibility).

Polars runs many operations on several threads and promises no row order unless it is asked
for. Each wrangling action that could reorder rows has a stated rule, and this file checks the
rule on data large enough that a random order would show:

  polars_group_by  groups come out in the order they first appear in the input (`maintain_order` is written in the step)
  polars_sort      rows with equal keys keep their input order (`maintain_order` is written)
  polars_join      left/inner keep the order of the left table, right keeps the right table's (`maintain_order` is written)
  polars_unique    keeps the FIRST row of each duplicate group, in the input order (`keep` and `maintain_order` are written)
  polars_sample    the same seed gives the same sample; the seed is written in the step (no default seed any more)
  step_top_n_other equal counts are ranked by the value, so the same top N every run

The order rules used to be defaults of the actions (ADR-090); they are parameters that the recipe states now, so each test
writes them.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_deterministic_order.py -q
"""
import random

import polars as pl
import pytest

import transformer.actions  # noqa: F401
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS as ACTIONS
from utils.errors import TransformationError


def action_summarize(lf, spec):
    return ACTIONS["polars_group_by"](lf, {"by": spec["group_by"], "maintain_order": True,
                                           "named_aggs": {f"{c}_count": f"pl.col({c!r}).count()" for c in spec["columns"]}})


def action_sort(lf, spec):
    return ACTIONS["polars_sort"](lf, {"maintain_order": True, **spec})


def join_action(lf, spec):
    how = spec["how"]
    on = spec["on"] if isinstance(spec["on"], list) else [spec["on"]]
    return ACTIONS["polars_join"](lf, {"right_ingredient": "R", "on": on, "how": how, "__right_df__": spec["__right_df__"],
                                       "maintain_order": "right_left" if how == "right" else "left_right"})


def action_drop_duplicates(lf, spec):
    return ACTIONS["polars_unique"](lf, {"subset": spec["columns"], "keep": "first", "maintain_order": True})


def action_unique_rows(lf, spec):
    return ACTIONS["polars_unique"](lf, {"keep": "any", "maintain_order": True})


def action_sample(lf, spec):
    return ACTIONS["polars_sample"](lf, spec)


def action_top_n_other(lf, spec):
    return ACTIONS["step_top_n_other"](lf, {"other_label": "Other", "new_column": f"{spec['column']}_top{spec['n']}", **spec})

N = 40_000
RUNS = 5  # the same call several times: a random order differs between runs


@pytest.fixture(scope="module")
def data():
    rng = random.Random(1)
    groups = [rng.randrange(3000) for _ in range(N)]     # many groups, in a random order
    ties = [rng.randrange(5) for _ in range(N)]          # few distinct values: many ties
    return pl.DataFrame({"row_id": list(range(N)), "group": groups, "tie": ties})


def first_appearance(values):
    return list(dict.fromkeys(values))


def test_summarize_returns_groups_in_first_appearance_order(data):
    expected = first_appearance(data["group"].to_list())
    for _ in range(RUNS):
        out = action_summarize(data.lazy(), {"columns": ["row_id"], "group_by": ["group"], "agg": "count"}).collect()
        assert out["group"].to_list() == expected


def test_sort_keeps_the_input_order_of_ties(data):
    ties = data["tie"].to_list()
    expected = sorted(range(N), key=lambda i: ties[i])      # Python's sort is stable
    for _ in range(RUNS):
        out = action_sort(data.lazy(), {"by": ["tie"]}).collect()
        assert out["row_id"].to_list() == expected


def test_sort_descending_keeps_the_input_order_of_ties(data):
    ties = data["tie"].to_list()
    expected = sorted(range(N), key=lambda i: -ties[i])
    for _ in range(RUNS):
        out = action_sort(data.lazy(), {"by": ["tie"], "descending": True}).collect()
        assert out["row_id"].to_list() == expected


def _lookup():
    rng = random.Random(2)
    keys = list(range(0, 3000, 2))                          # only even keys exist on the right
    rng.shuffle(keys)
    return pl.DataFrame({"group": keys, "label": [f"k{k}" for k in keys]})


def test_left_join_keeps_the_order_of_the_left_table(data):
    for _ in range(RUNS):
        out = join_action(data.lazy(), {"__right_df__": _lookup().lazy(), "on": "group", "how": "left"}).collect()
        assert out["row_id"].to_list() == data["row_id"].to_list()


def test_inner_join_keeps_the_order_of_the_left_table(data):
    even = [g % 2 == 0 for g in data["group"].to_list()]
    expected = [r for r, keep in zip(data["row_id"].to_list(), even) if keep]
    for _ in range(RUNS):
        out = join_action(data.lazy(), {"__right_df__": _lookup().lazy(), "on": "group", "how": "inner"}).collect()
        assert out["row_id"].to_list() == expected


def test_right_join_keeps_the_order_of_the_right_table():
    left = pl.DataFrame({"group": list(range(0, 3000)), "x": list(range(3000))})
    right = _lookup()
    for _ in range(RUNS):
        out = join_action(left.lazy(), {"__right_df__": right.lazy(), "on": "group", "how": "right"}).collect()
        assert out["group"].to_list() == right["group"].to_list()


def test_drop_duplicates_keeps_the_first_row_of_each_group_in_input_order(data):
    first_rows = {}
    for row_id, group in zip(data["row_id"].to_list(), data["group"].to_list()):
        first_rows.setdefault(group, row_id)
    expected = list(first_rows.values())
    for _ in range(RUNS):
        out = action_drop_duplicates(data.lazy(), {"columns": ["group"]}).collect()
        assert out["row_id"].to_list() == expected


def test_unique_rows_keeps_input_order(data):
    doubled = pl.concat([data, data])
    expected = data["row_id"].to_list()
    for _ in range(RUNS):
        out = action_unique_rows(doubled.lazy(), {}).collect()
        assert out["row_id"].to_list() == expected


def test_sample_has_no_default_seed_any_more(data):
    with pytest.raises(TransformationError, match="seed"):
        action_sample(data.lazy(), {"fraction": 0.1})


def test_sample_with_an_explicit_seed_is_repeatable_and_a_different_seed_differs(data):
    a = action_sample(data.lazy(), {"fraction": 0.1, "seed": 7}).collect()["row_id"].to_list()
    b = action_sample(data.lazy(), {"fraction": 0.1, "seed": 7}).collect()["row_id"].to_list()
    c = action_sample(data.lazy(), {"fraction": 0.1, "seed": 8}).collect()["row_id"].to_list()
    assert a == b and a != c


def test_many_to_many_join_gives_left_order_then_right_order():
    """Several matches per key on both sides (samples x genes): the matches of one left row keep the
    order they have in the right table. "maintain_order=left" alone did not guarantee this."""
    rng = random.Random(5)
    left = pl.DataFrame({"lid": list(range(74)), "k": [rng.randrange(42) for _ in range(74)]})
    right = pl.DataFrame({"rid": list(range(984)), "k": [rng.randrange(42) for _ in range(984)]})
    by_key: dict = {}
    for rid, k in zip(right["rid"].to_list(), right["k"].to_list()):
        by_key.setdefault(k, []).append(rid)
    for how in ("inner", "left"):
        expected = []
        for lid, k in zip(left["lid"].to_list(), left["k"].to_list()):
            matches = by_key.get(k)
            if matches:
                expected += [(lid, rid) for rid in matches]
            elif how == "left":
                expected.append((lid, None))
        for _ in range(RUNS):
            out = join_action(left.lazy(), {"__right_df__": right.lazy(), "on": "k", "how": how}).collect()
            assert list(zip(out["lid"].to_list(), out["rid"].to_list())) == expected


def test_top_n_other_keeps_the_same_values_on_every_run_with_many_ties(data):
    # 3000 groups with few rows each: many groups share a count, so only the tie rule decides
    kept = []
    for _ in range(RUNS):
        out = action_top_n_other(data.lazy(), {"column": "group", "n": 25}).collect()
        kept.append(sorted(set(out["group_top25"].to_list()) - {"Other"}))
    assert all(k == kept[0] for k in kept) and len(kept[0]) == 25
