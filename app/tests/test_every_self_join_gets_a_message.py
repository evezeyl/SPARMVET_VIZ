"""Every self-join builds and gets a message, and none is refused (D-0183, D-0050, D-0099).

Eve 2026-11-16 (replacing D-0078): "No error in Polars, then no error for us; a warning / caution is good." and "A self-join
(a table joined with itself, the anti-join on the same key included) gives a warning, never an error." Polars reports nothing
for it, and an anti-join of a table with itself is not always empty: it returns the rows whose key is missing, because Polars
never matches a missing key.

Each case below is written once and run twice, on a real table of five rows (key s1, s2, s2, s3 and a row with an empty key):
  - through the recipe checker with the real catalogs: exactly one advice J12 (severity A, a "Suggestion:" remedy), and no
    error of any kind for the join (there is no code J15 any more);
  - through the build (`DataAssembler`): it builds and gives the rows Polars gives, and a caution (a `PipelineError` of
    severity "warning") with the real numbers: rows before the join, rows after it, rows with a missing key in the key
    columns (left table, right table). The text of the caution starts with the text of the advice: one function writes both.
A join with a table that is not already held (a normal join) gets nothing from either.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_every_self_join_gets_a_message.py -q
"""
import copy
from pathlib import Path

import polars as pl
import pytest
import yaml

import transformer.actions  # noqa: F401  (loads the registry)
from app.modules.data_analysis_recipe_validator import checker_catalogs
from transformer.data_assembler import DataAssembler
from utils.recipe_check import check_recipe

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = yaml.safe_load((ROOT / "config/data_analysis_recipes/templates/simple_template.yaml").read_text())
CATALOGS = checker_catalogs()
A, B = "primary_data", "metadata_schema"


def tables():
    base = pl.LazyFrame({"sample_id": ["s1", "s2", "s2", "s3", None], "value": [1.0, 2.0, 3.0, 4.0, 5.0], "group": ["x", "x", "y", "y", "z"]})
    other = pl.LazyFrame({"sample_id": ["s1", "s3", "s9"], "category": ["c1", "c3", "c9"]})
    return {A: base, B: other}


def join(right, how, **keys):
    return {"action": "polars_join", "right_ingredient": right, "how": how, "maintain_order": "left_right", **({"on": ["sample_id"]} if not keys else keys)}


ANTI = join(A, "anti")
FILTER = {"action": "modif_filter", "column": "value", "op": "gt", "value": 1.0, "na": "remove"}
# (name, steps, rows before the join, rows after it, rows with a missing key: left table, right table)
CASES = [
    ("1 plain anti", [ANTI], 5, 1, 1, 1),
    ("2 after a filter", [FILTER, ANTI], 4, 1, 1, 1),
    ("3 after a left join of B", [join(B, "left"), ANTI], 5, 1, 1, 1),
    ("4 left_on = right_on", [join(A, "anti", left_on=["sample_id"], right_on=["sample_id"])], 5, 1, 1, 1),
    ("5 composite key, same order", [join(A, "anti", on=["sample_id", "group"])], 5, 1, 1, 1),
    ("6 composite key, other order", [join(A, "anti", left_on=["sample_id", "group"], right_on=["group", "sample_id"])], 5, 5, 1, 1),
    ("7 rename of another column", [{"action": "polars_rename", "mapping": {"value": "measurement"}}, ANTI], 5, 1, 1, 1),
    ("8 polars_remove", [{"action": "polars_remove", "predicates": ["pl.col('value') < 2"]}, ANTI], 4, 1, 1, 1),
    ("9 polars_head", [{"action": "polars_head", "n": 3}, ANTI], 3, 0, 0, 1),
    ("10 with_columns on another column", [{"action": "polars_with_columns", "named_exprs": {"double": "pl.col('value') * 2"}}, ANTI], 5, 1, 1, 1),
    ("11 with_columns on the key", [{"action": "polars_with_columns", "named_exprs": {"sample_id": "pl.col('sample_id').str.to_uppercase()"}}, ANTI], 5, 5, 1, 1),
    ("12 anti after a full join of B", [join(B, "full"), ANTI], 6, 2, 2, 1),
    ("13a left self-join", [join(A, "left")], 5, 7, 1, 1),
    ("13b semi self-join", [join(A, "semi")], 5, 4, 1, 1),
    ("13c inner self-join", [join(A, "inner")], 5, 6, 1, 1),
    ("14 anti of B after a left join of B", [join(B, "left"), join(B, "anti")], 5, 3, 1, 0),
    ("15 other key columns (group against sample_id)", [join(A, "left", left_on=["group"], right_on=["sample_id"])], 5, 5, 0, 1),
]
IDS = [case[0] for case in CASES]


def recipe_with(steps):
    raw = copy.deepcopy(TEMPLATE)
    raw["joins"]["main_collection"]["tier1"]["steps"] = copy.deepcopy(steps)
    return raw


