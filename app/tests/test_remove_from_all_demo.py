"""The option "remove from all the data" on the demo recipe and its real data (task AUDIT-REMOVE-FROM-ALL-DATA, step 1; D-0415 part B, D-0416): the engine builds the tables.

The pure logic is `utils.remove_from_all` (tests of its own cases: `libs/utils/tests/test_remove_from_all.py`). Here the engine's plan is the input and the engine's build is
the proof, on `1_test_data_ST22_dummy` (28 tables, 17 plots, `sample_id` declared the entity key in 11 schemas):
- the option is offered, reaches 27 of the 28 tables at tier 1 (the 28th, `APEC_STEC_virulence_genes`, has no sample column and is not mentioned), among them the tables
  no plot reads (D-0416 point 1), and says the type of the key there;
- the named case "resequenced sample": two sample ids are removed; they are in every reached table before and in none after, in every table built from them (tier 1 and tier 2
  files the engine stores), and the table that does not hold the key is byte for byte what it was;
- the other samples' rows are the same rows in the same order, EXCEPT in the two tables that compute across samples (`QA_aggregated_no_key` tier 2 counts per group, `QA_population_zscore` tier 2
  is a z-score over the population): there the numbers of the other samples change too. That is the nature of those tables, not a fault; it is said here so that the dialog can tell the user (finding of this step);
- a value that is in no table changes no row and affects no plot; the original's stored tables are byte-identical before and after; `describe` alone builds nothing.

Mutation index (each seen failing, see the report): MUTATION D1 `apply` writes at tier 1 of the first place only; MUTATION D2 the list of values is cut to its first value (seen failing here and in the pure test).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_remove_from_all_demo.py -q
"""
import hashlib
import json
from pathlib import Path

import polars as pl
import pytest

from app.modules.audit_run import run_audit
from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe
from app.modules.orchestrator import DataOrchestrator
from app.modules.plan_composer import compose_plan_book
from utils import audit_copy, remove_from_all as rfa
from utils.audit_copy import start_audit
from utils.recipe_graph import build_graph

ROOT = Path(__file__).resolve().parents[2]
RECIPE_ID = "1_test_data_ST22_dummy"
PIPELINES = ROOT / "config" / "data_analysis_recipes" / "pipelines"
RAW_DATA = ROOT / "assets" / "test_data"
AUD = "1a2b3c4d"
NO_KEY_TABLE = "APEC_STEC_virulence_genes"
COMPUTES_ACROSS_SAMPLES = {("QA_aggregated_no_key", "T2"), ("QA_population_zscore", "T2")}


class Demo:
    """One build of the demo, shared by the tests: the original's tables, the option, the audit with its step per table and the run."""

    def __init__(self, root: Path):
        clear_data_analysis_recipe_cache()
        self.orch = DataOrchestrator(PIPELINES, RAW_DATA)
        self.loaded = load_data_analysis_recipe(PIPELINES / f"{RECIPE_ID}.yaml")
        self.graph = build_graph(self.loaded.raw)
        self.plans = compose_plan_book(self.orch, RECIPE_ID, self.loaded, self.graph)
        self.option = rfa.describe(self.loaded.raw, "sample_id", plans=self.plans)
        self.anchors = root / "anchors"
        self.untouched = run_audit(self.orch, RECIPE_ID, start_audit(self.loaded.raw, AUD).recipe, self.anchors, root / "audit_none")
        self.stored = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(self.anchors.glob("*.parquet"))}
        every = [pl.read_parquet(self.untouched.tables[p.table].t1_path)["sample_id"].unique().to_list() for p in self.option.places]
        self.victims = sorted(set.intersection(*[set(x) for x in every]))[:2]       # two ids: a list of values, not one
        self.audit = start_audit(self.loaded.raw, AUD)
        self.applied = rfa.apply(self.audit, self.option, self.victims, "resequenced: its results come later", plans=self.plans)
        self.run = run_audit(self.orch, RECIPE_ID, self.audit.recipe, self.anchors, root / "audit")

    def tables(self, run, table):
        t = run.tables[table]
        return {"T1": pl.read_parquet(t.t1_path), "T2": pl.read_parquet(t.t2_path) if t.t2_path else None}


@pytest.fixture(scope="module")
def demo(tmp_path_factory):
    yield Demo(tmp_path_factory.mktemp("remove_from_all"))
    clear_data_analysis_recipe_cache()


