"""The run of an audit copy without a screen (piece A5 of slice A, changed over to the second list `audit_steps` in piece C-1 of slice C of the HOME audit redesign): `app/modules/audit_run.py`.

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
- the engine runs the author's `steps`, THEN the `audit_steps` of the tier (proved on data with an author's step whose result depends on the order);
- removing the step gives the original back: the audit folder is emptied, the result is all reused;
- a second run of the same copy builds nothing; a step that cannot be applied is refused naming its id and its place (never skipped), also when the list
  holds several audit steps; a copy that is not the original plus audit steps does not run, nor one whose audit step lost its reason or is not an allowed action;
  an `audit_steps` list in a recipe that is not an audit copy is refused by the engine's own reading; the two folders must differ and neither lies inside the other (symlinks followed);
- the orchestrator takes a recipe that is not its file only when it is handed one: existing callers read the file as before.

Mutation index (each seen failing, see the report): MUTATION R1 the run always reads the original's table (it never builds); MUTATION K1 (in
`test_audit_keys.py`) the audit part is left out of the keys; MUTATION C1 (in `libs/utils/tests/test_audit_copy.py`) `without_audit_steps` leaves an audit list; MUTATION R2 the engine runs `audit_steps` before `steps`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_run.py -q
"""
import copy
import hashlib
import json
from pathlib import Path
from unittest import mock

import polars as pl
import pytest

from app.modules.audit_run import (
    BUILT, FROM_AUDIT_STORE, FROM_ORIGINAL, NONE, AuditRun, AuditRunError, run_audit)
from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe, loaded_from_resolved
from app.modules.orchestrator import TIER1_KEY_META, DataOrchestrator
from app.tests.test_table_keys import FILTER_A, ROOT, Staged, recipe, stores_during
from transformer.anchor import read_anchor_if_key
from utils.audit_copy import AuditCopy, add_step, all_audit_steps, remove_step, start_audit
from utils.recipe_tiers import AUDIT_COMMENT, AUDIT_STEPS

AUD = "1a2b3c4d"
ID1, ID2, ID3 = f"audit_{AUD}_1", f"audit_{AUD}_2", f"audit_{AUD}_3"
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

    def build_all(self):
        """What the opening of the recipe stores (D-0326, D-0343): the tables of the staged recipe and the table of the plot that has a tier 3 of its own."""
        super().build_all()
        self.orch.materialize_tier3("staged", "pa", self.anchors, keys=self.keys())

    def original_raw(self) -> dict:
        return load_data_analysis_recipe(self.recipes / "staged.yaml").raw

    def copy_with(self, *steps) -> AuditCopy:
        """The audit of the staged recipe with (place, step) added in order: the ids are `audit_<AUD>_1`, `_2`, ... in that order."""
        audit = start_audit(self.original_raw(), AUD)
        for place, step in steps:
            add_step(audit, place, step, "because")
        return audit

    def run(self, audit) -> AuditRun:
        """Run the copy (an `AuditCopy`, or a recipe dictionary that a test made by hand)."""
        return run_audit(self.orch, "staged", audit.recipe if isinstance(audit, AuditCopy) else audit, self.anchors, self.audit)

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
    audit = world.copy_with((place, step))
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
    run = world.run(world.copy_with(("T1:A", KEEP_S1)))
    assert pl.read_parquet(run.tables["A"].t1_path)["sample_id"].to_list() == ["s1"]
    assert pl.read_parquet(world.anchors / "A.parquet")["sample_id"].to_list() == ["s1", "s2"], "the original's table is as it was"
    assert run.tables["B"].t1_path == world.anchors / "B.parquet", "an unrelated table is read from the original's folder"
    assert run.tables["A"].t1_path == world.audit / "A.parquet"
    run = world.run(world.copy_with(("T2:J", DROP_GROUP_B)))
    assert run.tables["J"].t1_path == world.anchors / "J.parquet", "a step at tier 2 reads the original's Tier 1"
    assert run.tables["J"].t2_path == world.audit / "J__T2.parquet"
    assert "group_b" not in pl.read_parquet(run.tables["J"].t2_path).columns
    assert "group_b" in pl.read_parquet(world.anchors / "J__T2.parquet").columns, "the original's Tier 2 is as it was"


