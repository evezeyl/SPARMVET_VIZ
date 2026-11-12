"""QA canaries of 1_test_data_ST22_dummy: collections and plots with known answers (2026-11-11).

Each canary isolates ONE failure mode and its correct numbers are computed here from the RAW tsv files, not
through the recipe engine, so a mistake in the engine cannot hide in the oracle:

| Collection / plot                | Failure mode it catches                                             |
|----------------------------------|---------------------------------------------------------------------|
| QA_AMR_per_sample                | a sample that vanishes from a long table (left join), NA counted as a gene |
| QA_ST_with_NA                    | a missing value dropped or filled silently                          |
| QA_year_types                    | "2022.0" instead of "2022" (Float64 to text), the numeric year changed |
| QA_L50_integer                   | integer column for threshold filters (issue 62), values altered      |
| qa_facet_by_mapping (plot)       | panels that were asked for and not drawn (issue 65)                 |
| QA_fanout_exhibit                | two long tables joined on one key multiply rows (issue 68); an EXHIBIT of a known defect |
| QA_aggregated_no_key             | a plot whose data is an aggregate has no sample_id: removing a sample by its ID cannot reach it (issue 60) |
| QA_population_zscore             | a step that depends on the other samples (z-score): where a removal is placed changes the numbers (audit placement rule) |

When the many-to-many check of issue 68 is built, add a test here that it flags QA_fanout_exhibit and no other canary.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_qa_canaries.py -q
"""
from pathlib import Path

import matplotlib
import polars as pl
import pytest

matplotlib.use("Agg")

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.orchestrator import DataOrchestrator
from utils.config_loader import ConfigManager
from viz_factory.viz_factory import VizFactory

ROOT = Path(__file__).resolve().parents[2]
RECIPES_DIR = ROOT / "config" / "data_analysis_recipes" / "pipelines"
RECIPE_ID = "1_test_data_ST22_dummy"
RAW_DIR = ROOT / "assets" / "test_data" / RECIPE_ID
QA_GROUP = "QA Canaries"


def _tsv(pattern: str) -> pl.DataFrame:
    path = next(RAW_DIR.glob(pattern))
    return pl.read_csv(path, separator="\t", infer_schema_length=10000, null_values=["", "NA", "-"])


@pytest.fixture(scope="module")
def raw_config():
    return ConfigManager(str(RECIPES_DIR / f"{RECIPE_ID}.yaml")).raw_config


@pytest.fixture(scope="module")
def stage(tmp_path_factory, raw_config):
    """build(collection) -> (tier1, tier2) as collected frames, through the real orchestrator."""
    clear_data_analysis_recipe_cache()
    orchestrator = DataOrchestrator(RECIPES_DIR, ROOT / "assets" / "test_data")
    keys = orchestrator.compute_data_analysis_recipe_keys(RECIPE_ID)
    anchors = tmp_path_factory.mktemp("anchors")

    def build(collection: str):
        path = anchors / f"{collection}.parquet"
        tier1 = orchestrator.materialize_tier1(RECIPE_ID, collection, path, keys=keys).collect()
        tier2 = orchestrator.materialize_tier2(RECIPE_ID, collection, path, keys=keys).collect()
        return tier1, tier2

    build.orchestrator = orchestrator
    build.keys = keys
    build.anchors = anchors
    return build


def test_amr_canary_keeps_samples_without_a_gene(stage):
    res = _tsv("test_data_ResFinder_*.tsv")
    metadata = _tsv("test_metadata_*.tsv")
    n_samples = metadata["sample_id"].n_unique()
    per_sample = res.group_by("sample_id").len().with_columns(pl.col("sample_id").cast(pl.String))
    without_gene = n_samples - per_sample.height

    tier1, tier2 = stage("QA_AMR_per_sample")
    # T1 is long: one row per gene, plus one empty-gene row for each sample without a gene.
    assert tier1.height == res.height + without_gene
    assert tier2.height == n_samples, "a sample vanished (inner join instead of left join?)"
    assert tier2.filter(pl.col("n_amr_genes") == 0).height == without_gene
    assert tier2["n_amr_genes"].sum() == res.height, "an empty gene was counted as a gene"

    compared = tier2.with_columns(pl.col("sample_id").cast(pl.String)).join(per_sample, on="sample_id", how="left")
    expected = compared["len"].fill_null(0).cast(pl.Int64)
    assert (compared["n_amr_genes"].cast(pl.Int64) == expected).all()


