"""The run of an audit copy without a screen (piece A5 of slice A of the HOME audit redesign): `app/modules/audit_run.py`.

The copy is handed to the SAME engine functions as the original (`DataOrchestrator.materialize_tier1`, `materialize_tier2`, `materialize_tier3`, through
their `loaded` argument). "Nothing is ever copied: a stage is either reused or recomputed": a table whose key equals the original's is read from the
original's stored table, a table whose key differs is built into the audit's own folder, and a plot is affected when the CONTENT of its table differs
(ADR-101 point 6).

What is proved:
- a copy with no audit step reuses everything and builds nothing, on a staged recipe and on every shipped recipe that has its test data; the tables of the
  copy have the golden records of the baseline;
- on a staged recipe (two source tables A and B, a join J with a tier 2, a third unrelated table X with a tier 2, plots on J, on X and on A, the last with a
  tier 3 of its own), a `modif_filter` or a `polars_drop` at tier 1, tier 2 and tier 3: only the tables and plots after the step change, the others are reused
  (asserted by the result AND by which files appear in the audit folder), and the stored tables of the original are byte-identical before and after;
- a filter that removes nothing moves a key and no row: its plots are not affected; a step that changes the table affects its plots and no other;
- removing the step gives the original back: the audit folder is emptied, the result is all reused;
- a second run of the same copy builds nothing; a step that cannot be applied is refused naming its id and its place (never skipped), also when the list
  holds several audit steps; a copy that is not the original plus audit steps does not run; the two folders must differ;
- the orchestrator takes a recipe that is not its file only when it is handed one: existing callers read the file as before.

Mutation index (each seen failing, see the report): MUTATION R1 the run always reads the original's table (it never builds); MUTATION K1 (in
`test_audit_keys.py`) the audit part is left out of the keys; MUTATION C1 (in `libs/utils/tests/test_audit_copy.py`) `strip_marked` leaves a step.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_run.py -q
"""
import copy
import hashlib
import json
from pathlib import Path

import polars as pl
import pytest

from app.modules.audit_run import (
    BUILT, FROM_AUDIT_STORE, FROM_ORIGINAL, NONE, AuditRun, AuditRunError, run_audit)
from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe, loaded_from_resolved
from app.modules.orchestrator import TIER1_KEY_META, DataOrchestrator
from app.tests.test_table_keys import FILTER_A, ROOT, Staged, recipe, stores_during
from transformer.anchor import read_anchor_if_key
from utils.audit_copy import add_step, audit_recipe_of, remove_step

ID1, ID2, ID3 = "audit_1a2b3c4d_1", "audit_1a2b3c4d_2", "audit_00ff00ff_3"
KEEP_S1 = {"action": "modif_filter", "column": "sample_id", "op": "eq", "value": "s1", "na": "remove"}
KEEP_S2 = {"action": "modif_filter", "column": "sample_id", "op": "eq", "value": "s2", "na": "remove"}
NOTHING_REMOVED = {"action": "modif_filter", "column": "sample_id", "op": "ne", "value": "never", "na": "keep"}
DROP_GROUP_B = {"action": "polars_drop", "columns": ["group_b"]}
DROP_GROUP = {"action": "polars_drop", "columns": ["group"]}
BAD = {"action": "modif_filter", "column": "no_such_column", "op": "eq", "value": "x", "na": "remove"}


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


