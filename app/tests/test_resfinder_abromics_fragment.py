"""The fragment `ResFinder_Abromics_wrangling.yaml` means what the old one meant (RECIPES-SMALL-1, Eve 2026-11-15: convert, do not delete).

The old fragment used three actions that were removed in the switch to recipe format 1: `derive_categories`, `drop_duplicates`,
`summarize`. The converted fragment is the same work written as steps of today. The reference tables in
`app/tests/golden/resfinder_abromics/` were made by running the OLD functions from git history on the ST22 ResFinder data
(`make_old_result.py` there says how and what differs), so these tests compare the converted steps with the old result:
rows, row order, columns, values.

Also: the list of fragment files that no recipe includes (the fragment is one of them, on purpose, by Eve's decision).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_resfinder_abromics_fragment.py -q
"""
import contextlib
import io
import re
from pathlib import Path

import polars as pl
import pytest
import yaml

import transformer.actions  # noqa: F401  (loads the registry)
from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.data_analysis_recipe_validator import checker_catalogs
from app.modules.orchestrator import DataOrchestrator
from utils.recipe_loader import check_recipe_file

ROOT = Path(__file__).resolve().parents[2]
RECIPES = ROOT / "config" / "data_analysis_recipes"
FRAGMENT = RECIPES / "pipelines" / "1_test_data_ST22_dummy" / "wrangling" / "ResFinder_Abromics_wrangling.yaml"
GOLDEN = ROOT / "app" / "tests" / "golden" / "resfinder_abromics"
RESFINDER = "./assets/test_data/1_test_data_ST22_dummy/test_data_ResFinder_20260307_105756.tsv"
REFERENCE = "./config/references/amr_phenotypes/test_amr_categories_phenotype.tsv"
# steps up to and including the one that drops the helper columns: the part that replaces derive_categories
STEPS_OF_DERIVE_CATEGORIES = 8


def _recipe(folder: Path, steps: dict, resfinder: str = RESFINDER) -> Path:
    """A recipe with the two tables the fragment needs and one join whose tier1 is the given tier (a mapping with `steps`, written as its own file)."""
    (folder / "frag.yaml").write_text(yaml.safe_dump(steps, sort_keys=False), encoding="utf-8")
    text = f"""id: recipe
spec_version: 1
data_engine: python-polars
plot_engine: python-plotnine
info: {{ui_label: "t", description: "t", version: "1.0"}}
data_schemas:
  ResFinder:
    ui_label: ResFinder
    description: "r"
    source: {{type: local_tsv, path: {resfinder}}}
    null_values: []
    strip: true
    input_fields:
      sample_id: {{original_name: sample_id, type: String, is_entity_id: true}}
      gene: {{original_name: Gene, type: String}}
      cge_predicted_phenotype: {{original_name: CGE Predicted Phenotype, type: String}}
    tier1: {{steps: []}}
  AMR_phenotype_reference:
    ui_label: reference
    description: "r"
    source: {{type: local_tsv, path: {REFERENCE}}}
    null_values: []
    strip: true
    input_fields:
      phenotype_name: {{original_name: Predicted Phenotype, type: String}}
      amr_class: {{original_name: AMR Category (Class), type: String}}
    tier1: {{steps: []}}
joins:
  classes:
    ui_label: classes
    description: "d"
    ingredients:
      - dataset_id: ResFinder
      - dataset_id: AMR_phenotype_reference
    tier1: !include 'frag.yaml'
analysis_groups:
  g:
    ui_label: G
    description: "d"
    plots:
      p:
        ui_label: P
        description: "d"
        target_dataset: classes
        mapping: {{x: sample_id}}
        layers: [{{name: geom_bar, params: {{}}}}]
"""
    path = folder / "recipe.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def _run(folder: Path) -> pl.DataFrame:
    clear_data_analysis_recipe_cache()
    orchestrator = DataOrchestrator(folder, ROOT / "assets" / "test_data")
    with contextlib.redirect_stdout(io.StringIO()):
        keys = orchestrator.compute_data_analysis_recipe_keys("recipe")
        return orchestrator.materialize_tier1("recipe", "classes", folder / "a.parquet", keys=keys).collect()