def test_the_option_is_offered_and_reaches_every_table_that_holds_the_key_among_them_tables_no_plot_reads(demo):
    option, tables = demo.option, demo.graph.collections()
    assert option.offered and option.default_on is False and option.warning == rfa.WARNING
    assert [p.table for p in option.places] == [t for t in tables if t not in (NO_KEY_TABLE, "metadata_schema")], "26 of 28 tables, in graph order (the metadata is not an audit place, D-0632)"
    assert [(n.table, n.code) for n in option.not_reached] == [("metadata_schema", rfa.METADATA_LEFT_ALONE)], "only the metadata is named, as left alone; the table with no sample column is not mentioned"
    assert "left alone" in option.not_reached[0].reason.get("sentence") and "left join" in option.not_reached[0].reason.get("sentence")
    assert option.types == ("String",) and all(p.column == "sample_id" and p.tier == "T1" for p in option.places)
    no_plot = {p.table for p in option.places if not p.plots}
    assert {"Quality_metrics", "Detailed_summary", "FastP_with_metadata", "Bracken_with_metadata", "ResFinder_with_metadata", "AR1_MLST_Serotype_Virulence"} <= no_plot
    assert all(p.plots == tuple(demo.graph.plots_reading(p.place)) for p in option.places)


def test_places_that_the_key_reaches_through_steps_the_app_cannot_read_or_groups_say_so_in_notes(demo):
    notes = {p.table: [n.code for n in p.notes] for p in demo.option.places if p.notes}
    assert set(notes["Summary"]) == {"unread_step_passed"} and notes["Summary_quality"][-1] == "one_row_per_group_after_this_step"
    assert all(not p.notes for p in demo.option.places if p.table in ("Quality_metrics", "FastP"))


def test_apply_without_a_list_writes_at_every_reached_place_as_before_and_the_library_says_nothing_about_other_tables(demo):
    """D-0501: no statement about a table where no step is written. With no list given (PROVISIONAL P8) every reached place is written and none is left."""
    assert demo.applied.ticked_given is False and demo.applied.not_written == ()
    assert list(demo.applied.written) == [p.place for p in demo.option.places] and demo.option.unsure == ()
    assert not hasattr(demo.option, "may_stay") and not hasattr(demo.applied, "may_differ")


def test_the_column_is_offered_only_when_it_is_the_declared_key_not_for_the_join_columns_of_the_recipe(demo):
    for column in ("Gene_name", "VF_gene", "no_such_column"):
        assert not rfa.describe(demo.loaded.raw, column, plans=demo.plans).offered, column


def test_the_resequenced_sample_is_in_every_reached_table_before_and_in_none_after_tier_1_and_tier_2(demo):
    seen_t2 = 0
    for place in demo.option.places:
        before, after = demo.tables(demo.untouched, place.table), demo.tables(demo.run, place.table)
        assert set(demo.victims) <= set(before["T1"]["sample_id"].to_list()), f"{place.table}: the samples are there before (a test of nothing otherwise)"
        assert not set(demo.victims) & set(after["T1"]["sample_id"].to_list()), f"{place.table} T1"
        if after["T2"] is not None and "sample_id" in after["T2"].columns:
            seen_t2 += 1
            assert not set(demo.victims) & set(after["T2"]["sample_id"].to_list()), f"{place.table} T2"
    assert seen_t2 >= 5, "tables with a tier 2 that keeps the sample column were checked too"


def test_nothing_else_changed_the_other_samples_rows_are_the_same_rows_in_the_same_order(demo):
    for place in demo.option.places:
        before, after = demo.tables(demo.untouched, place.table), demo.tables(demo.run, place.table)
        assert after["T1"].equals(before["T1"].filter(~pl.col("sample_id").is_in(demo.victims))), f"{place.table} T1"
        if after["T2"] is None or (place.table, "T2") in COMPUTES_ACROSS_SAMPLES:
            continue
        if "sample_id" in before["T2"].columns:
            assert after["T2"].equals(before["T2"].filter(~pl.col("sample_id").is_in(demo.victims))), f"{place.table} T2"
        else:
            assert after["T2"].equals(before["T2"]), f"{place.table} T2"


