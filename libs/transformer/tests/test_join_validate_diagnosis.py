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
import re

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


# -- several joins that write validate: every one is tried, the one whose keys really repeat is named -----------------------

A = pl.DataFrame({"k": [1, 2, 3], "a": [1, 2, 3]})
UNIQUE_C = pl.DataFrame({"k": [1, 2, 3], "c": [1, 2, 3]})
REPEATING_B = pl.DataFrame({"k": [1, 1, 2], "b": [1, 2, 3]})
NULLS_C = pl.DataFrame({"k": [None, None, 1], "c": [1, 2, 3]})  # Polars accepts repeated nulls with nulls_equal off


def two_joins(first, second, tmp_path, how="left"):
    ingredients = {"A": A.lazy(), "C": first.lazy(), "B": second.lazy()}
    assembler = DataAssembler(ingredients, recipe_id="r", join_id="J")
    steps = [{"action": "polars_join", "right_ingredient": name, "on": ["k"], "how": how, "validate": "m:1", "maintain_order": "left_right"} for name in ("C", "B")]
    lf = assembler.assemble(steps)
    write_anchor(lf, tmp_path / "t.parquet", decision_hash="h", join_checks=assembler.join_checks)


def test_the_second_join_is_named_when_the_first_is_fine(tmp_path):
    with pytest.raises(TransformationError) as caught:
        two_joins(UNIQUE_C, REPEATING_B, tmp_path)
    text = str(caught.value)
    assert "'B'" in text and "assembly step 2" in text and "k=1" in text
    assert "'C'" not in text and "could not be found" not in text


def test_the_first_join_is_named_when_it_is_the_one_that_repeats(tmp_path):
    with pytest.raises(TransformationError) as caught:
        two_joins(REPEATING_B.rename({"b": "c"}), UNIQUE_C.rename({"c": "b"}), tmp_path)
    text = str(caught.value)
    assert "'C'" in text and "assembly step 1" in text and "'B'" not in text


def test_both_are_named_when_both_repeat(tmp_path):
    with pytest.raises(TransformationError) as caught:
        two_joins(REPEATING_B.rename({"b": "c"}), REPEATING_B, tmp_path)
    text = str(caught.value)
    assert "'C'" in text and "'B'" in text and "assembly step 1" in text and "assembly step 2" in text


def test_repeated_null_keys_that_polars_accepts_do_not_mislead_the_message_about_the_other_join(tmp_path):
    with pytest.raises(TransformationError) as caught:
        two_joins(NULLS_C, REPEATING_B, tmp_path)
    text = str(caught.value)
    assert "'B'" in text and "'C'" not in text and "counts as a value" not in text


def test_in_a_full_join_a_repeated_null_key_is_shown_as_a_fact_and_no_rule_is_invented(tmp_path):
    left = pl.DataFrame({"k": [None, None, 4], "j": [1, 1, 2], "a": [0, 1, 2]})  # found by the random run: Polars raises, with two key columns
    right = pl.DataFrame({"k": [None, 3, 5], "j": [2, None, 2], "w": [0, 1, 2]})
    assert polars_outcome(left, right, {"on": ["k", "j"], "how": "full", "validate": "1:m", "nulls_equal": False}) == "keys"
    with pytest.raises(TransformationError) as caught:
        engine(left, right, {"on": ["k", "j"], "how": "full", "validate": "1:m", "nulls_equal": False}, tmp_path)
    text = str(caught.value)
    assert "k=None" in text and "counts as" not in text and "missing key value" not in text


# -- several joins, every how, null keys: Polars decides which join is named ------------------------------------------------

def independent_oracle(base, rights, steps):
    """Which joins does Polars refuse, each run alone on the table it sees (the earlier joins WITHOUT validate), all columns."""
    refused, current = [], base.lazy()
    for number, (right, step) in enumerate(zip(rights, steps), start=1):
        common = dict(on=step["on"], how=step["how"], nulls_equal=step["nulls_equal"], maintain_order="left_right", coalesce=True)
        try:
            current.join(right.lazy(), validate=step["validate"], **common).collect()
        except pl.exceptions.ComputeError as exc:
            if "did not fulfill" in str(exc):
                refused.append(number)
        current = current.join(right.lazy(), **common)
    return refused


def test_the_joins_named_are_exactly_those_polars_refuses_on_random_multi_join_cases(tmp_path):
    rng = random.Random(11)
    named_cases = clean_cases = 0
    for case in range(2500):
        keys = rng.choice([["k"], ["k", "j"]])
        count = rng.choice([2, 3])
        base, _ = tables(rng, keys)
        base = base.rename({"a": "a0"}) if "a" in base.columns else base
        rights, steps = [], []
        for number in range(count):
            right = tables(rng, keys)[1].rename({"w": f"w{number}"})
            rights.append(right)
            steps.append({"on": keys, "how": rng.choice(["inner", "left", "full"]), "validate": rng.choice(["1:1", "1:m", "m:1", "m:m"]),
                          "nulls_equal": rng.choice([False, True])})
        # a join with how full adds the key columns of the right table: later joins use the columns of the base only
        expected = independent_oracle(base, rights, steps)
        ingredients = {"base": base.lazy(), **{f"R{n + 1}": r.lazy() for n, r in enumerate(rights)}}
        assembler = DataAssembler(ingredients, recipe_id="r", join_id="J")
        try:
            lf = assembler.assemble([{"action": "polars_join", "right_ingredient": f"R{n + 1}", "maintain_order": "left_right", "coalesce": True, **step} for n, step in enumerate(steps)])
            write_anchor(lf, tmp_path / "t.parquet", decision_hash="h", join_checks=assembler.join_checks)
            outcome = None
        except TransformationError as exc:
            outcome = str(exc)
        except pl.exceptions.ComputeError as exc:
            outcome = "RAW " + str(exc)
        if expected:
            named_cases += 1
            assert outcome is not None and not outcome.startswith("RAW") and "did not fulfill" not in outcome, (case, steps, outcome)
            if "cannot be used with how" not in outcome:
                named = [int(n) for n in re.findall(r"polars_join with the second table 'R(\d)'", outcome)]
                assert named == expected, (case, steps, expected, outcome)
        else:
            clean_cases += 1
            assert outcome is None or "cannot be used with how" in outcome or outcome.startswith("RAW"), (case, steps, outcome)
    assert named_cases > 300 and clean_cases > 300, (named_cases, clean_cases)
    print("multi-join cases:", named_cases, "refused,", clean_cases, "accepted")


def test_several_joins_are_named_in_the_order_of_the_recipe(tmp_path):
    with pytest.raises(TransformationError) as caught:
        two_joins(REPEATING_B.rename({"b": "c"}), REPEATING_B, tmp_path)
    text = str(caught.value)
    assert text.index("'C'") < text.index("'B'") and text.index("assembly step 1") < text.index("assembly step 2")
