"""One function finds the file of a dataset, for reading AND for hashing (SOURCE-LOOKUP-ONE-1), and a recipe
imported from a bundle finds its data by dataset id in the folder of its own import (IMPORT-PATH-1).

Each candidate file holds different rows, so the test can tell WHICH file was read. The file that is read must be the
file that the data hash covers (`get_source_files`).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_dataset_lookup_one.py -q
"""
from pathlib import Path

import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe
from app.modules.orchestrator import DataOrchestrator
from app.modules.session_manager import SessionManager
from utils.errors import IngestionError


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def _tsv(path: Path, marker: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"sample_id\n{marker}\n")
    return path


def _recipe(recipes_dir: Path, recipe_id: str = "tiny", source_path: Path | None = None) -> Path:
    recipes_dir.mkdir(parents=True, exist_ok=True)
    # the loader requires a source block; a path that does not exist stands for "no development path"
    source = f"    source: {{type: local_tsv, path: {source_path or recipes_dir.parent / 'nowhere' / 'T.tsv'}}}\n"
    entry = recipes_dir / f"{recipe_id}.yaml"
    entry.write_text(f"""id: {recipe_id}
info: {{ui_label: Tiny}}
data_engine: python-polars
plot_engine: python-plotnine
data_schemas:
  T:
{source}    null_values: []
    strip: false
    input_fields:
      sample_id: {{original_name: sample_id, type: Categorical, ui_label: Sample, is_entity_id: true}}
    tier1: {{steps: []}}
    tier2: {{steps: []}}
joins:
  C:
    ingredients:
      - dataset_id: T
    tier1: {{steps: []}}
    tier2: {{steps: []}}
analysis_groups:
  g:
    ui_label: G
    plots:
      p:
        ui_label: P
        target_dataset: C
        mapping: {{x: sample_id}}
        layers:
          - name: geom_bar
            params: {{}}
""")
    return entry


def _read(orch: DataOrchestrator, recipes_dir: Path, recipe_id: str = "tiny") -> str:
    """The marker of the file that the engine reads for dataset T of the recipe."""
    raw = load_data_analysis_recipe(recipes_dir / f"{recipe_id}.yaml").raw
    frame = orch.prepare_ingredient("T", raw["data_schemas"]["T"], recipe_id=recipe_id, recipe=raw)
    return frame.collect()["sample_id"].to_list()[0]


def _hashed_marker(orch: DataOrchestrator, recipe_id: str = "tiny") -> str:
    files = orch.get_source_files(recipe_id)
    return files["T"].read_text().splitlines()[1]


# --- the same file is read and hashed, in both lookup modes ----------------------------------------------------

def test_paths_mode_reads_and_hashes_the_recipe_path(tmp_path):
    other = _tsv(tmp_path / "elsewhere" / "T.tsv", "from_source_path")
    _tsv(tmp_path / "raw" / "T.tsv", "from_raw_data")
    recipes = tmp_path / "recipes"
    _recipe(recipes, source_path=other)
    orch = DataOrchestrator(recipes, tmp_path / "raw", data_lookup="data_analysis_recipe_paths")
    assert _read(orch, recipes) == _hashed_marker(orch) == "from_source_path"


def test_by_dataset_id_reads_and_hashes_raw_data_and_ignores_the_recipe_path(tmp_path):
    other = _tsv(tmp_path / "elsewhere" / "T.tsv", "from_source_path")
    _tsv(tmp_path / "raw" / "T.tsv", "from_raw_data")
    recipes = tmp_path / "recipes"
    _recipe(recipes, source_path=other)
    orch = DataOrchestrator(recipes, tmp_path / "raw", data_lookup="by_dataset_id")
    assert _read(orch, recipes) == _hashed_marker(orch) == "from_raw_data"