class World(Staged):
    """The staged recipe of `test_table_keys.py` (A and B, the join J = A + B with a tier 2, X plotted directly with a tier 2, plots pj on J and px on
    X) and a third plot pa on A that has a tier 3 of its own. The original's stored tables are in `anchors`, the audit's in `audit`."""

    def __init__(self, root: Path):
        self.audit = root / "audit"
        super().__init__(root)

    def write_recipe(self, **changes) -> None:
        changes = {"analysis_groups/g/plots/pa": {"target_dataset": "A", "mapping": {"x": "group"}, "layers": [{"name": "geom_bar", "params": {}}],
                                                  "tier3": {"steps": [DROP_GROUP]}}, **changes}
        super().write_recipe(**changes)

    def original_raw(self) -> dict:
        return load_data_analysis_recipe(self.recipes / "staged.yaml").raw

    def copy_with(self, *steps) -> dict:
        """The audit copy of the staged recipe with (place, step, id) added in order."""
        audit = audit_recipe_of(self.original_raw())
        for place, step, step_id in steps:
            add_step(audit, place, step, step_id, comment="because")
        return audit

    def run(self, audit: dict) -> AuditRun:
        return run_audit(self.orch, "staged", audit, self.anchors, self.audit)

    def audit_files(self) -> list:
        return sorted(p.name for p in self.audit.glob("*.parquet")) if self.audit.exists() else []

    def original_files(self) -> dict:
        return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(self.anchors.glob("*.parquet"))}


@pytest.fixture
def world(tmp_path):
    w = World(tmp_path)
    w.build_all()          # the original's tables are stored, as the app stores them
    return w


def reused(run: AuditRun, table: str) -> bool:
    t = run.tables[table]
    return t.t1 == FROM_ORIGINAL and t.t2 in (FROM_ORIGINAL, NONE)


# =====================================================================================================================
# No step: everything is the original's
# =====================================================================================================================


def test_a_copy_with_no_step_reuses_everything_builds_nothing_and_affects_no_plot(world):
    before = world.original_files()
    stored = stores_during(world, lambda: setattr(world, "result", world.run(world.copy_with())))
    run = world.result
    assert stored == [], "nothing is built"
    assert world.audit_files() == []
    assert all(reused(run, t) for t in ("A", "B", "J", "X"))
    assert run.tables["J"].t2 == FROM_ORIGINAL and run.tables["X"].t2 == FROM_ORIGINAL and run.tables["A"].t2 == NONE
    assert all(p.reused and not p.affected for p in run.plots.values()) and set(run.plots) == {"pj", "px", "pa"}
    assert run.affected_plots == [] and run.built_tables == []
    assert all(t.t1_key_original == t.t1_key_audit and t.t2_key_original == t.t2_key_audit for t in run.tables.values())
    assert world.original_files() == before


def test_the_original_is_stored_when_it_was_not_as_the_app_stores_it(tmp_path):
    w = World(tmp_path)
    assert list(w.anchors.glob("*.parquet")) == []
    run = w.run(w.copy_with())
    assert sorted(p.name for p in w.anchors.glob("*.parquet")) == ["A.parquet", "B.parquet", "J.parquet", "J__T2.parquet", "X.parquet", "X__T2.parquet"]
    assert w.audit_files() == [] and run.built_tables == []


# =====================================================================================================================
# A step at tier 1, tier 2, tier 3: only what is after it changes
# =====================================================================================================================

CASES = {
    # place, step, (tables built as `<t> T1` / `<t> T2`), audit files, affected plots
    "tier1 of a table that a join reads": (("T1:A", KEEP_S2), ["A T1", "J T1", "J T2"], ["A.parquet", "J.parquet", "J__T2.parquet"], ["pj", "pa"]),
    "tier1 of the other ingredient": (("T1:B", KEEP_S2), ["B T1", "J T1", "J T2"], ["B.parquet", "J.parquet", "J__T2.parquet"], ["pj"]),
    "tier1 of the join": (("T1:J", KEEP_S2), ["J T1", "J T2"], ["J.parquet", "J__T2.parquet"], ["pj"]),
    "tier1 of the unrelated table": (("T1:X", KEEP_S2), ["X T1", "X T2"], ["X.parquet", "X__T2.parquet"], ["px"]),
    "tier2 of the join": (("T2:J", DROP_GROUP_B), ["J T2"], ["J__T2.parquet"], ["pj"]),
    "tier2 of the unrelated table": (("T2:X", DROP_GROUP), ["X T2"], ["X__T2.parquet"], ["px"]),
    "tier2 of a table with no tier 2 of its own": (("T2:A", KEEP_S2), ["A T2"], ["A__T2.parquet"], ["pa"]),
    "tier3 of a plot with no tier 3": (("T3:pj", DROP_GROUP_B), [], [], ["pj"]),
    "tier3 of a plot with a tier 3": (("T3:pa", KEEP_S1), [], [], ["pa"]),
    "tier3 of the plot on the unrelated table": (("T3:px", DROP_GROUP), [], [], ["px"]),
}