def _fragment_steps() -> dict:
    return yaml.safe_load(FRAGMENT.read_text(encoding="utf-8"))


def _as_text(frame: pl.DataFrame) -> list[tuple]:
    """Every cell as text, a missing value as None: the old tables were written as text."""
    return [tuple(None if v is None else str(v) for v in row) for row in frame.rows()]


def _old(name: str) -> pl.DataFrame:
    return pl.read_csv(GOLDEN / name, separator="\t", infer_schema_length=0)


def test_the_converted_fragment_passes_the_checker(tmp_path):
    path = _recipe(tmp_path, _fragment_steps())
    errors = check_recipe_file(path, "run", catalogs=checker_catalogs(), base=ROOT).errors
    assert [p.text("recipe") for p in errors] == []


def test_the_fragment_uses_no_removed_action():
    text = FRAGMENT.read_text(encoding="utf-8")
    assert not re.search(r"action:\s*['\"]?(derive_categories|drop_duplicates|summarize)['\"]?\s*$", text, re.M)
    assert all(step["action"].startswith(("polars_", "modif_", "step_")) for step in _fragment_steps()["steps"])


def test_the_steps_that_replace_derive_categories_give_the_old_table(tmp_path):
    steps = _fragment_steps()
    steps["steps"] = steps["steps"][:STEPS_OF_DERIVE_CATEGORIES]
    _recipe(tmp_path, steps)
    new = _run(tmp_path)
    old = _old("old_after_derive_categories.tsv")
    assert new.columns == ["sample_id", "gene", "cge_predicted_phenotype", "AMR_Categories_Summary"]
    assert new.columns == old.columns
    assert new.height == old.height == 70, "one row per original row, in the same order"
    assert _as_text(new) == _as_text(old)


def test_the_whole_fragment_gives_the_old_final_table(tmp_path):
    _recipe(tmp_path, _fragment_steps())
    new = _run(tmp_path)
    old = _old("old_final.tsv")
    assert new.columns == old.columns == ["sample_id", "AMR_Categories_Summary", "gene_count"]
    assert new.height == old.height == 12
    assert _as_text(new) == _as_text(old)


def test_the_old_table_has_the_cases_that_make_the_comparison_mean_something():
    """The ST22 data has rows with several drugs of one class and rows with no class; (several classes in one row: the edge cases below)."""
    old = _old("old_after_derive_categories.tsv")
    assert old["cge_predicted_phenotype"].str.contains(",").sum() >= 3, "rows with several drugs"
    assert old["AMR_Categories_Summary"].n_unique() > 5


EDGE_CASES = [
    # sample, gene, CGE Predicted Phenotype -> expected AMR_Categories_Summary
    ("S1", "g1", "Gentamicin, Streptomycin", "Aminoglycosides"),           # two drugs, one class: once
    ("S1", "g2", "Ampicillin,Streptomycin", "Aminoglycosides, Beta-lactams (Penicillins & 1st Gen Cephalosporins)"),  # sorted whatever the order of the drugs, no space after the comma
    ("S2", "g3", "NoSuchDrug", None),                                       # a drug that is not in the reference: no class
    ("S2", "g4", "NoSuchDrug, Sulfamethoxazole", "Sulfonamides"),           # unmapped drugs are dropped
    ("S3", "g5", "", None),                                                 # an empty cell
    ("S3", "g6", "Trimethoprim", "Trimethoprim (Diaminopyrimidines)"),
]


