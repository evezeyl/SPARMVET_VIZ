"""The build runs every self-join as written and gives a caution with the numbers (D-0183, D-0050, D-0099).

Eve 2026-11-16: "A self-join (a table joined with itself, the anti-join on the same key included) gives a warning, never an
error." Polars reports nothing and the anti-join of a table with itself is not always empty: it keeps the rows whose key is
missing, because a missing key never matches. The build says what the join did: rows before, rows after, and how many rows
have a missing key in the key columns. The text is `utils.join_keys.self_join_text`, the rule `self_join`, the same two the
checker asks (J12).

The caution is a `PipelineError` of severity "warning", printed and kept in `DataAssembler.cautions`; nothing carries it to
the screen yet (see the report of SELF-JOIN-WARN-1). The build never raises for a self-join.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_self_join_build.py -q
"""
import polars as pl
import pytest

import transformer.actions  # noqa: F401  (loads the registry)
from transformer.data_assembler import DataAssembler
from utils.action_names import JOIN, JOIN_ASOF, JOIN_WHERE

A = {"k": [1, 2, 2, 3, None, None], "x": [10, 20, 30, 40, 50, 60]}
B = {"k": [1, 3], "y": [10, 30]}


def assembler():
    return DataAssembler({"A": pl.LazyFrame(A), "B": pl.LazyFrame(B)}, recipe_id="demo", join_id="J")


def run(steps, a=assembler):
    asm = a()
    return asm, asm.assemble(steps).collect()


def step(right="A", how="anti", **keys):
    return {"action": JOIN, "right_ingredient": right, "how": how, "maintain_order": "left_right", **({"on": ["k"]} if not keys else keys)}


def evidence(asm):
    assert len(asm.cautions) == 1
    return asm.cautions[0].evidence


def test_the_anti_join_of_a_table_with_itself_builds_and_keeps_the_rows_whose_key_is_missing():
    asm, result = run([step()])
    assert result["x"].to_list() == [50, 60]            # Polars never matches a missing key
    assert result["k"].to_list() == [None, None]


def test_its_caution_has_the_real_numbers():
    asm, _ = run([step()])
    found = evidence(asm)
    assert found["row_count_before"] == 6 and found["row_count_after"] == 2
    assert found["rows_with_missing_key_left"] == 2 and found["rows_with_missing_key_right"] == 2
    caution = asm.cautions[0]
    assert caution.severity == "warning" and caution.component == "DataAssembler"
    assert "Rows before the join: 6; rows after: 2; rows with a missing key in ['k']: 2 in the table at this step and 2 in 'A'" in caution.problem
    assert "keeps only the rows whose key is missing" in caution.problem
    assert caution.fix.startswith("Suggestion:") and caution.fix.count("Suggestion:") == 2


def test_with_no_missing_key_the_anti_self_join_is_empty_and_the_numbers_say_so():
    asm = DataAssembler({"A": pl.LazyFrame({"k": [1, 2, 3]})}, recipe_id="demo", join_id="J")
    result = asm.assemble([step()]).collect()
    assert result.height == 0
    found = asm.cautions[0].evidence
    assert (found["row_count_before"], found["row_count_after"], found["rows_with_missing_key_left"]) == (3, 0, 0)


def test_with_nulls_equal_the_missing_keys_find_each_other_and_the_result_is_empty():
    asm, result = run([step(**{"on": ["k"], "nulls_equal": True})])
    assert result.height == 0
    assert "keeps no row" in asm.cautions[0].problem and asm.cautions[0].evidence["row_count_after"] == 0


def test_a_left_self_join_runs_and_has_a_caution_with_its_numbers():
    asm, result = run([step(how="left")])
    # the repeated key 2 matches 2 x 2 = 4 rows, 1 and 3 one row each, the two missing keys one row each without a partner
    assert result.height == 8
    found = evidence(asm)
    assert (found["row_count_before"], found["row_count_after"]) == (6, 8)
    assert "with the suffix `_right`" in asm.cautions[0].problem and "Rows before the join: 6; rows after: 8" in asm.cautions[0].problem