@pytest.mark.parametrize("mode", ["data_analysis_recipe_paths", "by_dataset_id"])
def test_a_file_that_only_contains_the_id_is_neither_read_nor_hashed(tmp_path, mode):
    """The loose search `**/*<id>*.tsv` of the hash is gone: the engine never read such a file."""
    _tsv(tmp_path / "raw" / "sub" / "xT_old.tsv", "loose")
    recipes = tmp_path / "recipes"
    _recipe(recipes)
    orch = DataOrchestrator(recipes, tmp_path / "raw", data_lookup=mode)
    assert orch.get_source_files("tiny") == {}
    with pytest.raises(Exception):
        _read(orch, recipes)


def test_by_dataset_id_accepts_a_parquet_and_hashes_that_file(tmp_path):
    import polars as pl
    (tmp_path / "raw").mkdir()
    pl.DataFrame({"sample_id": ["from_parquet"]}).write_parquet(tmp_path / "raw" / "T.parquet")
    recipes = tmp_path / "recipes"
    _recipe(recipes)
    orch = DataOrchestrator(recipes, tmp_path / "raw", data_lookup="by_dataset_id")
    assert _read(orch, recipes) == "from_parquet"
    assert orch.get_source_files("tiny")["T"] == tmp_path / "raw" / "T.parquet"


def test_both_extensions_for_one_id_fail_the_read_and_the_hash(tmp_path):
    import polars as pl
    _tsv(tmp_path / "raw" / "T.tsv", "tsv")
    pl.DataFrame({"sample_id": ["pq"]}).write_parquet(tmp_path / "raw" / "T.parquet")
    recipes = tmp_path / "recipes"
    _recipe(recipes)
    orch = DataOrchestrator(recipes, tmp_path / "raw", data_lookup="by_dataset_id")
    with pytest.raises(IngestionError):
        _read(orch, recipes)
    with pytest.raises(IngestionError):
        orch.get_source_files("tiny")


# --- a recipe imported from a bundle: its own data folder -------------------------------------------------------

@pytest.mark.parametrize("mode", ["data_analysis_recipe_paths", "by_dataset_id"])
def test_an_imported_recipe_reads_and_hashes_its_own_folder(tmp_path, mode):
    """Even with a source.path in the recipe and a file of the same id in raw_data."""
    other = _tsv(tmp_path / "exporter_machine" / "T.tsv", "from_source_path")
    _tsv(tmp_path / "raw" / "T.tsv", "from_raw_data")
    imports = tmp_path / "user" / "_imports"
    _tsv(imports / "tiny" / "data" / "T.tsv", "from_import")
    recipes = tmp_path / "recipes"
    _recipe(recipes, source_path=other)
    orch = DataOrchestrator(recipes, tmp_path / "raw", data_lookup=mode, imports_dir=imports)
    assert _read(orch, recipes) == _hashed_marker(orch) == "from_import"


def test_an_imported_recipe_with_a_missing_data_file_fails_and_never_reads_another_file(tmp_path):
    _tsv(tmp_path / "raw" / "T.tsv", "from_raw_data")
    imports = tmp_path / "user" / "_imports"
    (imports / "tiny" / "data").mkdir(parents=True)          # the import exists, its data file does not
    recipes = tmp_path / "recipes"
    _recipe(recipes)
    orch = DataOrchestrator(recipes, tmp_path / "raw", data_lookup="by_dataset_id", imports_dir=imports)
    assert orch.get_source_files("tiny") == {}
    with pytest.raises(IngestionError) as e:
        _read(orch, recipes)
    assert "_imports" in str(e.value) or "import" in str(e.value).lower()


def test_two_imports_keep_separate_data_with_the_same_dataset_id(tmp_path):
    imports = tmp_path / "user" / "_imports"
    _tsv(imports / "tiny_a" / "data" / "T.tsv", "first")
    _tsv(imports / "tiny_b" / "data" / "T.tsv", "second")
    (tmp_path / "raw").mkdir()
    recipes = tmp_path / "recipes"
    _recipe(recipes, "tiny_a")
    _recipe(recipes, "tiny_b")
    orch = DataOrchestrator(recipes, tmp_path / "raw", data_lookup="by_dataset_id", imports_dir=imports)
    assert _read(orch, recipes, "tiny_a") == _hashed_marker(orch, "tiny_a") == "first"
    assert _read(orch, recipes, "tiny_b") == _hashed_marker(orch, "tiny_b") == "second"