def test_a_step_at_tier_1_that_removes_nothing_moves_the_keys_and_affects_no_plot(world):
    """Equal keys imply identical data; different keys do not imply different data (ADR-101 point 6): the content decides."""
    run = world.run(world.copy_with(("T1:A", NOTHING_REMOVED)))
    assert sorted(run.built_tables) == ["A T1", "J T1", "J T2"], "the keys moved, so the tables were built"
    assert run.plots["pj"].key_original != run.plots["pj"].key_audit and run.plots["pa"].key_original != run.plots["pa"].key_audit
    assert not run.plots["pj"].reused and not run.plots["pj"].affected
    assert not run.plots["pa"].affected and run.affected_plots == []


def test_a_step_at_tier_3_that_removes_nothing_does_not_affect_its_plot(world):
    run = world.run(world.copy_with(("T3:pj", NOTHING_REMOVED)))
    assert not run.plots["pj"].reused and not run.plots["pj"].affected
    assert world.audit_files() == []


def test_two_steps_at_two_places_change_what_is_after_either(world):
    run = world.run(world.copy_with(("T1:X", KEEP_S2), ("T3:pj", KEEP_S1), ("T2:J", DROP_GROUP_B)))
    assert world.audit_files() == ["J__T2.parquet", "X.parquet", "X__T2.parquet"]
    assert run.affected_plots == ["pj", "px"]


# =====================================================================================================================
# Remove the step: the original back; run twice: nothing built the second time
# =====================================================================================================================


def test_removing_the_step_gives_the_original_back_and_empties_the_audit_folder(world):
    audit = world.copy_with(("T1:A", KEEP_S1), ("T2:J", DROP_GROUP_B))
    assert world.run(audit).affected_plots == ["pj", "pa"]
    assert world.audit_files() == ["A.parquet", "J.parquet", "J__T2.parquet"]
    remove_step(audit, ID1)
    remove_step(audit, ID2)
    run = world.run(audit)
    assert world.audit_files() == [], "a table that is the original's again is taken out of the audit's folder"
    assert run.built_tables == [] and run.affected_plots == [] and all(reused(run, t) for t in run.tables)


def test_removing_one_of_two_steps_takes_out_only_what_is_the_originals_again(world):
    audit = world.copy_with(("T1:X", KEEP_S1), ("T2:J", DROP_GROUP_B))
    world.run(audit)
    remove_step(audit, ID1)
    world.run(audit)
    assert world.audit_files() == ["J__T2.parquet"]


def test_a_second_run_of_the_same_copy_builds_nothing(world):
    audit = world.copy_with(("T1:A", KEEP_S2))
    world.run(audit)
    stored = stores_during(world, lambda: setattr(world, "second", world.run(audit)))
    assert stored == [], "the audit's own folder serves what it holds under its key"
    assert world.second.tables["A"].t1 == FROM_AUDIT_STORE and world.second.tables["J"].t2 == FROM_AUDIT_STORE
    assert world.second.affected_plots == ["pj", "pa"]


def test_a_changed_data_file_rebuilds_the_audit_tables_it_feeds(world):
    audit = world.copy_with(("T1:A", FILTER_A))
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
    audit = world.copy_with(("T1:X", KEEP_S2))
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
    assert world.run(world.copy_with(("T1:X", KEEP_S2))).inputs_changed == ()


# =====================================================================================================================
# A step the engine cannot apply
# =====================================================================================================================


@pytest.mark.parametrize("place", ["T1:A", "T1:J", "T2:J", "T2:A", "T3:pj", "T3:pa"])
def test_a_step_that_cannot_be_applied_is_refused_naming_its_id_and_its_place(world, place):
    audit = world.copy_with((place, BAD))
    with pytest.raises(AuditRunError) as raised:
        world.run(audit)
    assert raised.value.step_id == ID1 and raised.value.place == place
    assert ID1 in str(raised.value) and place in str(raised.value) and "no_such_column" in str(raised.value)


