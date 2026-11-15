"""A join whose `validate` is not met says it in plain words (D35b, PROVISIONAL, Eve 2026-11-15; Polars 1.40.1).

Polars checks `validate` when the plan runs and says "join keys did not fulfill 1:1 validation". The step now names the step, the
table that is not unique, the key, what `validate` asked, what was found (how many key values repeat, one example) and the fix.
One test per value Polars has: 1:1 (both sides unique), 1:m (the left side unique), m:1 (the right side unique), m:m (nothing asked).
A null key counts as a repeat only with `nulls_equal: true` (as in Polars). Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_join_validate_message.py -q
"""
import polars as pl
import pytest

import transformer.actions  # noqa: F401
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS as ACTIONS
from utils.errors import TransformationError

LEFT_DUP = pl.DataFrame({"k": [1, 1, 2], "a": [1, 2, 3]})
RIGHT_DUP = pl.DataFrame({"k": [1, 2, 2], "w": [1, 2, 3]})
UNIQUE = pl.DataFrame({"k": [1, 2, 3], "w": [1, 2, 3]})


def join(left, right, validate, **more):
    spec = {"right_ingredient": "R", "on": ["k"], "how": "inner", "validate": validate, "maintain_order": "left_right", "__right_df__": right.lazy(), **more}
    return ACTIONS["polars_join"](left.lazy(), spec).collect()


@pytest.mark.parametrize("validate, left, right, side", [
    ("1:1", LEFT_DUP, UNIQUE, "first table"), ("1:1", UNIQUE, RIGHT_DUP, "second table"),
    ("1:m", LEFT_DUP, UNIQUE, "first table"),
    ("m:1", UNIQUE, RIGHT_DUP, "second table"),
], ids=["1:1-left", "1:1-right", "1:m-left", "m:1-right"])
def test_a_validate_that_is_not_met_is_refused_in_plain_words(validate, left, right, side):
    with pytest.raises(TransformationError) as caught:
        join(left, right, validate)
    text = str(caught.value)
    assert "did not fulfill" not in text, "the raw Polars message must not be passed on"
    assert "polars_join" in text and f"validate '{validate}'" in text and "'k'" in text and side in text and "'R'" in text
    assert "repeat" in text and "appears" in text
    assert caught.value.tip and "validate" in caught.value.tip


@pytest.mark.parametrize("validate, left, right", [
    ("1:1", UNIQUE, UNIQUE), ("1:m", UNIQUE, RIGHT_DUP), ("m:1", LEFT_DUP, UNIQUE),
    ("m:m", LEFT_DUP, RIGHT_DUP),
], ids=["1:1", "1:m", "m:1", "m:m"])
def test_a_validate_that_is_met_runs_and_gives_the_rows_of_polars(validate, left, right):
    out = join(left, right, validate)
    assert out.equals(left.lazy().join(right.lazy(), on="k", how="inner", validate=validate, maintain_order="left_right").collect())


def test_m_m_never_refuses_and_a_step_without_validate_is_unchanged():
    assert join(LEFT_DUP, RIGHT_DUP, "m:m").height == 4
    spec = {"right_ingredient": "R", "on": ["k"], "how": "inner", "maintain_order": "left_right", "__right_df__": RIGHT_DUP.lazy()}
    assert ACTIONS["polars_join"](LEFT_DUP.lazy(), spec).collect().height == 4


def test_a_null_key_is_a_repeat_only_with_nulls_equal_like_in_polars():
    nulls = pl.DataFrame({"k": [None, None, 1], "a": [1, 2, 3]})
    assert join(nulls, UNIQUE, "1:m").height == 1  # polars: ok
    with pytest.raises(TransformationError, match="repeat"):
        join(nulls, UNIQUE, "1:m", nulls_equal=True)


def test_left_on_and_right_on_are_read_and_the_message_names_the_columns():
    left = pl.DataFrame({"x": [1, 1], "a": [1, 2]})
    right = pl.DataFrame({"y": [1, 2], "w": [1, 2]})
    spec = {"right_ingredient": "R", "left_on": ["x"], "right_on": ["y"], "how": "inner", "validate": "1:1", "maintain_order": "left_right", "__right_df__": right.lazy()}
    with pytest.raises(TransformationError, match=r"'x'"):
        ACTIONS["polars_join"](left.lazy(), spec).collect()