@pytest.mark.parametrize("how", ["inner", "semi", "full"])
def test_every_kind_of_self_join_runs_and_is_counted(how):
    asm, result = run([step(how=how)])
    assert evidence(asm)["row_count_after"] == result.height


def test_a_self_join_on_other_key_columns_runs_and_gets_its_caution():
    """Before D-0183 it had no message at all."""
    tables = {"A": pl.LazyFrame({"id": [1, 2, 3], "parent": [None, 1, 1]})}
    asm = DataAssembler(tables, recipe_id="demo", join_id="J")
    result = asm.assemble([step(how="left", left_on=["parent"], right_on=["id"])]).collect()
    assert result.height == 3
    found = asm.cautions[0].evidence
    assert (found["row_count_before"], found["row_count_after"], found["rows_with_missing_key_left"], found["rows_with_missing_key_right"]) == (3, 3, 1, 0)
    assert "left key ['parent'] and the right key ['id']" in asm.cautions[0].problem


def test_a_table_joined_before_and_joined_again_is_a_self_join():
    asm, _ = run([step(right="B", how="left"), step(right="B", how="left")])
    assert len(asm.cautions) == 1 and asm.cautions[0].location.endswith("assembly step 2: action='polars_join', right_ingredient='B'")


def test_the_as_of_join_of_a_table_with_itself_runs_and_is_counted():
    tables = {"A": pl.LazyFrame({"t": [1, 2, 3, None], "v": [1, 2, 3, 4]}).sort("t", nulls_last=False)}
    asm = DataAssembler(tables, recipe_id="demo", join_id="J")
    result = asm.assemble([{"action": JOIN_ASOF, "right_ingredient": "A", "on": "t", "strategy": "backward"}]).collect()
    found = asm.cautions[0].evidence
    assert found["row_count_before"] == 4 and found["row_count_after"] == result.height
    assert found["rows_with_missing_key_left"] == 1 and "as-of join" in asm.cautions[0].problem


def test_the_join_on_conditions_of_a_table_with_itself_has_rows_before_and_after_only():
    tables = {"A": pl.LazyFrame({"v": [1, 2, 3]})}
    asm = DataAssembler(tables, recipe_id="demo", join_id="J")
    result = asm.assemble([{"action": JOIN_WHERE, "right_ingredient": "A", "predicates": ["pl.col('v') < pl.col('v_right')"]}]).collect()
    found = asm.cautions[0].evidence
    assert (found["row_count_before"], found["row_count_after"]) == (3, 3) and result.height == 3
    assert found["rows_with_missing_key_left"] is None
    assert "join on conditions" in asm.cautions[0].problem and "missing key" not in asm.cautions[0].problem


def test_the_caution_is_printed(capsys):
    run([step()])
    out = capsys.readouterr().out
    assert "[WARN]" in out and "Rows before the join: 6; rows after: 2" in out and "Suggestion:" in out


def test_a_join_of_two_different_tables_gets_no_caution_and_no_count():
    asm, result = run([step(right="B", how="left")])
    assert asm.cautions == [] and result.height == 6


def test_a_self_join_that_fails_when_it_runs_is_still_reported_by_its_own_error_and_the_caution_says_it_could_not_count():
    """`validate` fails when the join runs; the counting meets the same failure, so the caution has no numbers and says why."""
    asm = assembler()
    lazy = asm.assemble([step(how="left", on=["k"], validate="1:1")])
    assert "could not be counted" in asm.cautions[0].problem and asm.cautions[0].evidence.get("row_count_before") is None
    with pytest.raises(Exception):
        lazy.collect()   # the engine's own error for `validate` is unchanged (anchor.py explains it for the user)


def test_the_build_never_raises_for_a_self_join():
    for how in ("anti", "left", "inner", "semi", "full"):
        run([step(how=how)])


# -- what the text of each kind of self-join claims is what a real run gives (fix round 2026-11-16) ------------------------------

from collections import Counter  # noqa: E402

from utils import join_keys  # noqa: E402