def checked(steps):
    return check_recipe(recipe_with(steps), "run", file_stem="simple_template", catalogs=CATALOGS)


def build(steps, frames=None):
    assembler = DataAssembler(frames or tables(), recipe_id="r", join_id="main_collection")
    return assembler, assembler.assemble(copy.deepcopy(steps)).collect()


@pytest.mark.parametrize("name,steps,before,after,missing_left,missing_right", CASES, ids=IDS)
def test_the_checker_gives_one_advice_and_no_error(name, steps, before, after, missing_left, missing_right):
    result = checked(steps)
    found = [p for p in result.problems if p.code == "J12"]
    assert len(found) == 1, (name, [p.code for p in result.problems])
    assert found[0].severity == "A" and found[0].fix.startswith("Suggestion:") and "Fix: Suggestion" not in found[0].text()
    assert not [p for p in result.problems if p.code == "J15" or (p.code.startswith("J") and p.severity == "E")], name
    assert result.ok, [p.text() for p in result.errors]


@pytest.mark.parametrize("name,steps,before,after,missing_left,missing_right", CASES, ids=IDS)
def test_the_build_runs_the_join_as_written_and_cautions_with_the_numbers(name, steps, before, after, missing_left, missing_right):
    assembler, result = build(steps)              # nothing is refused
    assert len(assembler.cautions) == 1, name
    caution = assembler.cautions[0]
    assert caution.severity == "warning" and result.height == after
    found = caution.evidence
    assert (found["row_count_before"], found["row_count_after"], found["rows_with_missing_key_left"], found["rows_with_missing_key_right"]) \
        == (before, after, missing_left, missing_right), name
    assert f"Rows before the join: {before}; rows after: {after}" in caution.problem
    assert caution.fix.startswith("Suggestion:")


@pytest.mark.parametrize("name,steps,before,after,missing_left,missing_right", CASES, ids=IDS)
def test_the_caution_starts_with_the_text_of_the_advice(name, steps, before, after, missing_left, missing_right):
    advice = next(p for p in checked(steps).problems if p.code == "J12")
    caution = build(steps)[0].cautions[0]
    assert caution.problem.startswith(advice.message) and caution.fix == advice.fix


def test_the_anti_self_join_gives_the_rows_with_a_missing_key_because_polars_never_matches_a_missing_key():
    _, result = build([ANTI])
    assert result["sample_id"].to_list() == [None] and result["value"].to_list() == [5.0]


def test_two_rows_with_a_missing_key_show_the_count():
    frames = {A: pl.LazyFrame({"sample_id": ["s1", None, "s2", None], "value": [1, 2, 3, 4]})}
    assembler, result = build([ANTI], frames)
    assert result.height == 2
    found = assembler.cautions[0].evidence
    assert found["rows_with_missing_key_left"] == 2 and found["rows_with_missing_key_right"] == 2
    assert "rows with a missing key in ['sample_id']: 2 in the table at this step and 2 in 'primary_data'" in assembler.cautions[0].problem


def test_the_same_table_without_a_missing_key_gives_an_empty_result_and_the_numbers_say_so():
    frames = {A: pl.LazyFrame({"sample_id": ["s1", "s2"], "value": [1, 2]})}
    assembler, result = build([ANTI], frames)
    assert result.height == 0
    found = assembler.cautions[0].evidence
    assert (found["row_count_before"], found["row_count_after"], found["rows_with_missing_key_left"]) == (2, 0, 0)
    assert "If no row has a missing key, the result is empty" in next(p for p in checked([ANTI]).problems if p.code == "J12").message


def test_the_anti_text_is_the_true_sentence_and_not_the_one_of_the_old_error():
    message = next(p for p in checked([ANTI]).problems if p.code == "J12").message
    assert "keeps only the rows whose key is missing" in message and "a missing key never matches" in message
    assert "no row that has a key" not in message


def test_the_as_of_join_and_the_join_on_conditions_get_their_advice():
    asof = {"action": "polars_join_asof", "right_ingredient": A, "on": "value", "strategy": "backward"}
    where = {"action": "modif_join_where", "right_ingredient": A, "predicates": ["pl.col('value') < pl.col('value_right')"]}
    for step, label in ((asof, "as-of join"), (where, "join on conditions")):
        found = [p for p in checked([step]).problems if p.code == "J12"]
        assert len(found) == 1 and found[0].severity == "A" and label in found[0].message


def test_a_join_with_a_table_that_is_not_held_gets_no_message_and_no_caution():
    steps = [join(B, "left")]
    assert [p for p in checked(steps).problems if p.code == "J12"] == []
    assembler, result = build(steps)
    assert assembler.cautions == [] and result.height == 5


def test_no_case_raises_at_the_check_or_the_build():
    for _, steps, *_ in CASES:
        checked(steps)
        build(steps)
