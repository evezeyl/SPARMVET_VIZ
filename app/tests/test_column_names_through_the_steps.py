"""Which column names does a step see? (P0, 2026-11-13; the ground of the recipe graph, `utils.recipe_graph`, package P3)

Eve's question: if I rename a column in tier 1, can I use the new name in tier 2? And names that exist only after
a join? Answered by running the real orchestrator on small recipes (scratch: `tmpAI/architect/rename_names_probe.py`):

  - Steps run in order and each sees the table the step before left: a rename in a schema's tier 1 is seen by the
    join steps (tier 1 and tier 2); a column that exists only after a join (it comes from the right table) is seen by
    the next steps, by tier 2 and by `final_contract`; a rename after the join is seen by tier 2. No alias is needed.
  - The one declarative rename is `original_name` on an input field (the header of the file to the slug).

Gaps written as `xfail(strict=True)` (they fail today; the fix commit removes the mark):
  - a `final_contract` that names a column the table does not have is dropped with a console line, no error
    (`orchestrator.py:65`): "declared but not applied" must fail;
  - a step with no usable column key (a typo, `colums`) runs and changes nothing, in a schema's wrangling and in a
    join's steps; and a join step with the alias `column` also changes nothing (the schema path resolves the aliases
    `column`, `source`, `source_column`, `target_column`, `data_wrangler.py:132-137`; the join path
    `data_assembler.py` does not). The aliases go (recipe spec decision 25, #78); both paths must then fail.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_column_names_through_the_steps.py -q
"""
import json
import pathlib

import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.orchestrator import DataOrchestrator

JOIN_M = {"action": "join", "right_ingredient": "M", "on": "sample_id", "how": "left"}


def build(tmp_path: pathlib.Path, *, schema_t1=(), join_t1=(), join_t2=(), contract=None):
    """Two schemas (S: samples with a file header 'Sample ID'; M: a year per sample), one join C; returns (T1, T2)."""
    clear_data_analysis_recipe_cache()
    data, recipes = tmp_path / "data", tmp_path / "recipes"
    data.mkdir(parents=True); recipes.mkdir(parents=True)
    (data / "S.tsv").write_text("Sample ID\tgroup\tscore\ns1\tA\t5\ns2\tA\t15\ns3\tB\t25\n")
    (data / "M.tsv").write_text("sample_id\tyear\ns1\t2022\ns2\t2023\ns3\t2024\n")
    lines = [
        "id: p", "info: {display_name: P}", "data_schemas:", "  S:",
        f"    source: {{type: local_tsv, path: {data / 'S.tsv'}}}",
        "    input_fields:",
        '      sample_id: {original_name: "Sample ID", type: categorical, label: Sample, is_primary_key: true}',
        "      group: {original_name: group, type: categorical, label: Group}",
        "      score: {original_name: score, type: numeric, label: Score}",
        f"    wrangling: {{tier1: {json.dumps(list(schema_t1))}, tier2: []}}",
        "  M:", f"    source: {{type: local_tsv, path: {data / 'M.tsv'}}}",
        "    input_fields:",
        "      sample_id: {original_name: sample_id, type: categorical, label: Sample, is_primary_key: true}",
        "      year: {original_name: year, type: categorical, label: Year}",
        "    wrangling: {tier1: [], tier2: []}",
        "joins:", "  C:", "    ingredients:", "      - dataset_id: S", "      - dataset_id: M",
        f"    steps: {{tier1: {json.dumps(list(join_t1))}, tier2: {json.dumps(list(join_t2))}}}",
    ]
    if contract:
        lines.append("    final_contract: " + json.dumps(contract))
    lines += ["analysis_groups:", "  g:", "    label: G", "    plots:", "      p:", "        label: P", "        spec:",
              "          target_dataset: C", "          mapping: {x: group}", "          layers:",
              "            - name: geom_bar", "              params: {}"]
    (recipes / "p.yaml").write_text("\n".join(lines) + "\n")
    orch = DataOrchestrator(recipes, data, data_lookup="data_analysis_recipe_paths")
    keys = orch.compute_data_analysis_recipe_keys("p")
    anchor = tmp_path / "t1.parquet"
    t1 = orch.materialize_tier1("p", "C", anchor, keys=keys).collect()
    t2 = orch.materialize_tier2("p", "C", anchor, keys=keys).collect()
    return t1, t2


RENAME = {"action": "rename", "mapping": {"score": "points"}}


