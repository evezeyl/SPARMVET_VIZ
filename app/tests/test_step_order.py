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

from app.handlers.export_handlers import audited_frame
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
    steps = cfg["joins"][collection]["steps"]
    if tier1_extra:
        steps["tier1"] = list(steps["tier1"]) + list(tier1_extra)
    if tier2 is not None:
        steps["tier2"] = list(tier2)
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
    own_tier2 = raw_config["joins"][ZSCORE]["steps"]["tier2"]
    _, tier2, _ = run(variant(raw_config, ZSCORE, tier2=list(own_tier2) + [remove_samples([removed])]), ZSCORE)
    assert_z_equals(tier2, oracle_after, "the recipe's tier-2 z-score, then the removal")


@pytest.mark.parametrize("removal_first", [True, False], ids=["removal-then-zscore", "zscore-then-removal"])
def test_within_one_list_the_recorded_order_is_the_run_order(run, raw_config, removed, oracle_before, oracle_after, removal_first):
    """Same node (tier-2), a row filter and a population step: they do not commute, and the list order decides.

    Seen failing: reversing the list in `variant` (the oracles then swap).
    """
    own_tier2 = list(raw_config["joins"][ZSCORE]["steps"]["tier2"])
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
    own_tier2 = list(raw_config["joins"][ZSCORE]["steps"]["tier2"])

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
    zscore_step = raw_config["joins"][ZSCORE]["steps"]["tier2"][0]
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
    own_tier2 = list(raw_config["joins"][ZSCORE]["steps"]["tier2"])
    a, b = remove_samples([removed]), n50_at_least(threshold)
    _, t2_ab, keys_ab = run(variant(raw_config, ZSCORE, tier2=own_tier2 + [a, b]), ZSCORE)
    _, t2_ba, keys_ba = run(variant(raw_config, ZSCORE, tier2=own_tier2 + [b, a]), ZSCORE)
    assert plain(t2_ab).equals(plain(t2_ba))
    assert keys_ab.tier1_key == keys_ba.tier1_key, "only tier-2 differs, so the tier-1 key must not move"
    assert tier2_key(keys_ab.tier1_key, own_tier2 + [a, b]) != tier2_key(keys_ba.tier1_key, own_tier2 + [b, a])

    _, _, t1_ab = run(variant(raw_config, ZSCORE, tier1_extra=[a, b]), ZSCORE)
    _, _, t1_ba = run(variant(raw_config, ZSCORE, tier1_extra=[b, a]), ZSCORE)
    assert t1_ab.tier1_key != t1_ba.tier1_key, "swapping two tier-1 steps must change the tier-1 key"


# ── (3) and (4): HOME's audit step (T3) runs after the recipe; the export re-run equals the audit data ──

def exclusion(node_id: str, sample_ids: list) -> dict:
    return {"id": node_id, "node_type": "exclusion_row", "params": {"column": "sample_id", "op": "not_in", "value": list(sample_ids)},
            "reason": "test"}


def filter_row(node_id: str, column: str, op: str, value) -> dict:
    return {"id": node_id, "node_type": "filter_row", "params": {"column": column, "op": op, "value": value}, "reason": "test"}


def drop_column(node_id: str, column: str) -> dict:
    return {"id": node_id, "node_type": "drop_column", "params": {"column": column}, "reason": "test"}


def home_rows_and_drops(nodes: list) -> tuple[list, list]:
    """The filter rows and drops HOME hands to `audited_frame`, from a plot's active nodes (same rule as
    `_t3_filter_rows` and `_t3_drop_columns`, `app/handlers/home_theater.py` lines 309-381, which are closures and
    cannot be imported). It is a copy of those closures and must follow them."""
    rows = [{"column": n["params"]["column"], "op": n["params"].get("op", "eq"), "value": n["params"].get("value"),
             "dtype": n["params"].get("dtype", "Utf8")}
            for n in nodes if n["node_type"] in ("filter_row", "exclusion_row")]
    drops = [n["params"]["column"] for n in nodes if n["node_type"] == "drop_column"]
    return rows, drops


def test_home_audit_step_runs_after_the_recipe_tier2(original, removed, oracle_after):
    """Application order T1, recipe T2, then T3 (5a point 4): HOME's audited data of the canary plot is the removal
    applied to the stored T2, so the other samples keep their z-score over every sample.

    Seen failing: comparing with oracle_before (the removal placed before the statistic).
    This is today's mechanism; package P5 of `.claude/design/home_stage2_mechanism_spec.md` (v0.1, not yet confirmed by
    Eve) replaces it with the audit copy of the recipe, and the test then moves to that copy.
    """
    _, tier2, _ = original
    rows, drops = home_rows_and_drops([exclusion("n1", [removed])])
    audited = audited_frame(tier2.lazy(), rows, drops).collect()
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
    own_tier2 = raw_config["joins"][ZSCORE]["steps"]["tier2"]
    fork_tier2 = exported["joins"][fork]["steps"]["tier2"]
    assert fork_tier2[: len(own_tier2)] == own_tier2, "the recipe's own tier-2 steps must come first, unchanged"
    added = fork_tier2[len(own_tier2):]
    assert [(s["column"], s["op"]) for s in added] == [("sample_id", "not_in"), ("n50", "ge")], "not the recorded order"
    assert exported["joins"][fork]["steps"]["tier1"] == raw_config["joins"][ZSCORE]["steps"]["tier1"]


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
    rows, drops = home_rows_and_drops(nodes)
    home = plain(audited_frame(tier2.lazy(), rows, drops).collect())

    exported, skipped = build_mode2_recipe(raw_config, {ZPLOT: nodes})
    assert not skipped, skipped
    target = exported["analysis_groups"]["QA Canaries"]["plots"][ZPLOT]["spec"]["target_dataset"]
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
    rows, drops = home_rows_and_drops(nodes)
    home = audited_frame(tier2.lazy(), rows, drops).collect()
    exported, skipped = build_mode2_recipe(raw_config, {L50PLOT: nodes})
    assert not skipped, skipped
    target = exported["analysis_groups"]["QA Canaries"]["plots"][L50PLOT]["spec"]["target_dataset"]
    _, rerun, _ = run(exported, target)

    quast = _tsv("test_data_Quast_*.tsv")
    expected = sorted(quast.filter(pl.col("L50") >= value)["sample_id"].cast(pl.String).to_list())
    assert sorted(rerun["sample_id"].cast(pl.String).to_list()) == expected, "the re-run does not compare as numbers"
    assert sorted(home["sample_id"].cast(pl.String).to_list()) == expected, "HOME's audit data does not compare as numbers"
    assert rerun.equals(home)
