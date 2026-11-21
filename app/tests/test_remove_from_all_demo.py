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
        self.written = rfa.apply(self.audit, self.option, self.victims, "resequenced: its results come later", plans=self.plans)
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
    assert [p.table for p in option.places] == [t for t in tables if t != NO_KEY_TABLE], "27 of 28 tables, in graph order"
    assert option.not_reached == (), "the table with no sample column is not mentioned: it has nothing to do with the key"
    assert option.types == ("String",) and all(p.column == "sample_id" and p.tier == "T1" for p in option.places)
    no_plot = {p.table for p in option.places if not p.plots}
    assert {"Quality_metrics", "Detailed_summary", "FastP_with_metadata", "Bracken_with_metadata", "ResFinder_with_metadata", "AR1_MLST_Serotype_Virulence"} <= no_plot
    assert all(p.plots == tuple(demo.graph.plots_reading(p.place)) for p in option.places)


def test_places_that_the_key_reaches_through_steps_the_app_cannot_read_or_groups_say_so_in_notes(demo):
    notes = {p.table: [n.code for n in p.notes] for p in demo.option.places if p.notes}
    assert set(notes["Summary"]) == {"unread_step_passed"} and notes["Summary_quality"][-1] == "one_row_per_group_after_this_step"
    assert all(not p.notes for p in demo.option.places if p.table in ("Quality_metrics", "FastP", "metadata_schema"))


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
    assert {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(demo.anchors.glob("*.parquet"))} == demo.stored


def test_the_steps_are_one_per_reached_table_at_tier_1_in_the_audit_list_and_the_originals_lists_are_untouched(demo):
    steps = audit_copy.all_audit_steps(demo.audit.recipe)
    assert [s.place for s in steps] == [p.place for p in demo.option.places] and list(demo.written) == [s.step_id for s in steps]
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
