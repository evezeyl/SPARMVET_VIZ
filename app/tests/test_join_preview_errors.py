"""The Blueprint join preview shows only expected errors as "Preview failed" (D13).

A programming error (a missing import once was shown as the user's mistake) must not be swallowed.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_join_preview_errors.py -q
"""
import polars as pl
import pytest

from app.handlers.blueprint_handlers import run_join_preview
from utils.errors import IngestionError


def _frame(rows):
    lf = pl.LazyFrame(rows)
    return lf, {k: str(v) for k, v in lf.collect_schema().items()}


def _rows(lf, keys):
    return lf.select([pl.col(k) for k in keys]).unique().collect().rows()


def _ok(ingredient_id):
    return _frame({"sample_id": ["a", "b"]})


def test_a_good_preview_has_the_match_stats():
    result = run_join_preview(_ok, _rows, "l", "r", ["sample_id"], ["sample_id"])
    assert result["error"] is None and result["verdict"]["ok"]
    assert result["_meta"]["left_ing"] == "l"


@pytest.mark.parametrize("error", [IngestionError("Dataset 'x' could not be loaded"),
                                   ValueError("No join or data schema 'x'"),
                                   FileNotFoundError("recipe gone"),
                                   pl.exceptions.ColumnNotFoundError("key")])
def test_an_expected_error_is_shown_with_its_message(error):
    def materialise(ingredient_id):
        raise error
    result = run_join_preview(materialise, _rows, "l", "r", ["k"], ["k"])
    assert result["error"].startswith("Preview failed: ") and str(error) in result["error"]


@pytest.mark.parametrize("error", [NameError("check_join_keys"), AttributeError("x"), TypeError("x"), ImportError("x")])
def test_a_programming_error_is_not_shown_as_the_users_mistake(error):
    def materialise(ingredient_id):
        raise error
    with pytest.raises(type(error)):
        run_join_preview(materialise, _rows, "l", "r", ["k"], ["k"])
