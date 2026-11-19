"""Step order: the order of steps is the order of the lineage (TEST-ORDER-1, package P0, 2026-11-14).

Eve's request (2026-11-12): (1) the order of steps is the order of the lineage; (2) steps at one node commute only
when they are row-local; (3) the z-score canary `QA_population_zscore` shows that the order changes the result and
that the recorded order is the one that is run; (4) the exported recipe, re-run, equals the audit data.

What these tests rely on (all DECIDED, `.claude/design/home_audit_steps.md`):
  5a point 11  the order of steps is their position in the dataflow, never the time they were created; row filters
               and drops at the same node combine (AND, union) and commute; steps at different nodes do not (a filter
               before an aggregation is not the same as the same filter after it); removing a step recomputes the rest.
  5a point 4   the order of application is T1 steps, the recipe's tier-2 steps, audit T2 steps, T3 steps.
  5a point 15  a different order gives a different key; equal keys imply identical data, different keys do not imply
               different data.
  issue #62    a non-integer threshold on an integer column compares as numbers (rule decided, fix in P1).

Method. Real engine, real recipe: the shipped `1_test_data_ST22_dummy` is loaded with the real `ConfigManager`; a
variant is a copy of its resolved configuration with steps added or reordered, written to a temporary folder exactly
as the export writes a recipe (`yaml.safe_dump(sort_keys=False)`) and run by the real `DataOrchestrator`. So the
order that is tested is the order that survives the file and that the engine runs. Steps are the named, parameterised
registered actions the audit writes (`modif_filter`, `polars_drop`, via `utils.action_names`). Oracles are computed
from the RAW tsv files with plain Polars, never through the engine. Every commutation test also checks the result
against its oracle, because two steps that silently do nothing would "commute" too (finding F6 of the test
inventory).

How each test was seen to fail (mutation check, 2026-11-14), see the comment above each test.

Not tested here (they depend on the unconfirmed stage-2 mechanism or on an open choice; listed in the report of
TEST-ORDER-1): the audit compiler writing a step at T1 or T2 of a table (P5, API not confirmed), the series key of
T3 (P4), a filter on a column that a step of the same node drops (order of a drop and a filter on the same column is
not decided). The mechanism pinned by the audit-step tests (HOME's `audited_frame` on the stored T2; the per-plot
export copy `{collection}__t3_{plot}`) is today's: package P5 of `.claude/design/home_stage2_mechanism_spec.md` (v0.1,
not yet confirmed by Eve) replaces it with the audit copy of the recipe, and those tests then move to that copy.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_step_order.py -q
"""
import copy
from pathlib import Path

import polars as pl
import pytest
import yaml

from app.modules.t3_audit_engine import AuditStepError, audited_frame
from app.modules.cache_keys import clear_data_analysis_recipe_cache, tier2_key
from app.modules.orchestrator import DataOrchestrator
from blueprint_arch.t3_translator import build_mode2_recipe
from utils import action_names
from utils.config_loader import ConfigManager

ROOT = Path(__file__).resolve().parents[2]
RECIPES_DIR = ROOT / "config" / "data_analysis_recipes" / "pipelines"
RECIPE_ID = "1_test_data_ST22_dummy"
RAW_DIR = ROOT / "assets" / "test_data" / RECIPE_ID

ZSCORE = "QA_population_zscore"   # collection: T1 = sample_id, country, n50; T2 adds n50_zscore over all samples
ZPLOT = "qa_population_zscore"
L50 = "QA_L50_integer"            # collection: sample_id, L50 as Int64; no tier-2 steps
L50PLOT = "qa_l50_integer"


# ── oracles from the raw files ────────────────────────────────────────────────

def _tsv(pattern: str) -> pl.DataFrame:
    path = next(RAW_DIR.glob(pattern))
    return pl.read_csv(path, separator="\t", infer_schema_length=10000, null_values=["", "NA", "-"])


@pytest.fixture(scope="module")
def raw_samples() -> pl.DataFrame:
    """One row per sample: sample_id, country (metadata), n50 (Quast); the population of the z-score canary."""
    quast = _tsv("test_data_Quast_*.tsv").select(pl.col("sample_id").cast(pl.String), pl.col("N50").cast(pl.Float64).alias("n50"))
    meta = _tsv("test_metadata_*.tsv").select(pl.col("sample_id").cast(pl.String), pl.col("Country").cast(pl.String).alias("country"))
    return meta.join(quast, on="sample_id", how="left").sort("sample_id")


def _zscore(frame: pl.DataFrame) -> pl.DataFrame:
    """The canary's statistic over the rows given: (n50 - mean) / standard deviation (sample sd, like Polars)."""
    return frame.with_columns(((pl.col("n50") - pl.col("n50").mean()) / pl.col("n50").std()).alias("n50_zscore"))