def test_the_bad_one_of_several_steps_in_a_list_is_the_one_named(world):
    audit = world.copy_with(("T1:A", KEEP_S1), ("T1:A", BAD), ("T1:A", NOTHING_REMOVED))
    with pytest.raises(AuditRunError) as raised:
        world.run(audit)
    assert raised.value.step_id == ID2 and raised.value.place == "T1:A"
    assert world.audit_files() == []
    assert not world.audit.exists() or [p.name for p in world.audit.iterdir() if p.name.startswith(".audit_probe_")] == [], "the scratch folder of the diagnosis is removed"


def _audit_bytes(world) -> dict:
    return {p.name: p.read_bytes() for p in sorted(world.audit.glob("*.parquet"))} if world.audit.exists() else {}


def test_a_refused_run_leaves_nothing_it_built_in_the_audit_folder_and_the_original_untouched(world):
    """MUTATION F2: without the clean-up on failure, A, J and J__T2 stay after the refused step at tier 3."""
    before = world.original_files()
    audit = world.copy_with(("T1:A", KEEP_S2), ("T3:pj", BAD))
    with pytest.raises(AuditRunError) as raised:
        world.run(audit)
    assert raised.value.step_id == ID2
    assert world.audit_files() == [] and not world.audit.exists(), "the folder this run created is removed too"
    assert world.original_files() == before


def test_a_refused_run_keeps_the_tables_a_previous_run_of_the_same_copy_left_and_removes_only_its_own(world):
    good = world.copy_with(("T1:A", KEEP_S2))
    world.run(good)
    kept = _audit_bytes(world)
    assert sorted(kept) == ["A.parquet", "J.parquet", "J__T2.parquet"]
    before = world.original_files()
    bad = world.copy_with(("T1:A", KEEP_S2), ("T1:B", KEEP_S2), ("T3:pj", BAD))
    with pytest.raises(AuditRunError):
        world.run(bad)
    assert world.original_files() == before
    assert "B.parquet" not in world.audit_files(), "the table this run built is gone"
    assert set(_audit_bytes(world)) <= set(kept), "nothing new is left"
    assert _audit_bytes(world)["A.parquet"] == kept["A.parquet"], "the table the run only read is still there"
    again = world.run(good)
    # J of the earlier run was replaced by the refused run under the same name (its key moved with B) and was taken out with it: rebuilt, not served stale
    assert again.built_tables == ["J T1", "J T2"]


def test_a_refused_run_that_built_nothing_new_changes_nothing_in_the_audit_folder(world):
    good = world.copy_with(("T1:A", KEEP_S2))
    world.run(good)
    kept = _audit_bytes(world)
    with pytest.raises(AuditRunError):
        world.run(world.copy_with(("T1:A", KEEP_S2), ("T3:pj", BAD)))
    assert _audit_bytes(world) == kept


def test_an_interrupt_leaves_nothing_in_the_audit_folder_either(world):
    before = world.original_files()
    audit = world.copy_with(("T1:A", KEEP_S2))
    with mock.patch.object(world.orch, "materialize_tier3", side_effect=KeyboardInterrupt):
        with pytest.raises(KeyboardInterrupt):
            world.run(audit)
    assert world.audit_files() == [] and not world.audit.exists()
    assert world.original_files() == before


def test_a_bad_step_on_a_table_the_join_reads_is_named_at_its_own_place(world):
    audit = world.copy_with(("T1:B", BAD))
    with pytest.raises(AuditRunError) as raised:
        world.run(audit)
    assert raised.value.place == "T1:B" and raised.value.step_id == ID1


def test_a_failure_of_the_original_is_not_blamed_on_the_audit(world):
    world.write_recipe(**{"data_schemas/B/tier1/steps": [{"action": "polars_drop", "columns": ["no_such_column"]}]})
    with pytest.raises(Exception) as raised:
        world.run(world.copy_with())
    assert not isinstance(raised.value, AuditRunError)


