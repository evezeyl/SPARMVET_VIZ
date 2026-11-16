"""Which column names does a step see? The behaviours of the deleted test file, written again in recipe format 1.

`app/tests/test_column_names_through_the_steps.py` (2026-11-13) answered Eve's question by running the real orchestrator:
if a column is renamed in tier 1, is the new name usable in tier 2, and are the names that exist only after a join? It was
deleted in the migration to recipe format 1 and nothing took its place (D-0031: a test is adapted to the decided design, not
dropped). Its answers, as the engine gives them today:

  - steps run in order and each sees the table the step before left: a rename in a schema's tier 1 is seen by the steps of
    the join (tier 1 and tier 2); a column that exists only after the join (it comes from the right table) is seen by the
    next steps and by tier 2; a rename after the join is seen by tier 2;
  - the one declarative rename is `original_name` on an input field (the header of the file to the slug);
  - a step that names a column the table does not have fails, with its name (nothing runs and changes nothing).

The three `xfail` cases of the old file (a `final_contract` that names a missing column, the alias `column`, a typo key)
were written for the old format: `final_contract` and the aliases no longer exist (the checker refuses them, DEC14, DEC23)
and a step with a key that the action does not declare fails (`test_actions_must_act.py`); the last two are pinned below as
plain tests because they now pass.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_column_names_through_the_steps.py -q
"""
import json
import pathlib

import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.orchestrator import DataOrchestrator

JOIN_M = {"action": "polars_join", "right_ingredient": "M", "on": ["sample_id"], "how": "left", "maintain_order": "left_right"}


def keep_above(column, value):
    return {"action": "modif_filter", "column": column, "op": "gt", "value": value, "na": "remove"}


def keep_equal(column, value):
    return {"action": "modif_filter", "column": column, "op": "eq", "value": value, "na": "remove"}


def keep_not_equal(column, value):
    return {"action": "modif_filter", "column": column, "op": "ne", "value": value, "na": "remove"}


def build(tmp_path: pathlib.Path, *, schema_t1=(), join_t1=(), join_t2=()):
    """Two schemas (S: samples with a file header 'Sample ID'; M: a year per sample), one join C; returns (T1, T2)."""
    clear_data_analysis_recipe_cache()
    data, recipes = tmp_path / "data", tmp_path / "recipes"
    data.mkdir(parents=True)
    recipes.mkdir(parents=True)
    (data / "S.tsv").write_text("Sample ID\tgroup\tscore\ns1\tA\t5\ns2\tA\t15\ns3\tB\t25\n")
    (data / "M.tsv").write_text("sample_id\tyear\ns1\t2022\ns2\t2023\ns3\t2024\n")
    lines = [
        "id: p", "data_schemas:", "  S:",
        f"    source: {{type: local_tsv, path: {data / 'S.tsv'}}}",
        "    null_values: []", "    strip: false", "    input_fields:",
        '      sample_id: {original_name: "Sample ID", type: String, is_entity_key: true}',
        "      group: {type: String}",
        "      score: {type: Int64}",
        f"    wrangling: {{tier1: {json.dumps(list(schema_t1))}}}",
        "  M:", f"    source: {{type: local_tsv, path: {data / 'M.tsv'}}}",
        "    null_values: []", "    strip: false", "    input_fields:",
        "      sample_id: {type: String, is_entity_key: true}",
        "      year: {type: String}",
        "    wrangling: {tier1: []}",
        "joins:", "  C:", "    ingredients:", "      - dataset_id: S", "      - dataset_id: M",
        f"    steps: {{tier1: {json.dumps(list(join_t1))}, tier2: {json.dumps(list(join_t2))}}}",
        "analysis_groups:", "  g:", "    label: G", "    plots:", "      p:", "        label: P", "        spec:",
        "          target_dataset: C", "          mapping: {x: group}", "          layers:",
        "            - name: geom_bar", "              params: {}",
    ]
    (recipes / "p.yaml").write_text("\n".join(lines) + "\n")
    orchestrator = DataOrchestrator(recipes, data, data_lookup="data_analysis_recipe_paths")
    keys = orchestrator.compute_data_analysis_recipe_keys("p")
    anchor = tmp_path / "t1.parquet"
    t1 = orchestrator.materialize_tier1("p", "C", anchor, keys=keys).collect()
    t2 = orchestrator.materialize_tier2("p", "C", anchor, keys=keys).collect()
    return t1, t2


RENAME = {"action": "polars_rename", "mapping": {"score": "points"}}


def test_the_file_header_is_renamed_to_the_slug_at_ingest(tmp_path):
    t1, _ = build(tmp_path, join_t1=[JOIN_M])
    assert "sample_id" in t1.columns and "Sample ID" not in t1.columns


def test_a_rename_in_a_schema_is_seen_by_the_join_steps_of_tier1_and_tier2(tmp_path):
    t1, _ = build(tmp_path, schema_t1=[RENAME], join_t1=[JOIN_M, keep_above("points", 10)])
    assert "points" in t1.columns and "score" not in t1.columns and t1.height == 2
    t1, t2 = build(tmp_path / "b", schema_t1=[RENAME], join_t1=[JOIN_M], join_t2=[keep_above("points", 10)])
    assert (t1.height, t2.height) == (3, 2)


def test_a_column_that_exists_only_after_the_join_is_seen_by_later_steps_and_tier2(tmp_path):
    t1, t2 = build(tmp_path, join_t1=[JOIN_M, keep_equal("year", "2023")], join_t2=[keep_not_equal("year", "2022")])
    assert (t1.height, t2.height) == (1, 1)


def test_a_rename_after_the_join_is_seen_by_tier2(tmp_path):
    t1, t2 = build(tmp_path, join_t1=[JOIN_M, {"action": "polars_rename", "mapping": {"year": "season"}}],
                   join_t2=[keep_not_equal("season", "2022")])
    assert "season" in t1.columns and (t1.height, t2.height) == (3, 2)


def test_the_old_name_is_gone_after_a_rename(tmp_path):
    """The other half of a rename: a step that still uses the old name fails with it, it is not read as the new one."""
    with pytest.raises(Exception, match="score"):
        build(tmp_path, schema_t1=[RENAME], join_t1=[JOIN_M, keep_above("score", 10)])


def test_a_step_that_names_a_missing_column_fails_with_its_name(tmp_path):
    with pytest.raises(Exception, match="nonexistent"):
        build(tmp_path, join_t1=[JOIN_M, keep_equal("nonexistent", "x")])


def test_a_schema_step_that_names_a_missing_column_fails_with_its_name(tmp_path):
    with pytest.raises(Exception, match="nonexistent"):
        build(tmp_path, schema_t1=[keep_equal("nonexistent", "x")], join_t1=[JOIN_M])


def test_a_step_with_the_old_alias_column_key_fails_and_does_not_pass_in_silence(tmp_path):
    """The old `column` alias of a list-of-columns parameter is not read any more (DEC14); the step is refused."""
    with pytest.raises(Exception, match="column is not a parameter of polars_drop_nulls"):
        build(tmp_path, schema_t1=[{"action": "polars_drop_nulls", "column": ["score"]}], join_t1=[JOIN_M])


def test_a_step_with_a_typo_key_fails_and_does_not_pass_in_silence(tmp_path):
    with pytest.raises(Exception, match="colums is not a parameter of polars_drop_nulls"):
        build(tmp_path, join_t1=[JOIN_M, {"action": "polars_drop_nulls", "colums": ["score"]}])