@pytest.fixture(scope="module")
def removed(raw_samples) -> str:
    """The sample removed in the tests: the one with the largest N50, so its removal moves the mean visibly."""
    return raw_samples.sort("n50", descending=True)["sample_id"][0]


@pytest.fixture(scope="module")
def oracle_after(raw_samples, removed) -> pl.DataFrame:
    """Removal AFTER the statistic: z over all samples, then the sample is taken out; the others keep their value."""
    return _zscore(raw_samples).filter(pl.col("sample_id") != removed)


@pytest.fixture(scope="module")
def oracle_before(raw_samples, removed) -> pl.DataFrame:
    """Removal BEFORE the statistic: the sample is taken out, then z over the remaining samples."""
    return _zscore(raw_samples.filter(pl.col("sample_id") != removed))


# ── steps as the audit writes them (named, parameterised registered actions) ──

def remove_samples(ids: list) -> dict:
    return {"action": action_names.FILTER, "column": "sample_id", "op": "not_in", "value": list(ids), "na": "remove"}


def n50_at_least(threshold: float) -> dict:
    return {"action": action_names.FILTER, "column": "n50", "op": "ge", "value": threshold, "na": "remove"}


def drop(*columns: str) -> dict:
    return {"action": action_names.DROP, "columns": list(columns)}


# ── running a variant of the shipped recipe through the real engine ──────────

@pytest.fixture(scope="module")
def raw_config() -> dict:
    return ConfigManager(str(RECIPES_DIR / f"{RECIPE_ID}.yaml")).raw_config