# =====================================================================================================================
# The order: the author's steps, then the audit steps
# =====================================================================================================================

SORT_DESC = {"action": "polars_sort", "by": ["sample_id"], "descending": [True], "maintain_order": True}
HEAD_ONE = {"action": "polars_head", "n": 1}


def test_the_engine_runs_the_authors_steps_then_the_audit_steps_proved_on_data(world):
    """MUTATION R2: with the audit list run BEFORE the author's list, the filter `sample_id = s1` runs first and `head 1` keeps that row: the table holds s1;
    in the order of the format the author's steps give the single row s2 and the audit filter then removes it: the table is empty."""
    world.write_recipe(**{"data_schemas/X/tier1/steps": [SORT_DESC, HEAD_ONE]})
    world.build_all()
    assert pl.read_parquet(world.anchors / "X.parquet")["sample_id"].to_list() == ["s2"], "the original: sorted from the top, one row"
    run = world.run(world.copy_with(("T1:X", KEEP_S1)))
    frame = pl.read_parquet(run.tables["X"].t1_path)
    assert frame["sample_id"].to_list() == [] and frame.columns == ["sample_id", "group"]
    assert run.tables["X"].t1 == BUILT, "the table is rebuilt (the key moved)"
    assert run.affected_plots == [], "the plot on X reads the tier 2 of X, a filter on group A: empty in both, so the plot is the same"


def test_the_audit_steps_of_one_list_run_in_the_order_they_were_added(world):
    """Two audit steps in one list, in the order of creation: drop `group`, then a filter on `group` cannot be applied (the column is gone); the other order is fine."""
    world.write_recipe(**{"data_schemas/X/tier2/steps": []})
    world.build_all()
    drop_then_filter = world.copy_with(("T1:X", DROP_GROUP), ("T1:X", FILTER_A))
    with pytest.raises(AuditRunError) as raised:
        world.run(drop_then_filter)
    assert raised.value.step_id == ID2, "the second step is the one that cannot be applied after the first"
    run = world.run(world.copy_with(("T1:X", FILTER_A), ("T1:X", DROP_GROUP)))
    frame = pl.read_parquet(run.tables["X"].t1_path)
    assert frame.columns == ["sample_id"] and frame["sample_id"].to_list() == ["s1"]


def test_an_audit_step_at_tier_2_and_tier_3_runs_after_the_authors_steps_of_that_tier(world):
    """The author's tier 2 of X is [group = A]; an audit filter `sample_id = s2` after it leaves nothing (s1 is the only A, s2 the only other)."""
    world.write_recipe(**{"data_schemas/X/tier2/steps": [FILTER_A]})
    world.build_all()
    assert pl.read_parquet(world.anchors / "X__T2.parquet")["sample_id"].to_list() == ["s1"]
    run = world.run(world.copy_with(("T2:X", KEEP_S2)))
    assert pl.read_parquet(run.tables["X"].t2_path)["sample_id"].to_list() == []


FILTER_A = {"action": "modif_filter", "column": "group", "op": "eq", "value": "A", "na": "remove"}


# =====================================================================================================================
# The engine's own reading: audit steps in a recipe that is not an audit copy
# =====================================================================================================================


