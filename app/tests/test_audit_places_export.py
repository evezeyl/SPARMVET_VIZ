"""What the export says and writes of audit steps written at a table (HOME audit, demo step 4): `audit_places.place_step_records`, `bake_place_steps`.

Proved on the demo `1_test_data_ST22_dummy` (the engine builds the tables):
- the record of a step names its place in words, the plot it was started from, the reason and the plots built from the place (the graph's, not a guess);
- the recipe baked for the reproducibility part holds the step as a plain step at the END of that tier of the table, says so in the table's comment, and changes nothing else
  (the argument is not changed); a recipe written from it, run by the engine with no audit machinery, builds for the plot the SAME table as the audit copy (the table of HOME's
  audited plot, the table of the exported data file);
- two steps at two tables are both baked, in order; a step at a table the recipe does not have is refused (KeyError) and nothing is written;
- an empty list bakes a copy equal to the recipe.

Mutation index (each seen failing): MUTATION X1 `bake_place_steps` puts the step at the START of the list (the order of the author's steps and the audit's is lost: the rebuilt
table differs); MUTATION X2 `place_step_records` lists no plot.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_places_export.py -q
"""
from pathlib import Path

import polars as pl
import pytest
import yaml

from app.modules.audit_places import bake_place_steps, place_step_records, place_words
from app.modules.audit_view import PlaceAudit
from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe
from app.modules.orchestrator import DataOrchestrator
from app.modules.plan_composer import compose_plan_book
from app.modules.session_manager import make_audit_step
from utils.recipe_graph import build_graph

ROOT = Path(__file__).resolve().parents[2]
RECIPE_ID = "1_test_data_ST22_dummy"
PIPELINES = ROOT / "config" / "data_analysis_recipes" / "pipelines"


def node(place="T1:ResFinder", column="identity", op="lt", value=99, reason="keep the hits below 99 for this check"):
    return make_audit_step("filter_row", {"column": column, "op": op, "value": value, "na": "remove"}, reason=reason,
                           place=place, started_from="subtab_amr_heatmap")


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    clear_data_analysis_recipe_cache()
    orch = DataOrchestrator(PIPELINES, ROOT / "assets" / "test_data")
    loaded = load_data_analysis_recipe(PIPELINES / f"{RECIPE_ID}.yaml")
    graph = build_graph(loaded.raw)
    yield {"orch": orch, "loaded": loaded, "graph": graph, "plans": compose_plan_book(orch, RECIPE_ID, loaded, graph), "root": tmp_path_factory.mktemp("export")}
    clear_data_analysis_recipe_cache()


def test_the_record_of_a_step_names_the_place_the_reason_and_the_plots_built_from_it(world):
    n = node()
    (record,) = place_step_records(world["graph"], [n])
    assert record["place"] == "T1:ResFinder" and record["place_words"] == "Table ResFinder (tier 1)" == place_words("T1:ResFinder")
    assert record["started_from"] == "amr_heatmap" and record["reason"].startswith("keep the hits") and record["action"] == "filter_row"
    assert record["params"]["column"] == "identity" and record["id"] == n["id"]
    assert record["plots"] == [p for p in world["graph"].plots() if f"T3:{p}" in world["graph"].below("T1:ResFinder")]
    assert "amr_heatmap" in record["plots"] and "mlst_bar" not in record["plots"]
    assert place_step_records(world["graph"], []) == []


def test_a_baked_recipe_holds_the_step_at_the_end_of_the_tier_and_changes_nothing_else(world):
    raw = world["loaded"].raw
    before = yaml.safe_dump(raw, sort_keys=False)
    baked = bake_place_steps(raw, [node(), node(place="T2:ResFinder", column="overlap", value=50)])
    assert yaml.safe_dump(raw, sort_keys=False) == before, "the argument is not changed"
    table = baked["data_schemas"]["ResFinder"]
    assert table["tier1"]["steps"][-1]["action"] == "modif_filter" and table["tier1"]["steps"][-1]["column"] == "identity"
    assert table["tier1"]["steps"][:-1] == raw["data_schemas"]["ResFinder"]["tier1"]["steps"], "the author's steps come first, unchanged"
    assert table["tier2"]["steps"][-1]["column"] == "overlap" and table["tier2"]["steps"][:-1] == raw["data_schemas"]["ResFinder"]["tier2"]["steps"]
    assert "audit steps" in table["comment"] and table["comment"].count("Written by the export") == 2
    untouched = {k: v for k, v in baked["data_schemas"].items() if k != "ResFinder"}
    assert untouched == {k: v for k, v in raw["data_schemas"].items() if k != "ResFinder"}
    assert bake_place_steps(raw, []) == {k: v for k, v in raw.items() if k != "plots"}, "an empty list bakes a copy equal to the recipe, without the loader's mirror `plots`"
    assert "plots" not in bake_place_steps(raw, [node()]), "a written recipe never carries the loader's mirror of analysis_groups (a root `plots:` does not load again)"


