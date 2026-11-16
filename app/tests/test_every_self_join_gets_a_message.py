"""No join of the base table with itself on the same key passes without a message (D-0078, D-0050).

"Only the anti-join of a table with itself on the same key is an error; every other self-join is a warning" (Eve). Each case
below is written once and run twice: through the recipe checker (the real catalogs) and through the build (`DataAssembler`).
For each case the test states what the checker says (J15, the error; J12, the advice; or nothing, and why) and the rows
that the join gives on a real table of five rows (key s1, s2, s2, s3 and a row with an empty key).

  - J15 cases: the build refuses; the rows it WOULD give are computed by running the actions without the check, so the claim
    "no row that has a key remains" is shown, not assumed (the row with the empty key survives: it is found nowhere).
  - J12 cases: the build runs as written; the rows are the real ones.
  - not a self-join on the same key: the keys differ, so neither J15 nor J12 (a table joined with itself on other columns, for
    example a parent and a child, is a real question). This is the one kind of self-join that gets no message; see the report.

The row counts of the "warning with the row numbers" (second half of D-0078) are not built here: it needs the build to count
rows before and after a join (a task of its own).

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
from transformer.registry import get_action_function
from utils.errors import TransformationError
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
# (name, steps, what the checker says, rows the join gives)
CASES = [
    ("1 plain", [ANTI], "J15", 1),
    ("2 after a filter", [FILTER, ANTI], "J15", 1),
    ("3 after a left join of B", [join(B, "left"), ANTI], "J15", 1),
    ("4 left_on = right_on", [join(A, "anti", left_on=["sample_id"], right_on=["sample_id"])], "J15", 1),
    ("5 composite key, same order", [join(A, "anti", on=["sample_id", "group"])], "J15", 1),
    ("6 composite key, other order", [join(A, "anti", left_on=["sample_id", "group"], right_on=["group", "sample_id"])], None, 5),
    ("7 rename of another column", [{"action": "polars_rename", "mapping": {"value": "measurement"}}, ANTI], "J15", 1),
    ("8 polars_remove", [{"action": "polars_remove", "predicates": ["pl.col('value') < 2"]}, ANTI], "J15", 1),
    ("9 polars_head", [{"action": "polars_head", "n": 3}, ANTI], "J15", 0),
    ("10 with_columns on another column", [{"action": "polars_with_columns", "named_exprs": {"double": "pl.col('value') * 2"}}, ANTI], "J15", 1),
    ("11 with_columns on the key", [{"action": "polars_with_columns", "named_exprs": {"sample_id": "pl.col('sample_id').str.to_uppercase()"}}, ANTI], "J12", 5),
    ("12 anti after a full join of B", [join(B, "full"), ANTI], "J12", 2),
    ("13a left self-join", [join(A, "left")], "J12", 7),
    ("13b semi self-join", [join(A, "semi")], "J12", 4),
    ("13c inner self-join", [join(A, "inner")], "J12", 6),
    ("14 anti of B after a left join of B (a real question)", [join(B, "left"), join(B, "anti")], "J12", 3),
]
IDS = [case[0] for case in CASES]


def recipe_with(steps):
    raw = copy.deepcopy(TEMPLATE)
    raw["joins"]["main_collection"]["steps"]["tier1"] = copy.deepcopy(steps)
    return raw


def advices_and_errors(steps):
    result = check_recipe(recipe_with(steps), "run", file_stem="simple_template", catalogs=CATALOGS)
    return {p.code: p for p in result.problems if p.code in ("J12", "J15")}


def run_without_the_check(steps):
    """What the steps give when nothing refuses them: each action applied in turn on the tables."""
    frames = tables()
    lf = frames[A]
    for step in steps:
        spec = {k: v for k, v in step.items() if k != "action"}
        if "right_ingredient" in step:
            spec["__right_df__"] = frames[step["right_ingredient"]]
        lf = get_action_function(step["action"])(lf, spec)
    return lf.collect()


def build(steps):
    return DataAssembler(tables(), recipe_id="r", join_id="main_collection").assemble(copy.deepcopy(steps)).collect()


@pytest.mark.parametrize("name,steps,code,rows", CASES, ids=IDS)
def test_the_checker_says_j15_j12_or_nothing_as_stated(name, steps, code, rows):
    found = advices_and_errors(steps)
    assert sorted(found) == ([code] if code else []), (name, sorted(found))
    if code == "J15":
        assert found["J15"].severity == "E"
    if code == "J12":
        assert found["J12"].severity == "A" and found["J12"].fix.startswith("Suggestion:")


@pytest.mark.parametrize("name,steps,code,rows", CASES, ids=IDS)
def test_the_build_follows_the_same_rule_and_the_rows_are_the_stated_ones(name, steps, code, rows):
    if code == "J15":
        with pytest.raises(TransformationError, match="with itself"):
            build(steps)
        shown = run_without_the_check(steps)  # the refusal is right: this is what it would have given
        assert shown.height == rows
        assert shown["sample_id"].drop_nulls().len() == 0 or name.startswith(("9", "6"))
    else:
        assert build(steps).height == rows


def test_in_every_j15_case_only_the_row_with_the_empty_key_survives():
    """The text says 'no row that has a key': a row whose key is empty is found nowhere, so it stays."""
    for name, steps, code, _ in CASES:
        if code == "J15":
            keys = run_without_the_check(steps)["sample_id"].to_list()
            assert all(key is None for key in keys), (name, keys)


def test_the_j12_text_for_anti_is_true_for_a_table_joined_before():
    """Left join of B, then anti of B on the key: 5 rows in, the 3 whose key is not in B are kept (the old text said 'removes every row')."""
    steps = [join(B, "left"), join(B, "anti")]
    text = advices_and_errors(steps)["J12"].message
    assert "removes the rows whose key is found in 'metadata_schema'" in text and "matches itself" not in text
    assert build(steps)["sample_id"].to_list() == ["s2", "s2", None]


def test_the_j12_text_for_anti_is_true_after_a_full_join_of_the_other_table():
    steps = [join(B, "full"), ANTI]
    text = advices_and_errors(steps)["J12"].message
    assert "removes the rows whose key is found in 'primary_data'" in text
    # the row that only B has (s9) has an empty left key after a full join, so it stays with the row that had no key
    assert build(steps)["sample_id"].to_list() == [None, None]


def test_the_j15_message_has_one_period_between_what_happens_and_the_suggestions():
    problem = advices_and_errors([ANTI])["J15"]
    assert not problem.message.endswith(".") and problem.fix.endswith(".")
    text = problem.text()
    assert ".." not in text and "Fix: Suggestion" not in text and text.count("Suggestion:") == 2


def test_no_text_of_a_self_join_doubles_the_label():
    for _, steps, code, _ in CASES:
        if code:
            assert "Fix: Suggestion" not in advices_and_errors(steps)[code].text()