def test_the_engine_refuses_an_audit_steps_list_in_a_recipe_that_is_not_an_audit_copy(world):
    """The checker refuses it when a file is loaded (profile run); the engine refuses it too, whatever way the recipe came, with a plain error and no table built."""
    import dataclasses
    from types import SimpleNamespace
    from utils.errors import DataAnalysisRecipeError
    original = load_data_analysis_recipe(world.recipes / "staged.yaml")
    audit = world.copy_with(("T1:A", KEEP_S1), ("T2:J", DROP_GROUP_B), ("T3:pa", KEEP_S1))
    as_a_copy = loaded_from_resolved(original, audit.recipe)
    assert as_a_copy.is_audit_copy and not original.is_audit_copy
    ordinary = dataclasses.replace(as_a_copy, config=SimpleNamespace(raw_config=audit.recipe, loaded_files=()))
    assert not ordinary.is_audit_copy
    target = world.root / "refused" / "A.parquet"
    target.parent.mkdir()
    for call in (lambda: world.orch.materialize_tier1("staged", "A", target, loaded=ordinary),
                 lambda: world.orch.materialize_tier2("staged", "J", target, loaded=ordinary),
                 lambda: world.orch.materialize_tier3("staged", "pa", target.parent, loaded=ordinary)):
        with pytest.raises(DataAnalysisRecipeError, match="only an audit recipe has audit steps"):
            call()
    assert list(target.parent.iterdir()) == []


def test_a_recipe_file_with_an_audit_steps_list_is_refused_by_the_load_gate_and_by_the_engine(world):
    """Two lines of defence: the checker (profile run, HOME's gate) and the engine's own reading when it builds from the file."""
    from app.modules.data_analysis_recipe_validator import validate_data_analysis_recipe
    from utils.errors import DataAnalysisRecipeError
    before = world.original_files()
    world.write_recipe(**{"data_schemas/A/tier1/audit_steps": [{**KEEP_S1, "id": ID1, AUDIT_COMMENT: "x"}]})
    problems = validate_data_analysis_recipe(world.recipes / "staged.yaml")
    assert problems and any("only an audit recipe has audit steps" in str(p) for p in problems)
    with pytest.raises(DataAnalysisRecipeError, match="only an audit recipe has audit steps"):
        world.orch.materialize_tier1("staged", "A", world.anchor("A"))
    assert world.original_files() == before, "nothing was built or stored"


def test_the_run_reads_the_audit_steps_of_tier_2_of_a_table_that_has_none_of_its_own(world):
    """The reader of `audit_run.py` (l.170, `tier2_steps(loaded.raw, table)`) must see an audit step that is the ONLY tier-2 step of table A: with the author's steps
    alone A would be taken for `none` (T2 equals T1), the audit step would be skipped and the plot `pa` not changed. (l.154 reads the ORIGINAL, which has no audit list:
    reading the author's steps there changes nothing, so it has no behaviour of its own to test.)"""
    run = world.run(world.copy_with(("T2:A", KEEP_S2)))
    table = run.tables["A"]
    assert table.t2 == BUILT and table.t2_path is not None and table.t2_path.exists()
    assert pl.read_parquet(table.t2_path)["sample_id"].to_list() == ["s2"]
    assert run.affected_plots == ["pa"]


# =====================================================================================================================
# The engine's own guard: a copy that is not sound is not run, whoever calls (reviewer's point 4)
# =====================================================================================================================


def handed(world, recipe: dict, original: bool = True):
    """A recipe handed to the engine as an audit copy, the way a direct caller does it (no `run_audit`)."""
    import dataclasses
    from app.modules.cache_keys import ResolvedRecipe
    loaded = loaded_from_resolved(load_data_analysis_recipe(world.recipes / "staged.yaml"), recipe)
    return loaded if original else dataclasses.replace(loaded, config=ResolvedRecipe(recipe))


def build_each_tier(world, loaded):
    """The three builds a direct caller can make with a handed recipe; the outcome of each, as the exception type or None."""
    from utils.errors import DataAnalysisRecipeError
    target = world.root / "direct" / "T.parquet"
    target.parent.mkdir(exist_ok=True)
    outcome = {}
    for name, call in (("tier1", lambda: world.orch.materialize_tier1("staged", "A", target, loaded=loaded)),
                       ("tier2", lambda: world.orch.materialize_tier2("staged", "J", target, loaded=loaded)),
                       ("tier3", lambda: world.orch.materialize_tier3("staged", "pa", target.parent, loaded=loaded))):
        try:
            call()
            outcome[name] = None
        except DataAnalysisRecipeError as error:
            outcome[name] = str(error)
    return outcome