def test_a_step_at_a_table_the_recipe_does_not_have_is_refused(world):
    with pytest.raises(KeyError):
        bake_place_steps(world["loaded"].raw, [node(place="T1:no_such_table")])


def test_the_recipe_built_from_the_baked_one_gives_the_plot_the_table_of_the_audit_copy(world, tmp_path):
    """The reproducibility part: the baked recipe, run by the engine as any recipe, builds what HOME's audited plot and the exported data file hold."""
    nodes = [node()]
    clear_data_analysis_recipe_cache()
    anchors = tmp_path / "anchors"
    audited = PlaceAudit(world["orch"], anchors, tmp_path / "audit").plot_lazy(RECIPE_ID, "amr_heatmap", nodes, world["plans"]).collect()
    baked = bake_place_steps(world["loaded"].raw, nodes)
    folder = tmp_path / "pipelines"
    folder.mkdir()
    (folder / f"{RECIPE_ID}.yaml").write_text(yaml.safe_dump(baked, sort_keys=False, allow_unicode=True), encoding="utf-8")
    clear_data_analysis_recipe_cache()
    rebuilt = DataOrchestrator(folder, ROOT / "assets" / "test_data").materialize_tier3(RECIPE_ID, "amr_heatmap", tmp_path / "rebuilt").collect()
    assert audited.height < 74 and rebuilt.equals(audited), "the recipe alone builds the audited table"
    clear_data_analysis_recipe_cache()


# ------------------------------------------------------------------ the session keeps a step written at a table
def test_a_saved_and_restored_session_keeps_the_step_with_its_place_and_the_format_number_is_the_current_one(tmp_path):
    from app.modules.session_manager import SESSION_FORMAT_VERSION, SessionManager, split_key_drops
    assert SESSION_FORMAT_VERSION == 6, "the stored form changed (FLOW-3: the steps are ONE flat list `audit_pipeline`, each with its place T1, T2 or T3, no `plot_scope`): an older file is refused, never converted"
    sm = SessionManager(tmp_path)
    key = "aaaaaaaaaaaa:bbbbbbbbbbbb"
    step = node()
    sm.write_t3_ghost(key, RECIPE_ID, "a" * 64, "b" * 64, audit_steps=[step])
    saves, skipped = sm.scan_t3_ghosts(key)
    assert skipped == [] and saves[0]["schema_version"] == SESSION_FORMAT_VERSION
    back = saves[0]["audit_pipeline"]
    assert back == [step] and back[0]["place"] == "T1:ResFinder" and back[0]["started_from"] == "subtab_amr_heatmap" and back[0]["reason"]


@pytest.mark.parametrize("old_number", [3, 4, 5])
def test_a_file_of_the_older_format_is_refused_not_converted(tmp_path, old_number):
    """3: before the steps written at a table; 4: before the steps written at a plot's tier 3 went into the same list (format 5); 5: before the one flat list `audit_pipeline` (format 6, FLOW-3)."""
    import json
    from app.modules.session_manager import LegacySessionError, SessionManager
    sm = SessionManager(tmp_path)
    key = "aaaaaaaaaaaa:bbbbbbbbbbbb"
    sm.session_dir(key).mkdir(parents=True, exist_ok=True)
    (sm.session_dir(key) / "t3_20261101T000000.json").write_text(json.dumps({"session_key": key, "saved_at": "2026-11-01T00:00:00", "schema_version": old_number,
                                                                          "audit_pipeline": [], "t3_plot_overrides": {}}))
    with pytest.raises(LegacySessionError, match="older version of the app and cannot be opened"):
        sm.scan_t3_ghosts(key)


def test_restore_judges_a_stored_key_drop_at_its_own_place_and_keeps_the_filter(world):
    from app.modules.session_manager import split_key_drops
    keep = node()
    drop_key = make_audit_step("drop_column", {"column": "sample_id"}, reason="no", place="T1:ResFinder", started_from="subtab_amr_heatmap")
    kept, refused = split_key_drops([keep, drop_key], world["loaded"].raw, world["plans"])
    assert kept == [keep], "the filter is restored"
    assert [r["id"] for r in refused] == [drop_key["id"]] and "sample_id" in refused[0]["problem"]