def test_missing_sequence_type_stays_missing(stage):
    summary = _tsv("test_data_Summary_*.tsv")
    tier1, tier2 = stage("QA_ST_with_NA")
    assert tier1.height == summary.height
    assert tier1["ST"].null_count() == summary["Sequence Type"].null_count() == 2, "a missing value was filled or dropped"
    assert tier1.equals(tier2)


def test_year_label_has_no_decimal_and_year_stays_numeric(stage):
    metadata = _tsv("test_metadata_*.tsv")
    tier1, _ = stage("QA_year_types")
    assert tier1["year_label"].dtype == pl.String
    assert not tier1["year_label"].str.ends_with(".0").any(), "Float64 was cast to text without going through Int64"
    expected = metadata["Year"].cast(pl.Int64).cast(pl.String).value_counts().sort("Year").to_dicts()
    got = tier1["year_label"].value_counts().sort("year_label").rename({"year_label": "Year"}).to_dicts()
    assert got == expected
    assert tier1["year"].dtype == pl.Float64, "the numeric year must stay numeric for range filters"


def test_integer_column_keeps_its_values(stage):
    quast = _tsv("test_data_Quast_*.tsv")
    tier1, _ = stage("QA_L50_integer")
    assert tier1["L50"].dtype == pl.Int64
    assert tier1["L50"].value_counts().sort("L50").to_dicts() == quast["L50"].value_counts().sort("L50").to_dicts()


def test_fanout_exhibit_multiplies_rows_as_documented(stage, raw_config):
    """EXHIBIT of issue 68: the numbers below are the defect, they are not a target. When the join is fixed or
    the check is built, change this test on purpose."""
    res = _tsv("test_data_ResFinder_*.tsv").group_by("sample_id").len().rename({"len": "n_res"})
    spec = raw_config["additional_datasets_schemas"]["VirulenceFinder"]
    with_stage = stage.orchestrator.prepare_ingredient("VirulenceFinder", spec).collect()
    vir = with_stage.group_by("sample_id").len().rename({"len": "n_vir"})
    both = (
        vir.with_columns(pl.col("sample_id").cast(pl.String))
        .join(res.with_columns(pl.col("sample_id").cast(pl.String)), on="sample_id", how="left")
        .with_columns(pl.col("n_res").fill_null(1))
        .with_columns((pl.col("n_res") * pl.col("n_vir")).alias("expected_rows"))
    )
    tier1, tier2 = stage("QA_fanout_exhibit")
    assert tier1.height == both["expected_rows"].sum()
    assert tier1.height > tier2.height, "the exhibit no longer multiplies rows"
    got = tier2.with_columns(pl.col("sample_id").cast(pl.String)).join(both, on="sample_id")
    assert (got["rows_per_sample"].cast(pl.Int64) == got["expected_rows"].cast(pl.Int64)).all()


