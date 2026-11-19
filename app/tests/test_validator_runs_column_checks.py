"""The app's recipe check runs the checks that need the recipe graph (J08), and never accepts a recipe checked without them.

Before: `checker_problems`, `checker_advices` and `uploaded_recipe_report` called the checker without a graph, so J08 (a column
that is in both tables of a join and is not a join key: Polars renames the second one silently) was skipped in the app and ran
only in the tests of the checker. Now the validator builds the graph. A recipe the graph refuses (an unknown ingredient, a plot with
no table, a cycle) also carries an error of the checker itself, so nothing is hidden by the missing graph; and a recipe checked
without the columns is never accepted (`REQUIRED_COVERAGE`).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_validator_runs_column_checks.py -q

# @deps
# consumes: app/modules/data_analysis_recipe_validator.py (checker_problems, uploaded_recipe_report, REQUIRED_COVERAGE), libs/utils/src/utils/recipe_factory.py, libs/utils/src/utils/recipe_graph.py
# doc: .claude/knowledge/architecture_decisions.md#adr-099, .claude/knowledge/decision_ledger.md (D-0031)
# @end_deps
"""
import copy

import pytest

from app.modules import data_analysis_recipe_validator as validator
from app.modules.data_analysis_recipe_validator import REQUIRED_COVERAGE, checker_problems, uploaded_recipe_report
from utils.recipe_factory import minimal_join, minimal_plot, minimal_recipe, minimal_schema, write_recipe

JOIN_STEP = {"action": "polars_join", "right_ingredient": "B", "on": ["sample_id"], "how": "left", "maintain_order": "left_right"}


def two_tables(shared_column: bool):
    """Two tables that share `sample_id` (the join key) and, when `shared_column`, also `v` (not a key)."""
    a = minimal_schema("data/a.tsv", {"sample_id": "String", "v": "Float64"}, entity_key="sample_id")
    b_columns = {"sample_id": "String", "w": "Float64"}
    if shared_column:
        b_columns["v"] = "Float64"
    b = minimal_schema("data/b.tsv", b_columns)
    return minimal_recipe("r", schemas={"A": a, "B": b}, joins={"AB": minimal_join(["A", "B"], [JOIN_STEP])},
                          plots={"p": minimal_plot("AB", {"x": "sample_id"})})


def codes(problems):
    return [p.problem.split("]")[0].lstrip("[") for p in problems]


def test_the_app_check_reports_a_column_that_is_in_both_tables_of_a_join_and_is_not_the_key(tmp_path):
    path = write_recipe(tmp_path / "r.yaml", two_tables(shared_column=True))
    found = [p for p in checker_problems(path) if p.problem.startswith("[J08]")]
    assert found and "'v'" in found[0].problem, "J08 was skipped: the validator gives the checker no graph"


def test_a_join_whose_only_shared_column_is_the_key_has_no_j08_and_no_missing_coverage(tmp_path):
    path = write_recipe(tmp_path / "r.yaml", two_tables(shared_column=False))
    problems = checker_problems(path)
    assert "J08" not in codes(problems) and not [p for p in problems if "did not cover" in p.problem]


def test_the_upload_check_runs_the_column_checks_too():
    report = uploaded_recipe_report(two_tables(shared_column=True), "build")
    assert any(line.startswith("[J08]") for line in report)
    assert not any(line.startswith("[J08]") for line in uploaded_recipe_report(two_tables(shared_column=False), "build"))


def test_a_recipe_checked_without_the_columns_is_not_accepted(monkeypatch, tmp_path):
    assert "columns" in REQUIRED_COVERAGE
    path = write_recipe(tmp_path / "r.yaml", two_tables(shared_column=False))
    monkeypatch.setattr(validator, "_graph_of", lambda raw: None)
    missing = [p for p in checker_problems(path) if "did not cover" in p.problem]
    assert missing and "columns" in missing[0].problem


@pytest.mark.parametrize("name, change, code", [
    ("an ingredient that is no table", lambda r: r["joins"]["AB"]["ingredients"].append({"dataset_id": "NOPE"}), "J04"),
    ("a plot that reads no table", lambda r: r["analysis_groups"]["main"]["plots"]["p"].update(target_dataset="NOPE"), "PS02"),
    ("a join step that names a table the join does not list",
     lambda r: r["joins"]["AB"]["tier1"]["steps"].append({**JOIN_STEP, "right_ingredient": "ZZ"}), "J05"),
])
def test_a_recipe_the_graph_refuses_still_carries_an_error_of_the_checker_and_the_check_does_not_crash(tmp_path, name, change, code):
    raw = two_tables(shared_column=False)
    change(raw)
    assert validator._graph_of(copy.deepcopy(raw)) is None, f"{name}: the graph was expected to refuse it"
    problems = checker_problems(write_recipe(tmp_path / "r.yaml", raw))
    assert code in codes(problems), f"{name}: the checker says nothing, so the recipe would pass without the graph"


def test_a_file_that_is_not_a_recipe_gives_no_graph():
    assert validator._graph_of(None) is None and validator._graph_of(["a"]) is None