def variant(raw_config: dict, collection: str, *, tier1_extra=None, tier2=None) -> dict:
    """A copy of the resolved recipe: steps appended at the end of a join's tier-1 list, and/or its tier-2 list replaced.

    `plots` is the loader's internal mirror of `analysis_groups`; a recipe written with it does not load again
    (removed the same way as `build_mode2_recipe` does).
    """
    cfg = copy.deepcopy(raw_config)
    cfg.pop("plots", None)
    join = cfg["joins"][collection]
    if tier1_extra:
        join["tier1"]["steps"] = list(join["tier1"]["steps"]) + list(tier1_extra)
    if tier2 is not None:
        join["tier2"] = {**join.get("tier2", {}), "steps": list(tier2)}
    return cfg


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    """run(cfg, collection) -> (T1, T2) collected, plus the keys: the recipe is written to a file and run by the orchestrator."""
    def _run(cfg: dict, collection: str):
        folder = tmp_path_factory.mktemp("recipe")
        (folder / f"{RECIPE_ID}.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True))
        clear_data_analysis_recipe_cache()
        orchestrator = DataOrchestrator(folder, ROOT / "assets" / "test_data")
        keys = orchestrator.compute_data_analysis_recipe_keys(RECIPE_ID)
        anchor = folder / f"{collection}.parquet"
        tier1 = orchestrator.materialize_tier1(RECIPE_ID, collection, anchor, keys=keys).collect()
        tier2 = orchestrator.materialize_tier2(RECIPE_ID, collection, anchor, keys=keys).collect()
        return tier1, tier2, keys
    return _run


@pytest.fixture(scope="module")
def original(run, raw_config):
    """The shipped recipe, unchanged, for the z-score collection: (T1, T2, keys)."""
    return run(variant(raw_config, ZSCORE), ZSCORE)


def plain(frame: pl.DataFrame) -> pl.DataFrame:
    """Categorical to text, so that frames from two separate runs compare by value, not by category encoding."""
    return frame.with_columns(pl.col(pl.Categorical).cast(pl.String))


def assert_z_equals(got: pl.DataFrame, oracle: pl.DataFrame, what: str):
    got = plain(got).select("sample_id", "n50_zscore").sort("sample_id")
    oracle = oracle.select("sample_id", "n50_zscore").sort("sample_id")
    assert got["sample_id"].to_list() == oracle["sample_id"].to_list(), f"{what}: not the same samples"
    assert (got["n50_zscore"] - oracle["n50_zscore"]).abs().max() < 1e-9, f"{what}: z-scores differ from the oracle"


# ── sanity: the two oracles really differ, otherwise every order test below proves nothing ──

def test_the_two_orders_give_different_numbers(oracle_before, oracle_after):
    # Fails when the oracles are made equal (e.g. oracle_before built without the removal).
    joined = oracle_before.join(oracle_after, on="sample_id", suffix="_after")
    assert joined.height == oracle_after.height
    assert (joined["n50_zscore"] - joined["n50_zscore_after"]).abs().min() > 1e-3, \
        "removing the sample before the statistic must change the z-score of EVERY other sample"


# ── (1) and (3): the order of the lineage is the order that is run ───────────

def test_a_removal_at_tier1_runs_before_the_zscore_of_tier2(run, raw_config, removed, oracle_before):
    # Seen failing: moving the removal to the end of tier2 (oracle_after) and swapping the oracle (before -> after).
    _, tier2, _ = run(variant(raw_config, ZSCORE, tier1_extra=[remove_samples([removed])]), ZSCORE)
    assert_z_equals(tier2, oracle_before, "removal at T1, then the recipe's tier-2 z-score")


def test_a_removal_at_the_end_of_tier2_runs_after_the_zscore(run, raw_config, original, removed, oracle_after):
    # Seen failing: putting the removal first in tier2 instead of last.
    own_tier2 = raw_config["joins"][ZSCORE]["tier2"]["steps"]
    _, tier2, _ = run(variant(raw_config, ZSCORE, tier2=list(own_tier2) + [remove_samples([removed])]), ZSCORE)
    assert_z_equals(tier2, oracle_after, "the recipe's tier-2 z-score, then the removal")


@pytest.mark.parametrize("removal_first", [True, False], ids=["removal-then-zscore", "zscore-then-removal"])
def test_within_one_list_the_recorded_order_is_the_run_order(run, raw_config, removed, oracle_before, oracle_after, removal_first):
    """Same node (tier-2), a row filter and a population step: they do not commute, and the list order decides.

    Seen failing: reversing the list in `variant` (the oracles then swap).
    """
    own_tier2 = list(raw_config["joins"][ZSCORE]["tier2"]["steps"])
    assert len(own_tier2) == 1, "the canary's tier-2 is the z-score step alone (QA_population_zscore.yaml)"
    steps = [remove_samples([removed])] + own_tier2 if removal_first else own_tier2 + [remove_samples([removed])]
    _, tier2, _ = run(variant(raw_config, ZSCORE, tier2=steps), ZSCORE)
    assert_z_equals(tier2, oracle_before if removal_first else oracle_after, f"tier2 = {[s['action'] for s in steps]}")


def test_the_unchanged_canary_is_the_zscore_over_every_sample(original, raw_samples):
    # Base line for the tests above. Seen failing: an oracle over 41 samples.
    _, tier2, _ = original
    assert_z_equals(tier2, _zscore(raw_samples), "original recipe")


# ── (2): steps at one node commute only when they are row-local ──────────────

ROW_LOCAL_PAIRS = {
    "two-row-filters": lambda removed, thr: (remove_samples([removed]), n50_at_least(thr)),
    "row-filter-and-drop-of-another-column": lambda removed, thr: (remove_samples([removed]), drop("country")),
}


@pytest.fixture(scope="module")
def threshold(raw_samples) -> float:
    """An N50 value that a sample really has (the middle one): `>=` keeps that sample and `>` removes it, so the
    boundary is tested; about half of the samples are removed."""
    values = raw_samples["n50"].drop_nulls().sort()
    return float(values[values.len() // 2])


@pytest.mark.parametrize("pair", sorted(ROW_LOCAL_PAIRS))
@pytest.mark.parametrize("node", ["tier1", "tier2"])
def test_row_local_steps_at_one_node_commute(run, raw_config, raw_samples, removed, threshold, pair, node):
    """Two row-local steps at the same node, in both orders: identical data (same rows, same order, same columns),
    and equal to the oracle, so two no-ops cannot pass.

    Seen failing: replacing a step of the reversed order by another one (a different threshold, or a drop of `n50`:
    the frames then differ), and making `n50_at_least` write `columns` instead of `column` (a silent no-op: the
    oracle check fails).
    """
    first, second = ROW_LOCAL_PAIRS[pair](removed, threshold)
    own_tier2 = list(raw_config["joins"][ZSCORE]["tier2"]["steps"])

    def build(a, b):
        if node == "tier1":
            return variant(raw_config, ZSCORE, tier1_extra=[a, b])
        return variant(raw_config, ZSCORE, tier2=own_tier2 + [a, b])

    _, ab, _ = run(build(first, second), ZSCORE)
    _, ba, _ = run(build(second, first), ZSCORE)
    assert plain(ab).equals(plain(ba)), f"{pair} at {node}: the two orders give different data"

    # The oracle: the same steps in plain Polars, at the same place relative to the z-score.
    population = raw_samples
    keep = pl.col("sample_id") != removed
    if pair == "two-row-filters":
        keep = keep & (pl.col("n50") >= threshold)
    expected = _zscore(population.filter(keep)) if node == "tier1" else _zscore(population).filter(keep)
    assert_z_equals(ab, expected, f"{pair} at {node}")
    assert ("country" in ab.columns) == (pair == "two-row-filters"), "the drop did not happen (or happened when not asked)"


def test_a_row_filter_and_a_population_step_at_one_node_do_not_commute(run, raw_config, removed):
    """The z-score is not row-local: at the same node it does not commute with a removal (complements the test above).

    Seen failing: replacing the z-score by a row-local step (the two orders then agree).
    """
    zscore_step = raw_config["joins"][ZSCORE]["tier2"]["steps"][0]
    _, ab, _ = run(variant(raw_config, ZSCORE, tier2=[remove_samples([removed]), zscore_step]), ZSCORE)
    _, ba, _ = run(variant(raw_config, ZSCORE, tier2=[zscore_step, remove_samples([removed])]), ZSCORE)
    assert ab["sample_id"].to_list() == ba["sample_id"].to_list(), "both orders keep the same samples"
    assert not plain(ab).equals(plain(ba)), "a removal and a z-score at one node gave the same data in both orders"


def test_an_empty_step_list_is_the_identity(run, raw_config):
    # Edge case: no step at a node. Seen failing: keeping the canary's own tier-2 (the z-score column is added).
    tier1, tier2, _ = run(variant(raw_config, ZSCORE, tier2=[]), ZSCORE)
    assert plain(tier1).equals(plain(tier2)), "an empty tier-2 list must give T2 = T1"


def test_one_step_equals_its_oracle(run, raw_config, raw_samples, threshold):
    # Edge case: a single step. Seen failing: the oracle with `>` instead of `>=` (the median sample is then lost).
    tier1, tier2, _ = run(variant(raw_config, ZSCORE, tier2=[n50_at_least(threshold)]), ZSCORE)
    expected = raw_samples.filter(pl.col("n50") >= threshold)
    got = plain(tier2).sort("sample_id")
    assert got["sample_id"].to_list() == expected["sample_id"].to_list()
    assert 0 < got.height < tier1.height, "the threshold must remove some samples and keep some"


def test_a_different_order_gives_a_different_key_even_when_the_data_is_equal(run, raw_config, removed, threshold):
    """Keys identify the definition, not the content (5a point 15): two row-local steps swapped give equal data and
    different keys; equal keys would claim identity of definitions that differ.

    Seen failing: hashing the step list as a set (sorted) in a copy of `tier2_key`: the keys then agree.
    """
    own_tier2 = list(raw_config["joins"][ZSCORE]["tier2"]["steps"])
    a, b = remove_samples([removed]), n50_at_least(threshold)
    _, t2_ab, keys_ab = run(variant(raw_config, ZSCORE, tier2=own_tier2 + [a, b]), ZSCORE)
    _, t2_ba, keys_ba = run(variant(raw_config, ZSCORE, tier2=own_tier2 + [b, a]), ZSCORE)
    assert plain(t2_ab).equals(plain(t2_ba))
    assert keys_ab.tier1_key_of(ZSCORE) == keys_ba.tier1_key_of(ZSCORE), "only tier-2 differs, so the tier-1 key must not move"
    assert tier2_key(keys_ab.tier1_key_of(ZSCORE), own_tier2 + [a, b], "python-polars") != tier2_key(keys_ba.tier1_key_of(ZSCORE), own_tier2 + [b, a], "python-polars")

    _, _, t1_ab = run(variant(raw_config, ZSCORE, tier1_extra=[a, b]), ZSCORE)
    _, _, t1_ba = run(variant(raw_config, ZSCORE, tier1_extra=[b, a]), ZSCORE)
    assert t1_ab.tier1_key_of(ZSCORE) != t1_ba.tier1_key_of(ZSCORE), "swapping two tier-1 steps must change the tier-1 key"


# ── (3) and (4): HOME's audit step (T3) runs after the recipe; the export re-run equals the audit data ──

def exclusion(node_id: str, sample_ids: list) -> dict:
    return {"id": node_id, "node_type": "exclusion_row", "params": {"column": "sample_id", "op": "not_in", "value": list(sample_ids)},
            "reason": "test"}


def filter_row(node_id: str, column: str, op: str, value) -> dict:
    return {"id": node_id, "node_type": "filter_row", "params": {"column": column, "op": op, "value": value}, "reason": "test"}


def drop_column(node_id: str, column: str) -> dict:
    return {"id": node_id, "node_type": "drop_column", "params": {"column": column}, "reason": "test"}


def test_home_audit_step_runs_after_the_recipe_tier2(original, removed, oracle_after):
    """Application order T1, recipe T2, then T3 (5a point 4): HOME's audited data of the canary plot is the removal
    applied to the stored T2, so the other samples keep their z-score over every sample.

    Seen failing: comparing with oracle_before (the removal placed before the statistic).
    This is today's mechanism; package P5 of `.claude/design/home_stage2_mechanism_spec.md` (v0.1, not yet confirmed by
    Eve) replaces it with the audit copy of the recipe, and the test then moves to that copy.
    """
    _, tier2, _ = original
    audited = audited_frame(tier2.lazy(), [exclusion("n1", [removed])]).collect()
    assert_z_equals(audited, oracle_after, "HOME audit data of qa_population_zscore")


def test_the_export_writes_the_audit_steps_after_the_recipe_tier2_in_recorded_order(raw_config, removed, threshold):
    """The exported recipe keeps the lineage order: the join's own tier-2 first, then the audit steps in the order
    they were recorded.

    Seen failing: reversing the node list given to the translator.
    This is today's mechanism; package P5 of `.claude/design/home_stage2_mechanism_spec.md` (v0.1, not yet confirmed by
    Eve) replaces it with the audit copy of the recipe, and the test then moves to that copy.
    """
    nodes = [exclusion("n1", [removed]), filter_row("n2", "n50", "ge", threshold)]
    exported, skipped = build_mode2_recipe(raw_config, {ZPLOT: nodes})
    assert not skipped
    fork = f"{ZSCORE}__t3_{ZPLOT}"
    own_tier2 = raw_config["joins"][ZSCORE]["tier2"]["steps"]
    fork_tier2 = exported["joins"][fork]["tier2"]["steps"]
    assert fork_tier2[: len(own_tier2)] == own_tier2, "the recipe's own tier-2 steps must come first, unchanged"
    added = fork_tier2[len(own_tier2):]
    assert [(s["column"], s["op"]) for s in added] == [("sample_id", "not_in"), ("n50", "ge")], "not the recorded order"
    assert exported["joins"][fork]["tier1"]["steps"] == raw_config["joins"][ZSCORE]["tier1"]["steps"]


CONCORDANCE_CASES = {
    "no-step": lambda removed, thr: [],
    "one-removal": lambda removed, thr: [exclusion("n1", [removed])],
    "removal-then-threshold": lambda removed, thr: [exclusion("n1", [removed]), filter_row("n2", "n50", "ge", thr)],
    "threshold-then-removal": lambda removed, thr: [filter_row("n2", "n50", "ge", thr), exclusion("n1", [removed])],
    "drop-then-removal": lambda removed, thr: [drop_column("n3", "country"), exclusion("n1", [removed])],
    "removal-then-drop": lambda removed, thr: [exclusion("n1", [removed]), drop_column("n3", "country")],
    "country-one-of": lambda removed, thr: [filter_row("n4", "country", "in", ["Norway", "France"])],
}


@pytest.mark.parametrize("case", sorted(CONCORDANCE_CASES))
def test_the_exported_recipe_rerun_equals_the_audit_data(run, raw_config, original, raw_samples, removed, threshold, case):
    """(4): the exported recipe (the translator's fork), written to a file and re-run from the raw data by the real
    engine, gives exactly the data HOME shows for the plot (`audited_frame` on the stored T2).

    Seen failing: removing the last translated step from the fork of the exported recipe (every case with steps
    fails; "no-step" has no fork); and changing the oracle of one case (the threshold, the removed sample).
    Oracle: the raw files with plain Polars (z-score over all samples, then the steps in order; the z-score is
    computed by `_zscore` over the raw N50 values), compared with BOTH the audit data and the re-run: same samples,
    z-scores and columns. All seven cases have this full oracle.
    This is today's mechanism; package P5 of `.claude/design/home_stage2_mechanism_spec.md` (v0.1, not yet confirmed by
    Eve) replaces it with the audit copy of the recipe, and the test then moves to that copy.
    """
    nodes = CONCORDANCE_CASES[case](removed, threshold)
    _, tier2, _ = original
    home = plain(audited_frame(tier2.lazy(), nodes).collect())

    exported, skipped = build_mode2_recipe(raw_config, {ZPLOT: nodes})
    assert not skipped, skipped
    target = exported["analysis_groups"]["QA Canaries"]["plots"][ZPLOT]["target_dataset"]
    assert (target == ZSCORE) == (not nodes), "a plot with audit steps reads its fork, one without reads the join"
    _, rerun, _ = run(exported, target)
    rerun = plain(rerun)
    expected = _zscore(raw_samples)
    for node in nodes:
        params = node["params"]
        if node["node_type"] == "exclusion_row":
            expected = expected.filter(~pl.col("sample_id").is_in(params["value"]))
        elif node["node_type"] == "filter_row" and params["op"] == "ge":
            expected = expected.filter(pl.col(params["column"]) >= params["value"])
        elif node["node_type"] == "filter_row" and params["op"] == "in":
            expected = expected.filter(pl.col(params["column"]).is_in(params["value"]))
        elif node["node_type"] == "drop_column":
            expected = expected.drop(params["column"])
    assert_z_equals(home, expected, f"{case}: audit data vs raw-file oracle")
    assert_z_equals(rerun, expected, f"{case}: re-run vs raw-file oracle")
    assert sorted(home.columns) == sorted(expected.columns), f"{case}: audit columns differ from the oracle"
    assert sorted(rerun.columns) == sorted(expected.columns), f"{case}: re-run columns differ from the oracle"
    assert rerun.columns == home.columns, f"{case}: columns differ: {rerun.columns} vs {home.columns}"
    assert rerun.equals(home), f"{case}: the re-run of the exported recipe differs from the audit data"
    if nodes:
        assert home.height < tier2.height or "country" not in home.columns, f"{case}: the audit steps changed nothing"


@pytest.fixture(scope="module")
def l50_original(run, raw_config):
    return run(variant(raw_config, L50), L50)


# 8.5 was an xfail until issue #62 was fixed by HOME-EXPLORE-1 (numeric comparison in HOME).
@pytest.mark.parametrize("value", [8, 8.5])
def test_rerun_equals_audit_data_for_a_threshold_on_an_integer_column(run, raw_config, l50_original, value):
    """(4) on the integer canary: `L50 >= value` gives the same rows in HOME and in the re-run of the export.
    The oracle is the raw Quast file compared as numbers (rule of #62).

    Seen failing (before #62 was fixed): HOME kept the samples with L50 = 8 for `>= 8.5` and the re-run did not.
    Seen failing (the integer case): an oracle with `>`.
    """
    _, tier2, _ = l50_original
    nodes = [filter_row("n1", "L50", "ge", value)]
    home = audited_frame(tier2.lazy(), nodes).collect()
    exported, skipped = build_mode2_recipe(raw_config, {L50PLOT: nodes})
    assert not skipped, skipped
    target = exported["analysis_groups"]["QA Canaries"]["plots"][L50PLOT]["target_dataset"]
    _, rerun, _ = run(exported, target)

    quast = _tsv("test_data_Quast_*.tsv")
    expected = sorted(quast.filter(pl.col("L50") >= value)["sample_id"].cast(pl.String).to_list())
    assert sorted(rerun["sample_id"].cast(pl.String).to_list()) == expected, "the re-run does not compare as numbers"
    assert sorted(home["sample_id"].cast(pl.String).to_list()) == expected, "HOME's audit data does not compare as numbers"
    assert rerun.equals(home)


# ── N13 (PLOT-TABLE-ORDER-1): one audit list, one order, in the table, the plot, the bundle and the exported recipe ──
# Decided by Eve 2026-11-14 (no silent error; the plot follows the table; the export is checked) and 2026-11-15 (the order
# written in the recipe is the order performed in the audit; an engine that cannot filter a column that is not there
# returns an error). The ORDER RULE (the recorded order) is DECIDED 2026-11-15 (S2-1): it lives in `audit_steps_in_order` only.

def _home_plot_data(t2: pl.DataFrame, raw_config: dict, nodes: list) -> pl.DataFrame:
    """The rows the PLOT gets: the audited frame (the one function HOME's plot and the bundle's plot call) handed to the
    real VizFactory with the recipe's own plot spec. The spec carries no `filters` key: the audited steps are not applied
    twice, and not in a second order, inside the factory."""
    from viz_factory import VizFactory

    spec = copy.deepcopy(raw_config["analysis_groups"]["QA Canaries"]["plots"][ZPLOT])
    assert "filters" not in spec
    figure = VizFactory().render(audited_frame(t2.lazy(), nodes), {"plots": {ZPLOT: spec}, "plot_defaults": {}}, ZPLOT)
    return pl.from_pandas(figure.data)


def _signature(frame: pl.DataFrame) -> tuple:
    """What two frames must share: the columns and, per sample, the z-score (compared to 9 places)."""
    frame = plain(frame).sort("sample_id")
    return (sorted(frame.columns), frame["sample_id"].to_list(), [round(v, 9) for v in frame["n50_zscore"].to_list()])


def _four_ways(original, raw_config, run, nodes):
    """The table, the plot, the results bundle's `T3_data_<plot>.tsv` (written and read back) and the re-run of the
    exported recipe, for one audit list. A way that cannot run gives the exception it raised."""
    import io

    _, tier2, _ = original
    out = {}

    def way(name, make):
        try:
            out[name] = make()
        except BaseException as exc:   # the engine's own error is a SparmvetError / PanicException: keep whatever it is
            out[name] = exc

    way("table", lambda: audited_frame(tier2.lazy(), nodes).collect())
    way("plot", lambda: _home_plot_data(tier2, raw_config, nodes))

    def bundle():
        buffer = io.BytesIO()
        audited_frame(tier2.lazy(), nodes).collect().write_csv(buffer, separator="\t")
        return pl.read_csv(io.BytesIO(buffer.getvalue()), separator="\t", schema_overrides={"sample_id": pl.String})
    way("bundle", bundle)

    def rerun():
        exported, skipped = build_mode2_recipe(raw_config, {ZPLOT: nodes})
        assert not skipped, skipped
        target = exported["analysis_groups"]["QA Canaries"]["plots"][ZPLOT]["target_dataset"]
        return run(exported, target)[1]
    way("rerun", rerun)
    return out


ORDERS = {
    "A drop n50, then filter n50": lambda thr: [drop_column("d", "n50"), filter_row("f", "n50", "ge", thr)],
    "B filter n50, then drop n50": lambda thr: [filter_row("f", "n50", "ge", thr), drop_column("d", "n50")],
    "C1 drop n50, then filter country": lambda thr: [drop_column("d", "n50"), filter_row("f", "country", "in", ["Norway", "France"])],
    "C2 filter country, then drop n50": lambda thr: [filter_row("f", "country", "in", ["Norway", "France"]), drop_column("d", "n50")],
}


@pytest.mark.parametrize("order", [o for o in sorted(ORDERS) if not o.startswith("A")])
def test_table_plot_bundle_and_rerun_agree_for_an_order_that_can_run(original, raw_config, raw_samples, run, threshold, order):
    """B, C1, C2: the table, the plot, the bundle file and the re-run of the exported recipe have the same rows and values,
    and the row count equals the oracle (the raw files in plain Polars), so four equal no-ops cannot pass.

    Seen failing: the old order (all filters, then all drops) breaks nothing here by itself; the old plot path (drops
    first, the filter skipped) gives 42 rows for B; the mutation that makes `audit_steps_in_order` reverse the list
    breaks B and C2 (a filter on a column that the drop removed) with an AuditStepError.
    """
    nodes = ORDERS[order](threshold)
    ways = _four_ways(original, raw_config, run, nodes)
    for name, result in ways.items():
        assert isinstance(result, pl.DataFrame), f"{order}: the {name} way raised {result!r}"
    if "country" in order:
        expected = raw_samples.filter(pl.col("country").is_in(["Norway", "France"]))
    else:
        expected = raw_samples.filter(pl.col("n50") >= threshold)
    assert 0 < expected.height < raw_samples.height, "the oracle must keep some and remove some"
    for name, frame in ways.items():
        assert frame.height == expected.height, f"{order}: the {name} way has {frame.height} rows, the oracle {expected.height}"
        assert "n50" not in frame.columns, f"{order}: the drop did not happen in the {name} way"
    reference = _signature(ways["table"])
    for name in ("plot", "rerun"):
        assert _signature(ways[name]) == reference, f"{order}: the {name} way differs from the table"
    assert ways["bundle"]["sample_id"].to_list() == plain(ways["table"])["sample_id"].to_list(), f"{order}: bundle file differs"


def test_a_drop_then_a_filter_on_one_column_is_an_error_in_the_table_the_plot_the_bundle_and_the_rerun(original, raw_config, run, threshold):
    """Order A: no way returns rows, none skips the filter. The table, the plot and the bundle raise the same
    AuditStepError, which names the step (number and reason), the column, the step that removed it and the fix; the
    re-run of the exported recipe stops with the engine's own error.

    Seen failing: the old code gave 21 rows (table, bundle) and 42 rows (plot) and no error.
    """
    ways = _four_ways(original, raw_config, run, ORDERS["A drop n50, then filter n50"](threshold))
    for name in ("table", "plot", "bundle"):
        error = ways[name]
        assert isinstance(error, AuditStepError), f"{name}: {error!r}"
    texts = {str(ways[name]) for name in ("table", "plot", "bundle")}
    assert len(texts) == 1, "the three places say the same thing"
    text = texts.pop()
    assert "audit step 2" in text and "n50" in text, text
    assert "audit step 1" in text and "removed it" in text, "it says which step removed the column"
    assert "Fix: remove audit step 1 or audit step 2" in text, text
    assert 'reason: "test"' in text, "it gives the reason of the step"
    assert "column 'n50' is not in the table" in text, "the engine's own words"
    assert ways["table"].pipeline_error is not None, "the Alerts panel gets the same text"
    assert isinstance(ways["rerun"], BaseException) and "n50" in str(ways["rerun"]) and "not in the table" in str(ways["rerun"])


def test_an_audit_step_on_a_column_that_never_existed_names_the_columns_and_the_fix(original):
    """No earlier step removed the column: the error says the table has other columns, never "removed it"."""
    _, tier2, _ = original
    with pytest.raises(AuditStepError) as caught:
        audited_frame(tier2.lazy(), [filter_row("f", "no_such_column", "ge", 1)]).collect()
    text = str(caught.value)
    assert "audit step 1" in text and "no_such_column" in text and "sample_id" in text, text
    assert "removed it" not in text and "remove audit step 1 from the plot's audit list" in text, text


def test_a_drop_of_a_column_that_an_earlier_step_dropped_is_an_error_too(original):
    """Case G of the evidence: the re-run stops on it, so the table must not ignore it (table = re-run)."""
    _, tier2, _ = original
    with pytest.raises(AuditStepError, match=r"audit step 2.*audit step 1"):
        audited_frame(tier2.lazy(), [drop_column("a", "n50"), drop_column("b", "n50")])


def test_the_number_of_a_step_counts_the_active_data_steps_of_the_list(original, threshold):
    """An inactive step and a plot style step are not counted; a step that was removed from the list is gone."""
    _, tier2, _ = original
    nodes = [{"node_type": "aesthetic_override", "params": {"alpha": 0.5}, "id": "a"},
             {**drop_column("x", "country"), "active": False},
             drop_column("d", "n50"), filter_row("f", "n50", "ge", threshold)]
    with pytest.raises(AuditStepError, match=r"audit step 2 .*audit step 1"):
        audited_frame(tier2.lazy(), nodes)


def test_no_step_gives_the_frame_unchanged(original):
    _, tier2, _ = original
    assert audited_frame(tier2.lazy(), []).collect().equals(tier2)


def test_an_exclusion_on_a_dropped_column_is_an_error_not_a_skip(original):
    """Case E of the evidence: the table kept 41 rows, the plot 42 and the re-run stopped."""
    _, tier2, _ = original
    with pytest.raises(AuditStepError, match="n50"):
        audited_frame(tier2.lazy(), [drop_column("d", "n50"), exclusion("e", ["1"]) | {"params": {"column": "n50", "op": "not_in", "value": [1.0]}}])


def test_the_order_rule_is_in_one_function(raw_config):
    """The decided order (2026-11-15, S2-1): the list order. This test pins the one function that carries the rule, so that
    changing the rule is a change of that function and of this test only."""
    from app.modules.t3_audit_engine import audit_steps_in_order

    nodes = [filter_row("f", "n50", "ge", 1), drop_column("d", "n50"), exclusion("e", ["1"])]
    assert [(s["number"], s["kind"], s["column"]) for s in audit_steps_in_order(nodes)] == [
        (1, "filter", "n50"), (2, "drop", "n50"), (3, "filter", "sample_id")]


def test_vizfactory_does_not_skip_a_filter_on_a_missing_column():
    """Real code only: a filter that a recipe's plot spec writes, on a column that the frame does not have, raises with the
    one error form (the plot, the column, the fix); it never returns all rows."""
    from utils.errors import VisualizationError
    from viz_factory import VizFactory

    frame = pl.LazyFrame({"x": [1, 2, 3, 4], "y": [1.0, 2.0, 3.0, 4.0]})
    spec = {"mapping": {"x": "x", "y": "y"}, "layers": [{"name": "geom_point", "params": {}}],
            "filters": [{"column": "n50", "op": "ge", "value": 3}]}
    with pytest.raises(VisualizationError, match=r"Plot 'p'.*'n50'.*Fix:"):
        VizFactory().render(frame, {"plots": {"p": spec}, "plot_defaults": {}}, "p")


def test_the_plot_path_gets_the_rows_of_the_table_path_for_a_filter_then_a_drop_on_one_column(original, raw_config, raw_samples, threshold):
    """Order B through the real function: the plot has the rows of the table, which are the oracle's (raw files).
    Was an xfail: the plot had 42 rows, the table 21.
    """
    _, tier2, _ = original
    nodes = [filter_row("f", "n50", "ge", threshold), drop_column("d", "n50")]
    table = audited_frame(tier2.lazy(), nodes).collect()
    expected = raw_samples.filter(pl.col("n50") >= threshold)
    assert table.height == expected.height < raw_samples.height
    assert _home_plot_data(tier2, raw_config, nodes).height == table.height