def test_edge_cases_unmapped_drug_empty_cell_two_drugs_one_class_order_kept(tmp_path):
    data = tmp_path / "resfinder.tsv"
    data.write_text("sample_id\tGene\tCGE Predicted Phenotype\n" + "\n".join("\t".join(c) for c in
                    [r[:3] for r in EDGE_CASES]) + "\n", encoding="utf-8")
    steps = _fragment_steps()
    steps["steps"] = steps["steps"][:STEPS_OF_DERIVE_CATEGORIES]
    _recipe(tmp_path, steps, resfinder=str(data))
    new = _run(tmp_path)
    assert [r[1] for r in new.select("sample_id", "AMR_Categories_Summary").rows()] == [e[3] for e in EDGE_CASES]
    assert new["gene"].to_list() == [e[1] for e in EDGE_CASES], "rows keep their order"


# -- the fragments that no recipe includes -----------------------------------------------------------------------------

# Each one is kept on purpose or still to be decided; the reason is the value. A new fragment that nothing includes is
# not in this list and fails the test below, so a forgotten file is seen when it is made.
KNOWN_FRAGMENTS_INCLUDED_BY_NOTHING = {
    "pipelines/1_test_data_ST22_dummy/wrangling/ResFinder_Abromics_wrangling.yaml":
        "converted to format 1 (RECIPES-SMALL-1); no shipped recipe has the reference table as an ingredient",
    "pipelines/1_test_data_ST22_dummy/plots/FastP_reads_boxplot.yaml": "found 2026-11-15, not decided",
    "pipelines/1_test_data_ST22_dummy/wrangling/Detailed_Summary_assembly_wrangling.yaml": "found 2026-11-15, not decided",
    "pipelines/1_test_data_ST22_dummy/wrangling/PlasmidFinder_wrangling.yaml": "found 2026-11-15, not decided",
    "pipelines/stress_test_master/plots/final_plot.yaml": "found 2026-11-15, not decided",
}


def fragments_included_by_nothing(recipes: Path = RECIPES) -> set[str]:
    """YAML files below a recipe folder (not the recipe files themselves) that no `!include` of any file under `recipes` names."""
    files = sorted(recipes.rglob("*.yaml"))
    included = set()
    for f in files:
        for m in re.finditer(r"!include\s+['\"]?([^'\"\s#]+)", f.read_text(encoding="utf-8")):
            included.add((f.parent / m.group(1)).resolve())
    recipe_files = {f for f in files if f.parent.parent == recipes and f.parent.name in ("pipelines", "retest", "templates", "experimental")}
    return {str(f.relative_to(recipes)) for f in files if f not in recipe_files and f.resolve() not in included}


def test_the_fragments_that_nothing_includes_are_exactly_the_known_ones():
    assert fragments_included_by_nothing() == set(KNOWN_FRAGMENTS_INCLUDED_BY_NOTHING)


def test_the_orphan_finder_can_fail(tmp_path):
    (tmp_path / "pipelines" / "r").mkdir(parents=True)
    (tmp_path / "pipelines" / "r.yaml").write_text("a: !include 'r/used.yaml'\n")
    (tmp_path / "pipelines" / "r" / "used.yaml").write_text("x: 1\n")
    assert fragments_included_by_nothing(tmp_path) == set()
    (tmp_path / "pipelines" / "r" / "forgotten.yaml").write_text("x: 1\n")
    assert fragments_included_by_nothing(tmp_path) == {"pipelines/r/forgotten.yaml"}


OLD_OUTPUT_FIELDS_LIST = "Summary_phenotype_length_fragmentation_assembly_output_fields"


def test_the_old_output_fields_list_is_gone_and_no_recipe_file_names_it():
    """Eve 2026-11-15 (N8): the old output-fields list of the phenotype view is deleted; nothing may include or mention it."""
    folder = RECIPES / "pipelines" / "1_test_data_ST22_dummy" / "assembly"
    assert not (folder / f"{OLD_OUTPUT_FIELDS_LIST}.yaml").exists()
    named_in = [str(f.relative_to(RECIPES)) for f in RECIPES.rglob("*.yaml") if OLD_OUTPUT_FIELDS_LIST in f.read_text(encoding="utf-8")]
    assert named_in == []