@pytest.mark.parametrize("name", sorted(CASES))
def test_a_step_changes_only_the_tables_and_plots_after_it_and_the_rest_is_reused(world, name):
    """MUTATION R1: a run that always reads the original's table builds nothing, so every case fails."""
    (place, step), built, files, affected = CASES[name]
    before = world.original_files()
    audit = world.copy_with((place, step, ID1))
    run = world.run(audit)
    assert world.audit_files() == files, "the audit folder holds exactly what was built"
    assert sorted(run.built_tables) == sorted(built)
    assert run.affected_plots == [p for p in ("pj", "px", "pa") if p in affected]
    for table in ("A", "B", "J", "X"):
        stages = {s for s in ("T1", "T2") if f"{table} {s}" in built}
        assert (not stages) == reused(run, table), f"{table}: reused exactly when no stage of it was built"
    for plot_id, plot in run.plots.items():
        assert plot.reused == (plot.key_original == plot.key_audit)
        if plot_id not in affected:
            assert not plot.affected
    assert world.original_files() == before, "the original's stored tables are byte-identical"


def test_the_tables_of_the_copy_are_the_ones_the_step_makes(world):
    run = world.run(world.copy_with(("T1:A", KEEP_S1, ID1)))
    assert pl.read_parquet(run.tables["A"].t1_path)["sample_id"].to_list() == ["s1"]
    assert pl.read_parquet(world.anchors / "A.parquet")["sample_id"].to_list() == ["s1", "s2"], "the original's table is as it was"
    assert run.tables["B"].t1_path == world.anchors / "B.parquet", "an unrelated table is read from the original's folder"
    assert run.tables["A"].t1_path == world.audit / "A.parquet"
    run = world.run(world.copy_with(("T2:J", DROP_GROUP_B, ID1)))
    assert run.tables["J"].t1_path == world.anchors / "J.parquet", "a step at tier 2 reads the original's Tier 1"
    assert run.tables["J"].t2_path == world.audit / "J__T2.parquet"
    assert "group_b" not in pl.read_parquet(run.tables["J"].t2_path).columns
    assert "group_b" in pl.read_parquet(world.anchors / "J__T2.parquet").columns, "the original's Tier 2 is as it was"


def test_a_step_at_tier_1_that_removes_nothing_moves_the_keys_and_affects_no_plot(world):
    """Equal keys imply identical data; different keys do not imply different data (ADR-101 point 6): the content decides."""
    run = world.run(world.copy_with(("T1:A", NOTHING_REMOVED, ID1)))
    assert sorted(run.built_tables) == ["A T1", "J T1", "J T2"], "the keys moved, so the tables were built"
    assert run.plots["pj"].key_original != run.plots["pj"].key_audit and run.plots["pa"].key_original != run.plots["pa"].key_audit
    assert not run.plots["pj"].reused and not run.plots["pj"].affected
    assert not run.plots["pa"].affected and run.affected_plots == []


def test_a_step_at_tier_3_that_removes_nothing_does_not_affect_its_plot(world):
    run = world.run(world.copy_with(("T3:pj", NOTHING_REMOVED, ID1)))
    assert not run.plots["pj"].reused and not run.plots["pj"].affected
    assert world.audit_files() == []