def test_a_recipe_without_an_import_folder_is_unchanged_by_the_imports_setting(tmp_path):
    _tsv(tmp_path / "raw" / "T.tsv", "from_raw_data")
    recipes = tmp_path / "recipes"
    _recipe(recipes)
    orch = DataOrchestrator(recipes, tmp_path / "raw", data_lookup="by_dataset_id", imports_dir=tmp_path / "user" / "_imports")
    assert _read(orch, recipes) == _hashed_marker(orch) == "from_raw_data"


def test_the_keys_of_an_imported_recipe_cover_the_files_it_reads(tmp_path):
    imports = tmp_path / "user" / "_imports"
    f = _tsv(imports / "tiny" / "data" / "T.tsv", "one")
    _tsv(tmp_path / "raw" / "T.tsv", "raw")
    recipes = tmp_path / "recipes"
    _recipe(recipes)
    orch = DataOrchestrator(recipes, tmp_path / "raw", data_lookup="by_dataset_id", imports_dir=imports)
    before = orch.compute_data_analysis_recipe_keys("tiny")
    assert before.data_batch_hash == SessionManager.compute_data_batch_hash({"T": f})
    f.write_text("sample_id\ntwo\n")
    after = orch.compute_data_analysis_recipe_keys("tiny")
    assert after.tier1_key_of("T") != before.tier1_key_of("T")
    # a change of the file in raw_data (which is not read) changes nothing
    (tmp_path / "raw" / "T.tsv").write_text("sample_id\nchanged\n")
    assert orch.compute_data_analysis_recipe_keys("tiny").tier1_key_of("T") == after.tier1_key_of("T")


def test_materialize_tier1_of_an_imported_recipe_holds_the_import_rows(tmp_path):
    imports = tmp_path / "user" / "_imports"
    _tsv(imports / "tiny" / "data" / "T.tsv", "imported_row")
    _tsv(tmp_path / "raw" / "T.tsv", "raw_row")
    recipes = tmp_path / "recipes"
    _recipe(recipes)
    orch = DataOrchestrator(recipes, tmp_path / "raw", data_lookup="data_analysis_recipe_paths", imports_dir=imports)
    lf = orch.materialize_tier1("tiny", "C", tmp_path / "user" / "C.parquet")
    assert lf.collect()["sample_id"].to_list() == ["imported_row"]


def test_the_validator_checks_the_import_file_not_the_exporters_original(tmp_path):
    """The data check of an imported recipe reads the import's own copy: one value differs from the original
    that is still on the machine, and the problem found proves WHICH file was read."""
    from app.modules.data_analysis_recipe_validator import validate_data_analysis_recipe_data
    original = _tsv(tmp_path / "exporter_machine" / "T.tsv", "ok")
    (tmp_path / "raw").mkdir()
    imports = tmp_path / "user" / "_imports"
    own = imports / "tiny" / "data" / "T.tsv"
    own.parent.mkdir(parents=True)
    own.write_text("other_column\nx\n")      # the import's copy lacks the declared column sample_id
    recipes = tmp_path / "recipes"
    _recipe(recipes, source_path=original)
    problems = validate_data_analysis_recipe_data(recipes / "tiny.yaml", tmp_path / "raw",
                                                  data_lookup="data_analysis_recipe_paths", imports_dir=imports)
    assert any("sample_id" in p.problem for p in problems), problems
    own.write_text("sample_id\nok\n")
    assert validate_data_analysis_recipe_data(recipes / "tiny.yaml", tmp_path / "raw",
                                              data_lookup="data_analysis_recipe_paths", imports_dir=imports) == []
