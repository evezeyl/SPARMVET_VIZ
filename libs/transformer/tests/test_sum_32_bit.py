"""The sum of a 32-bit whole-number column wraps around with no error (D43, PROVISIONAL; Polars 1.40.1, RUN).

The engine does not check it (Eve: a checker advice and a line in the description only). This pins the fact the advice and
the description state: the total of an Int32 column above about 2.1 thousand million is wrong, and right after a cast to Int64.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_sum_32_bit.py -q
"""
import polars as pl
import pytest

import transformer.actions  # noqa: F401
from transformer.actions.base import ACTION_SCHEMAS, AVAILABLE_WRANGLING_ACTIONS as ACTIONS

FRAME = pl.DataFrame({"n": [2_000_000_000, 2_000_000_000]}, schema={"n": pl.Int32})


def test_the_total_of_an_int32_column_wraps_around_and_is_right_after_the_cast():
    assert ACTIONS["polars_sum"](FRAME.lazy(), {}).collect()["n"].to_list() == [-294_967_296]
    cast = ACTIONS["polars_cast"](FRAME.lazy(), {"columns": ["n"], "dtype": "Int64"})
    assert ACTIONS["polars_sum"](cast, {}).collect()["n"].to_list() == [4_000_000_000]


def test_the_cumulative_sum_wraps_too():
    out = ACTIONS["polars_cum_sum"](FRAME.lazy(), {"columns": ["n"], "reverse": False}).collect()
    assert out["n"].to_list() == [2_000_000_000, -294_967_296]


@pytest.mark.parametrize("action", ["polars_sum", "polars_cum_sum"])
def test_the_description_says_so(action):
    text = ACTION_SCHEMAS[action]["description"]
    assert "Int32" in text and "wraps around" in text and "Int64" in text


# -- the note for a non-developer (ADVICE-TEXTS-1, Eve 2026-11-15): every number it states is run here -----------------
from pathlib import Path

PAGE = Path(__file__).resolve().parents[3] / "docs" / "appendix" / "transformer_actions.qmd"


def _total(values, dtype):
    return ACTIONS["polars_sum"](pl.DataFrame({"n": values}, schema={"n": dtype}).lazy(), {}).collect()["n"].to_list()[0]


def test_the_numbers_of_the_note_are_what_polars_gives():
    assert _total([2_000_000_000, 2_000_000_000], pl.Int32) == -294_967_296
    assert _total([2_000_000_000, 2_000_000_000], pl.Int64) == 4_000_000_000
    assert _total([0.1] * 10, pl.Float64) == 0.9999999999999999
    assert _total([9007199254740992.0, 1.0], pl.Float64) == 9007199254740992.0


@pytest.mark.parametrize("where", ["help", "page"])
def test_the_help_and_the_page_state_the_note_with_its_suggestion(where):
    text = ACTION_SCHEMAS["polars_sum"]["description"] if where == "help" else PAGE.read_text(encoding="utf-8")
    for needed in ("-294967296", "4000000000", "0.9999999999999999", "9007199254740992.0", "wraps around", "Suggestion: declare the column as 64-bit",
                   "Int64", "Float64", "does not matter"):
        assert needed in text, needed