def test_the_two_tables_that_compute_across_samples_change_for_the_others_too_and_that_is_known(demo):
    z_before, z_after = demo.tables(demo.untouched, "QA_population_zscore")["T2"], demo.tables(demo.run, "QA_population_zscore")["T2"]
    assert not z_after.equals(z_before.filter(~pl.col("sample_id").is_in(demo.victims))), "a z-score over the population moves when one sample leaves it"
    a_before, a_after = demo.tables(demo.untouched, "QA_aggregated_no_key")["T2"], demo.tables(demo.run, "QA_aggregated_no_key")["T2"]
    assert not a_after.equals(a_before), "a count per group loses the sample"
    assert COMPUTES_ACROSS_SAMPLES == {(t, "T2") for t in ("QA_aggregated_no_key", "QA_population_zscore")}


def test_the_table_that_does_not_hold_the_key_is_what_it_was_and_the_originals_stored_tables_are_byte_identical(demo):
    assert demo.tables(demo.run, NO_KEY_TABLE)["T1"].equals(demo.tables(demo.untouched, NO_KEY_TABLE)["T1"])
    assert demo.run.tables[NO_KEY_TABLE].t1 == "original", "it is not even rebuilt"
    now = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(demo.anchors.glob("*.parquet"))}
    assert {n: h for n, h in now.items() if n in demo.stored} == demo.stored, "every table stored before is byte-identical"
    assert all("__T3_" in n for n in set(now) - set(demo.stored)), "the only new files are the original's table of a plot with its own tier 3 step (the amr_heatmap, D-0623)"


def test_the_steps_are_one_per_reached_table_at_tier_1_in_the_audit_list_and_the_originals_lists_are_untouched(demo):
    steps = audit_copy.all_audit_steps(demo.audit.recipe)
    assert [s.place for s in steps] == [p.place for p in demo.option.places] and list(demo.applied.step_ids) == [s.step_id for s in steps]
    assert all(s.step["op"] == "not_in" and s.step["value"] == demo.victims and s.step["na"] == "keep" for s in steps)
    assert audit_copy.integrity_errors(demo.audit.recipe, demo.loaded.raw, demo.plans) == []
    assert demo.audit.recipe["data_schemas"]["Summary"]["tier1"]["steps"] == demo.loaded.raw["data_schemas"]["Summary"]["tier1"]["steps"]


def test_every_plot_that_reads_a_table_that_held_the_sample_is_affected(demo):
    assert sorted(demo.run.affected_plots) == sorted(demo.graph.plots()), "the demo has a plot on every path from the sample: all 17"
    assert len(demo.graph.plots()) == 17


def test_a_value_that_is_in_no_table_changes_no_row_and_affects_no_plot(demo, tmp_path):
    audit = start_audit(demo.loaded.raw, AUD)
    rfa.apply(audit, demo.option, ["no-such-sample"], "a value nobody has", plans=demo.plans)
    run = run_audit(demo.orch, RECIPE_ID, audit.recipe, demo.anchors, tmp_path / "audit")
    assert run.affected_plots == []
    for place in demo.option.places:
        assert demo.tables(run, place.table)["T1"].equals(demo.tables(demo.untouched, place.table)["T1"]), place.table


def test_describing_the_option_builds_nothing_and_applies_nothing(demo, tmp_path):
    rfa.describe(demo.loaded.raw, "sample_id", plans=demo.plans)
    run = run_audit(demo.orch, RECIPE_ID, start_audit(demo.loaded.raw, AUD).recipe, demo.anchors, tmp_path / "audit")
    assert run.built_tables == [] and run.affected_plots == [] and list((tmp_path / "audit").glob("*.parquet")) == []


# ---- the owner's case (D-0499, D-0531): keep the entity in the quality results only. MEASURED, not said. This test is why the option has no screen yet:
# ---- without a measured effect per result the user cannot see which places to untick.

ENTITY = "10668076"
QUALITY_PLACES_TO_UNTICK = ["QC_Reads_Anchor", "Quast_with_metadata", "FastP", "Quast", "Bracken"]   # the metadata is no longer a place (D-0632)