def test_a_sound_copy_handed_directly_is_run_as_before(world):
    audit = world.copy_with(("T1:A", KEEP_S1), ("T2:J", DROP_GROUP_B), ("T3:pa", KEEP_S1))
    assert build_each_tier(world, handed(world, audit.recipe)) == {"tier1": None, "tier2": None, "tier3": None}


@pytest.mark.parametrize("tier, place", [("tier1", ("data_schemas", "A")), ("tier2", ("joins", "J")), ("tier3", None)])
def test_an_audit_steps_that_is_not_a_list_is_refused_at_every_tier_by_every_build(world, tier, place):
    """Before: at tier 1 it raised and at tier 2 and tier 3 the engine read it as an empty list and ran nothing, silently."""
    audit = world.copy_with()
    body = audit.recipe["analysis_groups"]["g"]["plots"]["pa"] if place is None else audit.recipe[place[0]][place[1]]
    body[tier] = {**body.get(tier, {"steps": []}), AUDIT_STEPS: "not a list"}
    outcome = build_each_tier(world, handed(world, audit.recipe))
    assert all(text and "is not a list" in text for text in outcome.values()), outcome


def test_a_copy_built_by_hand_with_an_action_that_is_not_allowed_is_refused(world):
    audit = world.copy_with(("T1:A", KEEP_S1))
    audit.recipe["data_schemas"]["A"]["tier1"][AUDIT_STEPS][0].update(action="polars_sort", by=["sample_id"])
    outcome = build_each_tier(world, handed(world, audit.recipe))
    assert all(text and "an audit step is one of modif_filter, polars_drop" in text for text in outcome.values()), outcome


def test_a_copy_built_by_hand_with_no_reason_or_with_the_reason_in_comment_is_refused(world):
    audit = world.copy_with(("T1:A", KEEP_S1))
    step = audit.recipe["data_schemas"]["A"]["tier1"][AUDIT_STEPS][0]
    step["comment"] = step.pop(AUDIT_COMMENT)
    outcome = build_each_tier(world, handed(world, audit.recipe))
    assert all(text and "has no reason" in text for text in outcome.values()), outcome


def test_a_copy_built_by_hand_that_drops_a_key_column_is_refused_by_every_build(world):
    """ADAPTED (D-0358, D-0297): refused by PLACE; at T1:A the join J still reads `sample_id`, and the sentence names the place and the join."""
    audit = world.copy_with(("T1:A", KEEP_S1))
    audit.recipe["data_schemas"]["A"]["tier1"][AUDIT_STEPS][0] = {"action": "polars_drop", "columns": ["sample_id"], "id": ID1, AUDIT_COMMENT: "x"}
    outcome = build_each_tier(world, handed(world, audit.recipe))
    assert all(text and "Cannot drop the column 'sample_id' at T1:A" in text and "step 1 of T1:J" in text for text in outcome.values()), outcome


def test_a_copy_that_changed_an_author_step_or_holds_audit_steps_where_no_tier_reads_them_is_refused(world):
    audit = world.copy_with()
    audit.recipe["data_schemas"]["B"]["tier1"]["steps"].append(DROP_GROUP)
    assert all("not the original plus sound audit steps" in (t or "") for t in build_each_tier(world, handed(world, audit.recipe)).values())
    misplaced = world.copy_with()
    misplaced.recipe["analysis_groups"]["g"]["plots"]["pj"]["tier1"] = {"steps": [], AUDIT_STEPS: []}
    assert all("where no tier reads it" in (t or "") for t in build_each_tier(world, handed(world, misplaced.recipe)).values())


def test_a_copy_built_without_its_original_is_refused_because_nothing_can_be_checked_against(world):
    audit = world.copy_with(("T1:A", KEEP_S1))
    outcome = build_each_tier(world, handed(world, audit.recipe, original=False))
    assert all(text and "built without the recipe it was made from" in text for text in outcome.values()), outcome


# =====================================================================================================================
# What does not run
# =====================================================================================================================


