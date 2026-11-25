"""The audit recipe of an export made in Audit mode runs on its own (D-0622, D-0535): `audit_places.audit_recipe_of`, written by the export as `audit_recipe/<id>_audited.yaml`.

Proved on the demo `1_test_data_ST22_dummy` and its real data, with audit steps at tier 1 and tier 2 of ResFinder and at tier 3 of `amr_heatmap` together:
- the recipe, written to a folder of its own and run by a FRESH orchestrator with no session and no audit machinery, gives EVERY table at tier 1 and tier 2 and EVERY plot table the
  same rows and columns as the audit copy HOME shows (a table no step changes is the original's), and the audited tables really differ from the originals;
- it passes the recipe check and the data check (the load gate's two checks) with no problem;
- its `id` equals its file name and differs from the original's (`<original id>_audited`); its `info` says in plain words that it is the audit recipe of the original, with the date;
- each audit step is visible in the recipe at its place (the end of the tier it was written at) with its reason, its id and its day in the step's own comment; the original's own steps come first;
- the recipe it was made from is not changed; with no step it is the original (with the id and the info only).

Mutation index (each seen failing): MUTATION R1 `audit_recipe_of` bakes no step (the audited tables are the originals); MUTATION R2 the step carries no comment (the reason is missing);
MUTATION R3 the id stays the original's (the id differs from the file name and from `<id>_audited`).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_recipe_runs_alone.py -q
"""
import copy

import polars as pl
import pytest
import yaml

from app.modules.audit_places import audit_recipe_of
from app.modules.cache_keys import clear_data_analysis_recipe_cache, tier2_steps
from app.modules.data_analysis_recipe_validator import validate_data_analysis_recipe, validate_data_analysis_recipe_data
from app.modules.orchestrator import DataOrchestrator
from app.tests.test_audit_view import RECIPE_ID, ROOT, World

RAW = ROOT / "assets" / "test_data"


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    yield World(tmp_path_factory.mktemp("audit_recipe_alone"))
    clear_data_analysis_recipe_cache()


def three_tiers(world):
    return [world.node(place="T1:ResFinder", value=world.ids[0], reason="resequenced"), world.node(place="T2:ResFinder", value=world.ids[1], reason="low quality"),
            world.node(place="T3:amr_heatmap", value=world.ids[2], reason="contaminated")]


def tables_and_plots(orch, recipe_id, raw, anchors):
    """Every table at tier 1 and tier 2 and every plot table, as the engine builds them from the recipe alone: {(name, tier): frame}."""
    found = {}
    for table in sorted(_collections(raw)):
        found[(table, "T1")] = orch.materialize_tier1(recipe_id, table, anchors / f"{table}.parquet").collect()
        found[(table, "T2")] = orch.materialize_tier2(recipe_id, table, anchors / f"{table}.parquet").collect() if tier2_steps(raw, table) else found[(table, "T1")]
    for plot in sorted(_plots(raw)):
        found[(plot, "T3")] = orch.materialize_tier3(recipe_id, plot, anchors).collect()
    return found


def _collections(raw):
    from utils.recipe_graph import build_graph
    return build_graph(raw).collections()


def _plots(raw):
    from utils.recipe_graph import build_graph
    return build_graph(raw).plots()


def home_audited(world, nodes):
    """What HOME shows in Audit mode for every table and plot: the audit copy's table when a step changes it, else the original's."""
    originals = tables_and_plots(world.orch, RECIPE_ID, world.loaded.raw, world.anchors)
    audit = world.audit()
    shown = {}
    for (name, tier), frame in originals.items():
        if tier == "T3":
            lazy = audit.plot_lazy(RECIPE_ID, name, nodes, world.plans)
        else:
            lazy = audit.table_lazy(RECIPE_ID, name, tier, nodes, world.plans)
            if lazy is None and tier == "T2" and not tier2_steps(world.loaded.raw, name):
                lazy = audit.table_lazy(RECIPE_ID, name, "T1", nodes, world.plans)
        shown[(name, tier)] = frame if lazy is None else lazy.collect()
    return originals, shown


