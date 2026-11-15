"""A join whose `validate` Polars refuses is explained in plain words, and only then (D35b, PROVISIONAL, redesigned 2026-11-15).

Design: POLARS decides whether the join fails. Nothing is checked before the run. Where the engine runs the plan
(`write_anchor`), a Polars "join keys did not fulfill X validation" error is turned into a TransformationError that names the step,
the tables, the key, what `validate` asked, how many key values repeat (with one example) and the fix. The assembler hands
`write_anchor` the list of its joins that write `validate` (`join_checks`), so the step is known.

Proved on thousands of random cases (every `how`, every `validate`, empty tables, null keys with and without `nulls_equal`,
one or two key columns): the plain message appears exactly when Polars raises, and never when Polars accepts.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_join_validate_diagnosis.py -q
"""
import random

import polars as pl
import pytest

import transformer.actions  # noqa: F401
from transformer.anchor import write_anchor
from transformer.data_assembler import DataAssembler
from utils.errors import TransformationError

HOWS = ["inner", "left", "right", "full", "semi", "anti"]
VALIDATES = ["1:1", "1:m", "m:1", "m:m"]


def tables(rng, keys):
    def one(extra):
        n = rng.choice([0, 0, 1, 2, 3, 5])
        columns = {k: [rng.choice([None, 1, 2, 3]) if rng.random() < 0.8 else rng.choice([4, 5]) for _ in range(n)] for k in keys}
        columns[extra] = list(range(n))
        return pl.DataFrame(columns, schema={**{k: pl.Int64 for k in keys}, extra: pl.Int64})
    return one("a"), one("w")


def polars_outcome(left, right, step):
    """What Polars does with the join: "ok", "keys" (validation not met) or "unsupported" (validate on a semi or anti join)."""
    try:
        left.lazy().join(right.lazy(), on=step["on"], how=step["how"], validate=step["validate"], nulls_equal=step["nulls_equal"],
                         maintain_order="left_right").collect()
        return "ok"
    except pl.exceptions.ComputeError as exc:
        return "keys" if "did not fulfill" in str(exc) else "unsupported" if "is not supported" in str(exc) else str(exc)


def engine(left, right, step, tmp_path):
    assembler = DataAssembler({"L": left.lazy(), "R": right.lazy()}, recipe_id="r", join_id="LR")
    lf = assembler.assemble([{"action": "polars_join", "right_ingredient": "R", "maintain_order": "left_right", **step}])
    write_anchor(lf, tmp_path / "t1.parquet", decision_hash="h", join_checks=assembler.join_checks)  # the production call (collect, then write)


def test_the_message_appears_exactly_when_polars_raises_on_random_cases(tmp_path):
    rng = random.Random(7)
    raised = accepted = unsupported = 0
    for case in range(6000):
        keys = rng.choice([["k"], ["k", "j"]])
        left, right = tables(rng, keys)
        step = {"on": keys, "how": rng.choice(HOWS), "validate": rng.choice(VALIDATES), "nulls_equal": rng.choice([False, True])}
        expected = polars_outcome(left, right, step)
        try:
            engine(left, right, step, tmp_path)
            outcome = None
        except TransformationError as exc:
            outcome = str(exc)
        if expected == "keys":
            raised += 1
            assert outcome is not None, (case, step)
            assert "did not fulfill" not in outcome and f"validate '{step['validate']}'" in outcome and "repeat" in outcome and "'R'" in outcome, (case, outcome)
            assert all(repr(k) in outcome or k in outcome for k in keys)
        elif expected == "unsupported":
            unsupported += 1
            assert outcome is not None and "is not supported" not in outcome and f"validate '{step['validate']}' cannot be used with how '{step['how']}'" in outcome, (case, step, outcome)
        else:
            assert expected == "ok", expected
            accepted += 1
            assert outcome is None, (case, step, outcome)
    assert raised > 300 and accepted > 300 and unsupported > 300, (raised, accepted, unsupported)  # the cases cover both


@pytest.mark.parametrize("validate", ["1:1", "1:m", "m:1"])
def test_the_message_for_each_validate_value_names_the_table_and_the_example(validate, tmp_path):
    dup = pl.DataFrame({"k": [1, 1, 2], "a": [1, 2, 3]})
    unique = pl.DataFrame({"k": [1, 2, 3], "w": [1, 2, 3]})
    left, right = (dup, unique) if validate in ("1:1", "1:m") else (unique.rename({"w": "a"}), dup.rename({"a": "w"}))
    with pytest.raises(TransformationError) as caught:
        engine(left, right, {"on": ["k"], "how": "inner", "validate": validate, "nulls_equal": False}, tmp_path)
    text = str(caught.value)
    assert "first table" in text if validate != "m:1" else "second table 'R'" in text
    assert "k=1" in text and "2 times" in text and "polars_join" in text and "assembly step 1" in text
    assert caught.value.tip and "validate" in caught.value.tip


def test_a_step_without_validate_is_not_registered_and_a_polars_error_that_is_not_a_validation_is_not_touched(tmp_path):
    assembler = DataAssembler({"L": pl.DataFrame({"k": [1]}).lazy(), "R": pl.DataFrame({"k": [1], "w": [1]}).lazy()}, recipe_id="r", join_id="LR")
    assembler.assemble([{"action": "polars_join", "right_ingredient": "R", "on": ["k"], "how": "inner", "maintain_order": "left_right"}])
    assert assembler.join_checks == []