def test_a_copy_that_is_not_the_original_plus_audit_steps_does_not_run(world):
    audit = world.copy_with(("T1:A", KEEP_S1))
    audit.recipe["data_schemas"]["B"]["tier1"]["steps"].append(DROP_GROUP)
    with pytest.raises(AuditRunError, match="not the original plus audit steps"):
        world.run(audit)
    audit = world.copy_with()
    audit.recipe["data_schemas"]["A"]["tier1"]["steps"].insert(0, {**KEEP_S1, "id": ID1, AUDIT_COMMENT: "x"})
    with pytest.raises(AuditRunError, match="belongs in audit_steps"):
        world.run(audit)
    assert world.audit_files() == []


def test_a_hand_made_audit_step_between_two_author_steps_is_refused_not_run(world):
    """The second list says the order; an audit id written among the author's steps (by hand) is named and the copy does not run."""
    world.write_recipe(**{"data_schemas/A/tier1/steps": [DROP_GROUP_B, DROP_GROUP]})
    audit = world.copy_with()
    audit.recipe["data_schemas"]["A"]["tier1"]["steps"].insert(1, {**KEEP_S1, "id": ID1, AUDIT_COMMENT: "x"})
    with pytest.raises(AuditRunError, match="carries the id"):
        world.run(audit)
    assert world.audit_files() == []


def test_an_audit_step_that_lost_its_reason_or_is_not_an_allowed_action_does_not_run(world):
    """A reason can never be lost: moved to `comment` or dropped it is named, and the copy does not run (nothing is built)."""
    audit = world.copy_with(("T1:A", KEEP_S1))
    step = audit.recipe["data_schemas"]["A"]["tier1"][AUDIT_STEPS][0]
    step["comment"] = step.pop(AUDIT_COMMENT)
    with pytest.raises(AuditRunError, match="has no reason"):
        world.run(audit)
    del step["comment"]
    with pytest.raises(AuditRunError, match="has no reason"):
        world.run(audit)
    step[AUDIT_COMMENT] = "back"
    step["action"] = "polars_sort"
    with pytest.raises(AuditRunError, match="is one of modif_filter, polars_drop"):
        world.run(audit)
    assert world.audit_files() == []
    step.update(KEEP_S2)
    assert world.run(audit).affected_plots == ["pj", "pa"], "put right, the same copy runs"


def test_the_two_folders_must_differ(world):
    with pytest.raises(AuditRunError, match="folder of their own"):
        run_audit(world.orch, "staged", world.copy_with().recipe, world.anchors, world.anchors)


def _tree(folder: Path) -> dict:
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "dir" for p in sorted(folder.rglob("*"))}


@pytest.mark.parametrize("how", ["audit_inside_original", "original_inside_audit", "audit_inside_original_by_symlink", "original_inside_audit_by_symlink"])
def test_nested_folders_are_refused_before_anything_is_built(world, tmp_path, how):
    """MUTATION N1: with only the equal-folder check, a refused run of an audit folder that holds the original's folder rolls the original's tables back."""
    inner_audit = world.anchors / "inside_the_original"
    if how == "audit_inside_original":
        original, audit = world.anchors, inner_audit
    elif how == "original_inside_audit":
        original, audit = world.anchors, world.anchors.parent
    elif how == "audit_inside_original_by_symlink":
        (tmp_path / "alias").symlink_to(world.anchors, target_is_directory=True)
        original, audit = world.anchors, tmp_path / "alias" / "inside_the_original"
    else:
        (tmp_path / "alias").symlink_to(world.anchors.parent, target_is_directory=True)
        original, audit = world.anchors, tmp_path / "alias"
    outer = world.anchors.parent
    before_original, before_outer = _tree(world.anchors), _tree(outer)
    with pytest.raises(AuditRunError, match="one inside the other"):
        run_audit(world.orch, "staged", world.copy_with(("T1:A", KEEP_S2), ("T3:pj", BAD)).recipe, original, audit)
    assert _tree(world.anchors) == before_original, "the original's folder is byte-identical"
    assert _tree(outer) == before_outer, "nothing was created anywhere"
    assert not inner_audit.exists()