def test_the_file_header_is_renamed_to_the_slug_at_ingest(tmp_path):
    t1, _ = build(tmp_path, join_t1=[JOIN_M])
    assert "sample_id" in t1.columns and "Sample ID" not in t1.columns


def test_a_rename_in_a_schema_is_seen_by_the_join_steps_of_tier1_and_tier2(tmp_path):
    t1, t2 = build(tmp_path, schema_t1=[RENAME], join_t1=[JOIN_M, {"action": "filter_gt", "columns": ["points"], "value": 10}])
    assert "points" in t1.columns and "score" not in t1.columns and t1.height == 2
    t1, t2 = build(tmp_path / "b", schema_t1=[RENAME], join_t1=[JOIN_M],
                   join_t2=[{"action": "filter_gt", "columns": ["points"], "value": 10}])
    assert (t1.height, t2.height) == (3, 2)


def test_a_column_that_exists_only_after_the_join_is_seen_by_later_steps_tier2_and_the_contract(tmp_path):
    t1, t2 = build(tmp_path, join_t1=[JOIN_M, {"action": "filter_eq", "columns": ["year"], "value": "2023"}],
                   join_t2=[{"action": "filter_ne", "columns": ["year"], "value": "2022"}])
    assert (t1.height, t2.height) == (1, 1)
    t1, _ = build(tmp_path / "c", join_t1=[JOIN_M], contract={"sample_id": "categorical", "year": "categorical"})
    assert t1.columns == ["sample_id", "year"]


def test_a_rename_after_the_join_is_seen_by_tier2(tmp_path):
    t1, t2 = build(tmp_path, join_t1=[JOIN_M, {"action": "rename", "mapping": {"year": "season"}}],
                   join_t2=[{"action": "filter_ne", "columns": ["season"], "value": "2022"}])
    assert "season" in t1.columns and (t1.height, t2.height) == (3, 2)


def test_a_schema_step_that_names_a_missing_column_fails_with_its_name(tmp_path):
    with pytest.raises(Exception, match="nonexistent"):
        build(tmp_path, join_t1=[JOIN_M, {"action": "filter_eq", "columns": ["nonexistent"], "value": "x"}])


def test_the_schema_path_resolves_the_alias_column_today(tmp_path):
    """Pins today's behaviour: DataWrangler maps `column` (and source, source_column, target_column) to `columns`.
    This test goes with the alias removal (#78): then `column` must FAIL (see the xfail below), and this one is deleted."""
    t1, _ = build(tmp_path, schema_t1=[{"action": "filter_gt", "column": "score", "value": 10}], join_t1=[JOIN_M])
    assert t1.height == 2


@pytest.mark.xfail(strict=True, reason="declared but not applied: final_contract names a column the table lacks, "
                                       "orchestrator.py:65 only prints and drops it (recipe session: check X-series and the engine)")
def test_a_final_contract_naming_a_column_the_table_lacks_fails(tmp_path):
    with pytest.raises(Exception):
        build(tmp_path, schema_t1=[RENAME], join_t1=[JOIN_M], contract={"sample_id": "categorical", "score": "numeric"})


@pytest.mark.xfail(strict=True, reason="declared but not applied: a join step with the alias `column` runs and changes nothing "
                                       "(the join path does not resolve aliases); see ACTION-MUST-ACT-1")
def test_a_join_step_with_the_alias_column_does_not_pass_silently(tmp_path):
    t1, _ = build(tmp_path, join_t1=[JOIN_M, {"action": "filter_gt", "column": "score", "value": 10}])
    assert t1.height == 2   # the filter acted, or build() raised: today it returns 3 rows


@pytest.mark.xfail(strict=True, reason="declared but not applied: a step without a usable column key runs and changes nothing "
                                       "in a schema's wrangling; see ACTION-MUST-ACT-1")
def test_a_schema_step_with_a_typo_key_fails(tmp_path):
    with pytest.raises(Exception):
        build(tmp_path, schema_t1=[{"action": "filter_gt", "colums": ["score"], "value": 10}], join_t1=[JOIN_M])


@pytest.mark.xfail(strict=True, reason="declared but not applied: a step without a usable column key runs and changes nothing "
                                       "in a join's steps; see ACTION-MUST-ACT-1")
def test_a_join_step_with_a_typo_key_fails(tmp_path):
    with pytest.raises(Exception):
        build(tmp_path, join_t1=[JOIN_M, {"action": "filter_gt", "colums": ["score"], "value": 10}])
