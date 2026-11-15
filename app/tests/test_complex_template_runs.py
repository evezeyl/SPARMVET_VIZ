"""The shipped `complex_template` runs: its two data files exist, the recipe passes the checker, the engine builds it and its plot renders.

Found 2026-11-14 (D, proposals point 5): the template named `assets/test_data/genomics_data.tsv` and `metadata.tsv`, which did not
exist, so a user who copied the template could not run it. The files are small synthetic data made by
`assets/scripts/make_complex_template_data.py` (fixed seed; no real data). The tests also check the cases the files hold
(a missing gene list, a sample without a metadata row, a missing country, a tie), so a regenerated file that loses them fails.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_complex_template_runs.py -q
"""
import importlib.util
from pathlib import Path

import matplotlib
import polars as pl

matplotlib.use("Agg")

import transformer.actions  # noqa: F401  (loads the registry)
from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.data_analysis_recipe_validator import checker_catalogs, validate_data_analysis_recipe
from app.modules.orchestrator import DataOrchestrator
from utils.config_loader import ConfigManager
from utils.recipe_loader import check_recipe_file
from viz_factory.viz_factory import VizFactory

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "config" / "data_analysis_recipes" / "templates"
TEST_DATA = ROOT / "assets" / "test_data"
PLOT = "gene_presence_by_country"


def _build(anchor_dir: Path):
    clear_data_analysis_recipe_cache()
    orchestrator = DataOrchestrator(TEMPLATES, TEST_DATA)
    keys = orchestrator.compute_data_analysis_recipe_keys("complex_template")
    anchor = anchor_dir / "master_assembly.parquet"
    return orchestrator.materialize_tier2("complex_template", "master_assembly", anchor, keys=keys)


def test_the_two_data_files_exist_and_are_small():
    for name, header in (("genomics_data.tsv", "Accession\tGene_List"), ("metadata.tsv", "ID\tLocation")):
        lines = (TEST_DATA / name).read_text(encoding="utf-8").splitlines()
        assert lines[0] == header
        assert 20 <= len(lines) - 1 <= 100, f"{name} must stay a few tens of rows"


def test_the_template_passes_the_checker_with_no_error():
    path = TEMPLATES / "complex_template.yaml"
    assert [p.text(path.name) for p in check_recipe_file(path, "run", catalogs=checker_catalogs()).errors] == []
    assert validate_data_analysis_recipe(path) == []


def test_the_engine_builds_the_template_and_the_steps_act_on_the_data(tmp_path):
    frame = _build(tmp_path).collect()
    assert frame.columns == ["sample_id", "gene_presence", "country"]
    genes = frame["gene_presence"].drop_nulls().unique().to_list()
    # the strip step removed the spaces and the quotes: no value starts or ends with one
    assert genes and all(g == g.strip(' "') for g in genes)
    assert len(genes) == 9
    assert frame["gene_presence"].null_count() == 1, "the sample without a gene list stays as one row with a missing gene"
    # the left join keeps a genomics sample that has no metadata row (a missing country), and one more country is missing in the file
    assert frame["country"].null_count() >= 2
    assert "ACC9999" not in frame["sample_id"].to_list(), "a metadata row without genomics data does not enter the left join"
    per_country = (frame.unique(subset=["sample_id"]).group_by("country").len().filter(pl.col("country").is_not_null()))
    assert per_country["len"].n_unique() < per_country.height, "two countries have the same number of isolates (a tie)"


def test_the_plot_of_the_template_renders(tmp_path):
    lf = _build(tmp_path)
    raw = ConfigManager(str(TEMPLATES / "complex_template.yaml")).raw_config
    plot = VizFactory().render(lf, raw, PLOT)
    plot.draw()
    assert plot.data.shape[0] > 0 and {"country", "gene_presence"} <= set(plot.data.columns)


def test_the_generator_is_reproducible_and_matches_the_committed_files(tmp_path):
    """The committed files are what the script writes with its default seed (a hand edit of a file is seen here)."""
    spec = importlib.util.spec_from_file_location("make_complex_template_data", ROOT / "assets" / "scripts" / "make_complex_template_data.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    genomics, metadata = module.build(30, module.DEFAULT_SEED)
    module.write(tmp_path / "g.tsv", ["Accession", "Gene_List"], genomics)
    module.write(tmp_path / "m.tsv", ["ID", "Location"], metadata)
    assert (tmp_path / "g.tsv").read_bytes() == (TEST_DATA / "genomics_data.tsv").read_bytes()
    assert (tmp_path / "m.tsv").read_bytes() == (TEST_DATA / "metadata.tsv").read_bytes()
    again = module.build(30, module.DEFAULT_SEED)
    assert again == (genomics, metadata)
    assert module.build(30, 1) != (genomics, metadata), "the seed changes the data"
