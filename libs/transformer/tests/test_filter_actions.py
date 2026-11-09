"""The ne/gt/lt/not_in filter actions (issue #52) — the counterparts filter_eq,
filter_range and is_in were missing, closing a gap found by the T3-to-recipe translator
(#47): approximating strict gt as inclusive ge would silently include one extra boundary
value, so the translator refused rather than approximate until these existed.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_filter_actions.py -q
"""
import polars as pl
import pytest

from transformer.actions.cleaning.core import action_filter_gt, action_filter_lt, action_filter_ne
from transformer.actions.cleaning.analytical import action_not_in
from utils.errors import TransformationError


def frame():
    return pl.DataFrame({"v": [1, 2, 3, 4, 5], "country": ["Norway", "Sweden", "Denmark", "Norway", "Finland"]}).lazy()


# ── filter_ne ────────────────────────────────────────────────────────────────

def test_filter_ne_keeps_rows_not_equal_to_the_value():
    out = action_filter_ne(frame(), {"column": "country", "value": "Norway"}).collect()
    assert out["country"].to_list() == ["Sweden", "Denmark", "Finland"]


def test_filter_ne_falls_back_to_columns_list():
    out = action_filter_ne(frame(), {"columns": ["country"], "value": "Norway"}).collect()
    assert out["country"].to_list() == ["Sweden", "Denmark", "Finland"]


def test_filter_ne_no_column_is_a_no_op():
    out = action_filter_ne(frame(), {"value": "Norway"}).collect()
    assert out.height == 5


# ── filter_gt / filter_lt ────────────────────────────────────────────────────

def test_filter_gt_is_strictly_exclusive():
    out = action_filter_gt(frame(), {"columns": ["v"], "value": 3}).collect()
    assert out["v"].to_list() == [4, 5]


def test_filter_lt_is_strictly_exclusive():
    out = action_filter_lt(frame(), {"columns": ["v"], "value": 3}).collect()
    assert out["v"].to_list() == [1, 2]


def test_filter_gt_no_columns_is_a_no_op():
    out = action_filter_gt(frame(), {"value": 3}).collect()
    assert out.height == 5


def test_filter_gt_no_value_is_a_no_op():
    out = action_filter_gt(frame(), {"columns": ["v"]}).collect()
    assert out.height == 5


# ── not_in ───────────────────────────────────────────────────────────────────

def test_not_in_excludes_the_listed_values():
    out = action_not_in(frame(), {"column": "country", "values": ["Norway", "Sweden"]}).collect()
    assert out["country"].to_list() == ["Denmark", "Finland"]


def test_not_in_raises_on_missing_column():
    with pytest.raises(TransformationError):
        action_not_in(frame(), {"values": ["Norway"]})


def test_not_in_raises_on_missing_values():
    with pytest.raises(TransformationError):
        action_not_in(frame(), {"column": "country"})


def test_is_in_and_not_in_are_exact_complements():
    from transformer.actions.cleaning.analytical import action_is_in
    base = frame()
    values = ["Norway", "Sweden"]
    kept = set(action_is_in(base, {"column": "country", "values": values}).collect()["country"].to_list())
    excluded = set(action_not_in(base, {"column": "country", "values": values}).collect()["country"].to_list())
    assert kept | excluded == set(base.collect()["country"].to_list())
    assert kept & excluded == set()