def test_two_steps_at_two_places_change_what_is_after_either(world):
    run = world.run(world.copy_with(("T1:X", KEEP_S2, ID1), ("T3:pj", KEEP_S1, ID2), ("T2:J", DROP_GROUP_B, ID3)))
    assert world.audit_files() == ["J__T2.parquet", "X.parquet", "X__T2.parquet"]
    assert run.affected_plots == ["pj", "px"]


# =====================================================================================================================
# Remove the step: the original back; run twice: nothing built the second time
# =====================================================================================================================


def test_removing_the_step_gives_the_original_back_and_empties_the_audit_folder(world):
    audit = world.copy_with(("T1:A", KEEP_S1, ID1), ("T2:J", DROP_GROUP_B, ID2))
    assert world.run(audit).affected_plots == ["pj", "pa"]
    assert world.audit_files() == ["A.parquet", "J.parquet", "J__T2.parquet"]
    remove_step(audit, ID1)
    remove_step(audit, ID2)
    run = world.run(audit)
    assert world.audit_files() == [], "a table that is the original's again is taken out of the audit's folder"
    assert run.built_tables == [] and run.affected_plots == [] and all(reused(run, t) for t in run.tables)


def test_removing_one_of_two_steps_takes_out_only_what_is_the_originals_again(world):
    audit = world.copy_with(("T1:X", KEEP_S1, ID1), ("T2:J", DROP_GROUP_B, ID2))
    world.run(audit)
    remove_step(audit, ID1)
    world.run(audit)
    assert world.audit_files() == ["J__T2.parquet"]


def test_a_second_run_of_the_same_copy_builds_nothing(world):
    audit = world.copy_with(("T1:A", KEEP_S2, ID1))
    world.run(audit)
    stored = stores_during(world, lambda: setattr(world, "second", world.run(audit)))
    assert stored == [], "the audit's own folder serves what it holds under its key"
    assert world.second.tables["A"].t1 == FROM_AUDIT_STORE and world.second.tables["J"].t2 == FROM_AUDIT_STORE
    assert world.second.affected_plots == ["pj", "pa"]


def test_a_changed_data_file_rebuilds_the_audit_tables_it_feeds(world):
    audit = world.copy_with(("T1:A", FILTER_A, ID1))
    first = world.run(audit)
    assert pl.read_parquet(first.tables["A"].t1_path)["sample_id"].to_list() == ["s1"]
    world.write_data("A", "sample_id\tgroup\ns1\tA\ns2\tB\ns3\tA\n")
    clear_data_analysis_recipe_cache()
    run = world.run(audit)
    assert run.tables["A"].t1 == BUILT
    assert pl.read_parquet(run.tables["A"].t1_path)["sample_id"].to_list() == ["s1", "s3"]
    assert run.tables["B"].t1 == FROM_ORIGINAL


def test_a_table_built_while_the_data_changed_is_not_stored_and_the_run_says_so(world):
    """Every caller of a build is told when the inputs changed during it (STALE-KEY-STORE-1): the run puts it in its result, never silently."""
    from unittest import mock
    audit = world.copy_with(("T1:X", KEEP_S2, ID1))
    real = world.orch.prepare_ingredient

    def ingest_then_the_file_changes(ds_id, *args, **kwargs):
        lf = real(ds_id, *args, **kwargs)
        if ds_id == "X":
            world.write_data("X", "sample_id\tgroup\ns1\tA\ns2\tB\ns3\tB\n")
        return lf

    with mock.patch.object(world.orch, "prepare_ingredient", side_effect=ingest_then_the_file_changes):
        run = world.run(audit)
    assert run.inputs_changed and all("the data files changed" in text and "not stored" in text for text in run.inputs_changed)
    assert any("the audit's table 'X'" in text or "the original's table 'X'" in text for text in run.inputs_changed)


def test_a_run_that_saw_no_change_says_nothing(world):
    assert world.run(world.copy_with(("T1:X", KEEP_S2, ID1))).inputs_changed == ()