def _entity_rows_per_plot(demo, audit_recipe, out_dir):
    """Run the audit copy with the app's own run, then read each plot's own table the way the app reads it and count the rows of the entity (any text column equal to it)."""
    from app.modules.cache_keys import loaded_from_resolved
    run = run_audit(demo.orch, RECIPE_ID, audit_recipe, demo.anchors, out_dir)
    loaded = loaded_from_resolved(load_data_analysis_recipe(PIPELINES / f"{RECIPE_ID}.yaml"), audit_recipe, demo.plans)
    keys = demo.orch.compute_data_analysis_recipe_keys(RECIPE_ID, loaded=loaded)
    original_keys = demo.orch.compute_data_analysis_recipe_keys(RECIPE_ID, loaded=load_data_analysis_recipe(PIPELINES / f"{RECIPE_ID}.yaml"))
    counts = {}
    for plot_id in demo.graph.plots():
        target = demo.graph.plot_target(plot_id)
        same_t1 = keys.tier1_key_of(target) == original_keys.tier1_key_of(target)
        t2_same = keys.tier2_key_of(target) == original_keys.tier2_key_of(target)
        frame = demo.orch.materialize_tier3(RECIPE_ID, plot_id, demo.anchors if same_t1 else out_dir, keys=keys, loaded=loaded,
                                            tier2_path=None if t2_same else out_dir / f"{target}__T2.parquet").collect()
        counts[plot_id] = sum(int(frame.select(pl.col(c).cast(pl.String).eq(ENTITY).sum()).item() or 0) for c in frame.columns if frame.schema[c] in (pl.String, pl.Categorical))
    return run, counts


def test_the_owners_case_the_entity_stays_in_exactly_the_three_quality_plots_only_when_six_places_are_unticked_measured(demo, tmp_path):
    places = [p.place for p in demo.option.places]
    assert len(places) == 26 and all(f"T1:{t}" in places for t in QUALITY_PLACES_TO_UNTICK)
    _, before = _entity_rows_per_plot(demo, start_audit(demo.loaded.raw, AUD).recipe, tmp_path / "none")
    assert sorted(k for k, n in before.items() if n == 0) == ["qa_aggregated_no_key"], "the entity is in 16 of the 17 plots (the 17th groups it away) before any removal: a test of nothing otherwise"

    def untick(tables):
        audit = start_audit(demo.loaded.raw, AUD)
        applied = rfa.apply(audit, demo.option, [ENTITY], "kept in the quality results only", plans=demo.plans, ticked=[p for p in places if p not in {f"T1:{t}" for t in tables}])
        assert applied.not_written == tuple(f"T1:{t}" for t in sorted(tables, key=lambda t: places.index(f"T1:{t}"))) and applied.ticked_given is True
        return audit.recipe

    # two places unticked (what the owner could expect to be enough): the entity is gone from every plot, because the source tables below are still ticked
    run2, two = _entity_rows_per_plot(demo, untick(QUALITY_PLACES_TO_UNTICK[:2]), tmp_path / "two")
    assert {k for k, n in two.items() if n > 0} == set() and len(run2.affected_plots) == 17
    # six places unticked: the entity stays in exactly three plots
    run6, six = _entity_rows_per_plot(demo, untick(QUALITY_PLACES_TO_UNTICK), tmp_path / "six")
    stays = sorted(k for k, n in six.items() if n > 0)
    print("MEASURED six unticked: entity stays in", stays, "affected plots:", len(run6.affected_plots))
    assert len(stays) == 3 and len(run6.affected_plots) == 14


def test_after_the_removal_the_entity_is_left_in_the_metadata_only_and_in_no_table_or_plot_built_from_the_data_tables_measured(demo, tmp_path):
    """D-0632, D-0633: the removal is not written at the metadata (not an audit place; the tables that bring it in start from the data table with a left join), so the entity must
    be gone from every other table at tier 1 and tier 2 and from every plot. MEASURED on the demo recipe: the metadata table keeps the entity (it is left alone and the library
    says so, `METADATA_LEFT_ALONE`); any other table that still holds it would be a table the walk did not reach, and the test fails naming it."""
    still = []
    for table in demo.graph.collections():
        for tier, frame in demo.tables(demo.run, table).items():
            if frame is not None and "sample_id" in frame.columns and set(demo.victims) & set(frame["sample_id"].to_list()):
                still.append((table, tier))
    print("MEASURED the entity still appears in", still)
    assert {t for t, _ in still} == {"metadata_schema"}, still
    assert any(n.table == "metadata_schema" and n.code == rfa.METADATA_LEFT_ALONE for n in demo.option.not_reached)
    audit = start_audit(demo.loaded.raw, AUD)
    rfa.apply(audit, demo.option, [ENTITY], "removed from all the data", plans=demo.plans)
    _, counts = _entity_rows_per_plot(demo, audit.recipe, tmp_path / "all")
    assert {k: n for k, n in counts.items() if n} == {}, "the entity is in no plot after the removal at the data tables (the metadata is left alone)"