TABLES = {
    "unique key": ["a", "b", "c"],
    "repeated key and 2 missing keys": ["a", "a", "b", "c", None, None],
    "only missing keys": [None, None, None],
    "one row, missing": [None],
    "one value, three rows": ["a", "a", "a"],
}
PHRASE = {   # the part of the text that states the rule of each kind
    "left": "gives a x b rows, and a row with a missing key is kept once, with empty copied columns",
    "inner": "gives a x b rows, and a row with a missing key is dropped",
    "right": "gives a x b rows, and a row of 'A' with a missing key is kept once, with empty columns for the table at this step",
    "full": "gives a x b rows, and a row with a missing key is kept once from each side, with empty columns for the other side",
    "semi": "each row whose key is found in 'A' stays once, and a row with a missing key is dropped",
    "anti": "keeps only the rows whose key is missing, because a missing key never matches",
}


def rows_claimed(keys, how, nulls_equal=False):
    """The number of rows the text of the kind says: a key value that appears n times gives n x n rows (a self-join: a = b = n)."""
    groups = Counter(k for k in keys if k is not None)
    keyed, missing = sum(n * n for n in groups.values()), keys.count(None)
    if nulls_equal:   # a missing key is a value like any other
        keyed, missing = keyed + missing * missing, 0
        return {"left": keyed, "inner": keyed, "right": keyed, "full": keyed, "semi": len(keys), "anti": 0}[how]
    return {"left": keyed + missing, "inner": keyed, "right": keyed + missing, "full": keyed + 2 * missing,
            "semi": len(keys) - missing, "anti": missing}[how]


def self_join_of(keys, how, nulls_equal=False):
    asm = DataAssembler({"A": pl.LazyFrame({"k": keys, "v": list(range(len(keys)))}, schema={"k": pl.String, "v": pl.Int64})}, recipe_id="r", join_id="J")
    step_ = {"action": JOIN, "right_ingredient": "A", "how": how, "on": ["k"], "maintain_order": "left_right", **({"nulls_equal": True} if nulls_equal else {})}
    return asm, asm.assemble([step_]).collect(), step_


@pytest.mark.parametrize("how", ["left", "inner", "right", "full", "semi", "anti"])
@pytest.mark.parametrize("name", sorted(TABLES))
def test_the_rows_of_a_real_run_are_what_the_text_of_the_kind_says(how, name):
    keys = TABLES[name]
    asm, result, step_ = self_join_of(keys, how)
    assert result.height == rows_claimed(keys, how), (how, name)
    text = join_keys.self_join_text(join_keys.self_join("A", [], step_))[0]
    assert PHRASE[how] in text


@pytest.mark.parametrize("how", ["left", "inner", "right", "full", "semi", "anti"])
def test_with_nulls_equal_a_missing_key_is_a_value_like_any_other(how):
    keys = TABLES["repeated key and 2 missing keys"]
    _, result, step_ = self_join_of(keys, how, nulls_equal=True)
    assert result.height == rows_claimed(keys, how, nulls_equal=True)
    text = join_keys.self_join_text(join_keys.self_join("A", [], step_))[0]
    assert "a missing key matches a missing key" in text or "a missing key included" in text


def test_the_inner_self_join_of_a_table_with_a_repeated_key_and_two_missing_keys_gives_6_rows():
    """The case of the review: the two rows with a missing key are dropped, the repeated key adds two (2 x 2 + 1 + 1 = 6)."""
    _, result, _ = self_join_of(TABLES["repeated key and 2 missing keys"], "inner")
    assert result.height == 6 and result["k"].null_count() == 0


def test_the_old_sentence_that_a_repeated_key_only_adds_rows_is_gone():
    for how in PHRASE:
        text = join_keys.self_join_text(join_keys.self_join("A", [], {"action": JOIN, "right_ingredient": "A", "how": how, "on": ["k"]}))[0]
        assert "the same rows if each value of the column appears once" not in text


def test_the_claim_check_can_fail():
    """A wrong claim (inner keeps the missing keys) is not what the real run gives."""
    keys = TABLES["repeated key and 2 missing keys"]
    assert self_join_of(keys, "inner")[1].height != rows_claimed(keys, "left")