# =====================================================================================================================
# A step the engine cannot apply
# =====================================================================================================================


@pytest.mark.parametrize("place", ["T1:A", "T1:J", "T2:J", "T2:A", "T3:pj", "T3:pa"])
def test_a_step_that_cannot_be_applied_is_refused_naming_its_id_and_its_place(world, place):
    audit = world.copy_with((place, BAD, ID1))
    with pytest.raises(AuditRunError) as raised:
        world.run(audit)
    assert raised.value.step_id == ID1 and raised.value.place == place
    assert ID1 in str(raised.value) and place in str(raised.value) and "no_such_column" in str(raised.value)


def test_the_bad_one_of_several_steps_in_a_list_is_the_one_named(world):
    audit = world.copy_with(("T1:A", KEEP_S1, ID1), ("T1:A", BAD, ID2), ("T1:A", NOTHING_REMOVED, ID3))
    with pytest.raises(AuditRunError) as raised:
        world.run(audit)
    assert raised.value.step_id == ID2 and raised.value.place == "T1:A"
    assert world.audit_files() == []
    assert [p.name for p in world.audit.iterdir() if p.name.startswith(".audit_probe_")] == [], "the scratch folder of the diagnosis is removed"


def test_a_bad_step_on_a_table_the_join_reads_is_named_at_its_own_place(world):
    audit = world.copy_with(("T1:B", BAD, ID1))
    with pytest.raises(AuditRunError) as raised:
        world.run(audit)
    assert raised.value.place == "T1:B" and raised.value.step_id == ID1


def test_a_failure_of_the_original_is_not_blamed_on_the_audit(world):
    world.write_recipe(**{"data_schemas/B/tier1/steps": [{"action": "polars_drop", "columns": ["no_such_column"]}]})
    with pytest.raises(Exception) as raised:
        world.run(world.copy_with())
    assert not isinstance(raised.value, AuditRunError)


# =====================================================================================================================
# What does not run
# =====================================================================================================================


def test_a_copy_that_is_not_the_original_plus_audit_steps_does_not_run(world):
    audit = world.copy_with(("T1:A", KEEP_S1, ID1))
    audit["data_schemas"]["B"]["tier1"]["steps"].append(DROP_GROUP)
    with pytest.raises(AuditRunError, match="not the original plus audit steps"):
        world.run(audit)
    audit = world.copy_with()
    audit["data_schemas"]["A"]["tier1"]["steps"].insert(0, {**KEEP_S1, "id": ID1})
    audit["data_schemas"]["A"]["tier1"]["steps"].append(DROP_GROUP)
    with pytest.raises(AuditRunError, match="not at the end"):
        world.run(audit)
    assert world.audit_files() == []


def test_the_two_folders_must_differ(world):
    with pytest.raises(AuditRunError, match="folder of their own"):
        run_audit(world.orch, "staged", world.copy_with(), world.anchors, world.anchors)


def test_the_run_changes_neither_the_original_recipe_nor_the_copy_it_was_given(world):
    audit = world.copy_with(("T1:A", KEEP_S1, ID1), ("T3:pj", DROP_GROUP_B, ID2))
    kept_audit, kept_original = copy.deepcopy(audit), copy.deepcopy(world.original_raw())
    file_before = (world.recipes / "staged.yaml").read_bytes()
    world.run(audit)
    assert audit == kept_audit
    assert world.original_raw() == kept_original
    assert (world.recipes / "staged.yaml").read_bytes() == file_before


# =====================================================================================================================
# The orchestrator: a handed recipe, and nothing changed for the others
# =====================================================================================================================