def test_aggregated_plot_data_has_no_sample_key(stage):
    """Fixture of issue 60: T1 keeps the key, the T2 that the plot reads does not, and its numbers add up to the samples.

    This is the property that makes "remove sample X from every plot" impossible to do by filtering the plot's
    own data. When the audit reach is built, its tests use this collection as the plot that has no key column.
    """
    metadata = _tsv("test_metadata_*.tsv")
    expected = (
        metadata.group_by("Country", pl.col("Year").cast(pl.Int64).cast(pl.String).alias("year_label"))
        .len()
        .rename({"Country": "country", "len": "n_samples"})
        .with_columns(pl.col("n_samples").cast(pl.Int64))
        .sort("country", "year_label")
    )
    tier1, tier2 = stage("QA_aggregated_no_key")
    assert "sample_id" in tier1.columns and tier1.height == metadata.height
    assert "sample_id" not in tier2.columns, "the aggregate must not carry the key (that is what this canary is for)"
    got = (
        tier2.select(pl.col("country").cast(pl.String), pl.col("year_label").cast(pl.String), pl.col("n_samples").cast(pl.Int64))
        .sort("country", "year_label")
    )
    assert got.equals(expected), "counts per country and year differ from the raw metadata"
    assert got["n_samples"].sum() == metadata["sample_id"].n_unique(), "a sample was lost or counted twice"


def test_zscore_depends_on_the_other_samples(stage):
    """Fixture of the audit placement rule: the z-score of one sample is computed across ALL samples.

    The oracle comes from the raw Quast file. The second half shows why the place of a removal matters: removing a
    sample before the statistic changes every other sample's value, removing it after leaves them unchanged. No
    shipped recipe had a step of this kind until this canary.
    """
    quast = _tsv("test_data_Quast_*.tsv").select(pl.col("sample_id").cast(pl.String), pl.col("N50").cast(pl.Float64))
    mean, sd = quast["N50"].mean(), quast["N50"].std()
    expected = quast.with_columns(((pl.col("N50") - mean) / sd).alias("expected")).sort("sample_id")
    _, tier2 = stage("QA_population_zscore")
    got = tier2.select(pl.col("sample_id").cast(pl.String), pl.col("n50_zscore").cast(pl.Float64)).sort("sample_id")
    assert got.height == quast.height
    assert (got["n50_zscore"] - expected["expected"]).abs().max() < 1e-9, "z-scores differ from the raw-file oracle"

    removed = expected["sample_id"][0]
    kept = expected.filter(pl.col("sample_id") != removed)
    after = kept["expected"]  # removal AFTER the statistic: the other samples keep their value
    before = ((kept["N50"] - kept["N50"].mean()) / kept["N50"].std())  # removal BEFORE the statistic
    assert (after - before).abs().max() > 1e-3, "removing before and after the statistic must give different numbers"


def test_facet_by_in_mapping_gives_panels(stage, raw_config):
    tier1, _ = stage("QA_year_types")
    plot = VizFactory().render(tier1, raw_config, "qa_facet_by_mapping")
    assert type(plot.facet).__name__ == "facet_wrap", "facet_by written in mapping is ignored (issue 65)"
    figure = plot.draw()
    assert len(figure.axes) == 3, "expected one panel per country (France, Germany, Norway)"


def test_every_canary_plot_states_what_to_expect(raw_config):
    plots = raw_config["analysis_groups"][QA_GROUP]["plots"]
    assert plots, "the QA group is empty"
    for plot_id, entry in plots.items():
        assert plot_id.startswith("qa_"), plot_id
        labs = [layer for layer in entry["spec"]["layers"] if layer["name"] == "labs"]
        subtitle = (labs[0]["params"].get("subtitle", "") if labs else "")
        assert subtitle.startswith(("Expect", "Inflated")), f"{plot_id}: the expected numbers must be in the plot subtitle"


def test_plot_ids_are_unique_across_all_recipes():
    seen = {}
    for path in sorted(RECIPES_DIR.glob("*.yaml")):
        raw = ConfigManager(str(path)).raw_config
        for group in (raw.get("analysis_groups") or {}).values():
            for plot_id in (group.get("plots") or {}):
                assert plot_id not in seen, f"plot id {plot_id!r} is in {seen[plot_id]} and {path.stem} (must be unique, rules_data_analysis_recipe_structure.md section 8)"
                seen[plot_id] = path.stem
