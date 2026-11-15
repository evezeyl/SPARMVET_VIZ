"""The Blueprint join preview shows only expected errors as "Preview failed" (D13).

A programming error (a missing import once was shown as the user's mistake) must not be swallowed.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_join_preview_errors.py -q
"""
import polars as pl
import pytest

from app.handlers.blueprint_handlers import JOIN_PREVIEW_INTERNAL_ERROR, run_join_preview, safe_join_preview
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
                                   FileNotFoundError("recipe gone"),
                                   pl.exceptions.ColumnNotFoundError("key")])
def test_an_expected_error_is_shown_with_its_message(error):
    def materialise(ingredient_id):
        raise error
    result = run_join_preview(materialise, _rows, "l", "r", ["k"], ["k"])
    assert result["error"].startswith("Preview failed: ") and str(error) in result["error"]


@pytest.mark.parametrize("error", [NameError("check_join_keys"), AttributeError("x"), TypeError("x"), ImportError("x"), KeyError("x"),
                                   ValueError("bad int()")])
def test_a_programming_error_is_not_shown_as_the_users_mistake(error):
    def materialise(ingredient_id):
        raise error
    with pytest.raises(type(error)):
        run_join_preview(materialise, _rows, "l", "r", ["k"], ["k"])


# -- the effect: no exception may escape it (Shiny closes the session of the user otherwise)

@pytest.mark.parametrize("error", [NameError("check_join_keys"), AttributeError("x"), TypeError("x"), KeyError("x"),
                                   ValueError("bad int()")])
def test_the_effect_catches_a_programming_error_and_says_it_is_internal(error, caplog):
    def materialise(ingredient_id):
        raise error
    result = safe_join_preview(materialise, _rows, "l", "r", ["k"], ["k"])
    assert result == {"error": JOIN_PREVIEW_INTERNAL_ERROR}
    assert any(r.exc_info and r.exc_info[1] is error for r in caplog.records)  # the traceback is in the log


def test_the_two_messages_differ():
    def user_error(ingredient_id):
        raise IngestionError("Dataset 'x' could not be loaded")
    def bug(ingredient_id):
        raise NameError("x")
    mine = safe_join_preview(user_error, _rows, "l", "r", ["k"], ["k"])["error"]
    internal = safe_join_preview(bug, _rows, "l", "r", ["k"], ["k"])["error"]
    assert mine != internal
    assert "internal error" in internal and "internal error" not in mine
    assert "Dataset 'x' could not be loaded" in mine