def test_a_recipe_handed_to_the_engine_is_built_and_stored_under_its_own_key(world, tmp_path):
    """MUTATION (orchestrator): if the build were stopped by the difference between the handed recipe and the file, nothing would be stored."""
    original = load_data_analysis_recipe(world.recipes / "staged.yaml")
    audit = world.copy_with(("T1:A", KEEP_S1, ID1))
    loaded = loaded_from_resolved(original, audit)
    keys = world.orch.compute_data_analysis_recipe_keys("staged", loaded=loaded)
    target = tmp_path / "elsewhere" / "A.parquet"
    target.parent.mkdir()
    table = world.orch.materialize_tier1("staged", "A", target, keys=keys, loaded=loaded).collect()
    assert table["sample_id"].to_list() == ["s1"]
    assert target.exists() and read_anchor_if_key(target, TIER1_KEY_META, keys.tier1_key_of("A")) is not None
    assert keys.tier1_key_of("A") != world.keys().tier1_key_of("A")


def test_without_a_handed_recipe_the_engine_reads_the_file_as_before(world):
    keys = world.keys()
    assert world.orch.materialize_tier1("staged", "A", world.anchor("A"), keys=keys).collect()["sample_id"].to_list() == ["s1", "s2"]
    assert stores_during(world, world.build_all) == [], "the original's stored tables are served"
    world.write_recipe(**{"data_schemas/A/tier1/steps": [KEEP_S1]})
    assert world.orch.materialize_tier1("staged", "A", world.anchor("A")).collect()["sample_id"].to_list() == ["s1"]


def test_the_inputs_changed_check_still_sees_a_recipe_edited_while_a_table_is_built(world):
    """The check of a normal build re-reads the recipe file; only a handed recipe is fixed."""
    keys = world.keys()
    world.write_recipe(**{"data_schemas/X/tier1/steps": [KEEP_S1]})
    assert world.orch.inputs_changed("staged", keys, "X") is not None
    assert world.orch.inputs_changed("staged", world.keys(), "X") is None
    loaded = load_data_analysis_recipe(world.recipes / "staged.yaml")
    assert world.orch.inputs_changed("staged", world.keys(), "X", pinned=loaded) is None


# =====================================================================================================================
# The shipped recipes that have their test data: a copy with no step is the original
# =====================================================================================================================

PIPELINES = ROOT / "config" / "data_analysis_recipes" / "pipelines"
RAW_DATA = ROOT / "assets" / "test_data"
BASELINE = json.loads((ROOT / "app" / "tests" / "golden" / "baseline.json").read_text())["recipes"]


def _golden():
    import importlib.util
    spec = importlib.util.spec_from_file_location("golden_baseline", ROOT / "assets" / "scripts" / "golden_baseline.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("recipe_id", sorted(r for r, v in BASELINE.items() if "load" not in v))
def test_on_every_recipe_of_the_golden_baseline_a_copy_with_no_step_reuses_everything_with_the_golden_records(tmp_path, recipe_id):
    gb = _golden()
    orch = DataOrchestrator(PIPELINES, RAW_DATA)
    original = load_data_analysis_recipe(PIPELINES / f"{recipe_id}.yaml")
    audit = audit_recipe_of(original.raw)
    run = run_audit(orch, recipe_id, audit, tmp_path / "anchors", tmp_path / "audit")
    assert list((tmp_path / "audit").glob("*.parquet")) == [], "nothing is built"
    assert run.built_tables == [] and run.affected_plots == []
    assert all(p.reused for p in run.plots.values())
    for table, record in BASELINE[recipe_id]["t1"].items():
        if "error" in record or table not in run.tables:
            continue
        t = run.tables[table]
        assert t.t1 == FROM_ORIGINAL and t.t1_key_original == t.t1_key_audit
        assert gb.table_record(pl.read_parquet(t.t1_path)) == record, f"{table} T1"
        expected_t2 = BASELINE[recipe_id]["t2"][table]
        if "error" not in expected_t2:
            assert gb.table_record(pl.read_parquet(t.t2_path or t.t1_path)) == expected_t2, f"{table} T2"