def test_the_run_changes_neither_the_original_recipe_nor_the_copy_it_was_given(world):
    audit = world.copy_with(("T1:A", KEEP_S1), ("T3:pj", DROP_GROUP_B))
    kept_audit, kept_original = copy.deepcopy(audit.recipe), copy.deepcopy(world.original_raw())
    file_before = (world.recipes / "staged.yaml").read_bytes()
    world.run(audit)
    assert audit.recipe == kept_audit and audit.created == 2
    assert world.original_raw() == kept_original
    assert (world.recipes / "staged.yaml").read_bytes() == file_before


# =====================================================================================================================
# The orchestrator: a handed recipe, and nothing changed for the others
# =====================================================================================================================


def test_a_recipe_handed_to_the_engine_is_built_and_stored_under_its_own_key(world, tmp_path):
    """MUTATION (orchestrator): if the build were stopped by the difference between the handed recipe and the file, nothing would be stored."""
    original = load_data_analysis_recipe(world.recipes / "staged.yaml")
    audit = world.copy_with(("T1:A", KEEP_S1))
    loaded = loaded_from_resolved(original, audit.recipe)
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
    audit = start_audit(original.raw, AUD).recipe
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


# =====================================================================================================================
# The real case of slice A, in the form of the second list: one filter at tier 1 of `Summary` of the ST22 recipe
# =====================================================================================================================


def test_the_real_case_of_slice_a_gives_the_same_numbers_in_the_new_form(tmp_path):
    """Slice A (first form, the step at the end of `steps`) measured on `1_test_data_ST22_dummy`: one filter at tier 1 of `Summary` that keeps 221 of the 623
    rows: 26 of 28 tables reused, 2 built, 1 of 17 plots affected (`phenotype_genome_length_fragmentation`), the original's stored tables byte-identical;
    after removing the step nothing is built and no plot is affected. The same numbers are asked of the second list."""
    recipe_id = "1_test_data_ST22_dummy"
    orch = DataOrchestrator(PIPELINES, RAW_DATA)
    original = load_data_analysis_recipe(PIPELINES / f"{recipe_id}.yaml").raw
    audit = start_audit(original, AUD)
    add_step(audit, "T1:Summary", {"action": "modif_filter", "column": "category", "op": "eq", "value": "cge_phenotype", "na": "remove"}, "the real case")
    assert audit.recipe["data_schemas"]["Summary"]["tier1"]["steps"] == original["data_schemas"]["Summary"]["tier1"]["steps"], "the author's list is untouched"
    anchors, audit_dir = tmp_path / "anchors", tmp_path / "audit"
    run = run_audit(orch, recipe_id, audit.recipe, anchors, audit_dir)
    stored = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(anchors.glob("*.parquet"))}
    assert pl.read_parquet(run.tables["Summary"].t1_path).height == 221 and pl.read_parquet(anchors / "Summary.parquet").height == 623
    assert len(run.tables) == 28 and len(run.plots) == 17
    assert sum(1 for t in run.tables.values() if t.t1 == FROM_ORIGINAL and t.t2 in (FROM_ORIGINAL, NONE)) == 26
    assert sorted(run.built_tables) == ["Summary T1", "Summary_phenotype_length_fragmentation T1"]
    assert run.affected_plots == ["phenotype_genome_length_fragmentation"]
    assert sorted(p.name for p in audit_dir.glob("*.parquet")) == ["Summary.parquet", "Summary_phenotype_length_fragmentation.parquet"]
    remove_step(audit, f"audit_{AUD}_1")
    again = run_audit(orch, recipe_id, audit.recipe, anchors, audit_dir)
    assert again.built_tables == [] and again.affected_plots == [] and list(audit_dir.glob("*.parquet")) == []
    assert {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(anchors.glob("*.parquet"))} == stored, "the original's stored tables are byte-identical"