def test_the_audit_recipe_run_alone_gives_every_audited_table_and_plot_table(world, tmp_path):
    nodes = three_tiers(world)
    originals, shown = home_audited(world, nodes)
    folder = tmp_path / "audit_recipe"
    folder.mkdir()
    recipe = audit_recipe_of(world.loaded.raw, nodes, RECIPE_ID, "2026-11-24")
    (folder / f"{recipe['id']}.yaml").write_text(yaml.safe_dump(recipe, sort_keys=False, allow_unicode=True), encoding="utf-8")
    clear_data_analysis_recipe_cache()
    alone = tables_and_plots(DataOrchestrator(folder, RAW), recipe["id"], recipe, tmp_path / "alone")
    assert alone.keys() == shown.keys() and len(alone) > 40, len(alone)
    for key, frame in shown.items():
        assert alone[key].columns == frame.columns and alone[key].equals(frame), key
    changed = [key for key in shown if not shown[key].equals(originals[key])]
    assert {("ResFinder", "T1"), ("ResFinder", "T2"), ("amr_heatmap", "T3")} <= set(changed) and len(changed) < len(shown), "the steps change what they reach and no more"
    clear_data_analysis_recipe_cache()


def test_the_audit_recipe_passes_the_recipe_check_and_the_data_check_and_its_id_is_its_file_name(world, tmp_path):
    recipe = audit_recipe_of(world.loaded.raw, three_tiers(world), RECIPE_ID, "2026-11-24")
    path = tmp_path / f"{recipe['id']}.yaml"
    path.write_text(yaml.safe_dump(recipe, sort_keys=False, allow_unicode=True), encoding="utf-8")
    assert recipe["id"] == f"{RECIPE_ID}_audited" and recipe["id"] == path.stem and recipe["id"] != RECIPE_ID
    assert validate_data_analysis_recipe(path) == []
    assert validate_data_analysis_recipe_data(path, RAW) == []
    clear_data_analysis_recipe_cache()


def test_the_info_says_it_is_the_audit_recipe_of_the_original_with_the_date(world):
    recipe = audit_recipe_of(world.loaded.raw, three_tiers(world), RECIPE_ID, "2026-11-24")
    text = recipe["info"]["description"]
    assert f"audit recipe of '{RECIPE_ID}'" in text and "2026-11-24" in text and "reason" in text
    assert recipe["info"]["ui_label"] == f"{world.loaded.raw['info']['ui_label']} (audited)"
    assert recipe["info"]["description"].endswith(world.loaded.raw["info"]["description"]), "the original's description is kept after it"


def test_each_audit_step_is_visible_at_its_place_with_its_reason_and_the_original_steps_come_first(world):
    nodes = three_tiers(world)
    before = copy.deepcopy(world.loaded.raw)
    recipe = audit_recipe_of(world.loaded.raw, nodes, RECIPE_ID, "2026-11-24")
    assert world.loaded.raw == before, "the recipe it was made from is not changed"
    table = recipe["data_schemas"]["ResFinder"]
    original = before["data_schemas"]["ResFinder"]
    t1_last, t2_last = table["tier1"]["steps"][-1], table["tier2"]["steps"][-1]
    assert table["tier1"]["steps"][:-1] == original["tier1"]["steps"] and table["tier2"]["steps"][:-1] == original["tier2"]["steps"]
    plot = next(e for g in recipe["analysis_groups"].values() for p, e in g["plots"].items() if p == "amr_heatmap")
    t3_last = plot["tier3"]["steps"][-1]
    for step, node, words in ((t1_last, nodes[0], "resequenced"), (t2_last, nodes[1], "low quality"), (t3_last, nodes[2], "contaminated")):
        assert node["id"] in step["comment"] and words in step["comment"], step
        assert step["action"] == "modif_filter"
    assert plot["tier3"]["steps"][0]["action"] == "polars_fill_null", "the recipe's own tier-3 step of the plot comes first"


def test_with_no_audit_step_the_audit_recipe_is_the_original_with_only_the_id_and_the_info_changed(world):
    recipe = audit_recipe_of(world.loaded.raw, [], RECIPE_ID, "2026-11-24")
    rest = {k: v for k, v in recipe.items() if k not in ("id", "info")}
    assert rest == {k: v for k, v in world.loaded.raw.items() if k not in ("id", "info", "plots")}
