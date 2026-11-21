"""A shipped recipe reads the data files of its own `source.path` as a default (D-0425, RECIPE-DEFAULT-DATA-FALLBACK-TEST, part 1).

The owner's requirement: "We need to ensure that the recipe read the test data as a default fallback". The paths in the shipped
recipes are examples and the default used when no data file is selected; the test data is optional. With the local development
deployment (`config/deployment/local/local.yaml`, `data_lookup` not written, so `data_analysis_recipe_paths`), each shipped recipe, with
no data file selected by a user, must read exactly the file its `source.path` names.

What "a data file selected by a user" is in the code today: there is no selector that overrides the recipe's path. HOME's Data Import
REPLACES the file at the place the orchestrator reads (`DataOrchestrator.file_place`), so the replaced file is the file read; a recipe
imported from a bundle reads the folder of its import instead (`import_data_dir`). The priority tests below test those two, nothing else.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_recipe_default_data.py -q
"""
from pathlib import Path
from textwrap import dedent

import polars as pl
import pytest

from app.modules.data_analysis_recipe_validator import find_data_analysis_recipes, validate_data_analysis_recipe_data
from app.modules.orchestrator import DataOrchestrator
from app.modules.cache_keys import load_data_analysis_recipe
from utils.errors import IngestionError

REPO = Path(__file__).resolve().parents[2]
LOCAL_DEPLOYMENT = REPO / "config" / "deployment" / "local" / "local.yaml"
RECIPES_DIR = REPO / "config" / "data_analysis_recipes" / "pipelines"
SHIPPED = find_data_analysis_recipes(RECIPES_DIR)
DEMO = "1_test_data_ST22_dummy"
# Recipes that are broken on purpose are not in this folder (the retest recipes have their own folder and tests,
# test_retest_data_analysis_recipes.py); a shipped recipe that the load gate rejects is skipped below with the gate's reason.


@pytest.fixture(scope="module")
def local():
    """The Bootloader on the local development deployment, started from the repository root, and an orchestrator built as server.py builds it."""
    mp = pytest.MonkeyPatch()
    for var in ("SPARMVET_APP_FEATURES", "SPARMVET_DATA_ANALYSIS_RECIPE"):
        mp.delenv(var, raising=False)
    mp.setenv("SPARMVET_DEPLOYMENT", str(LOCAL_DEPLOYMENT))
    mp.chdir(REPO)
    from app.src.bootloader import Bootloader

    boot = Bootloader()
    orchestrator = DataOrchestrator(
        data_analysis_recipes_dir=boot.get_location("data_analysis_recipes"),
        raw_data_dir=boot.get_location("raw_data"),
        data_lookup=boot.data_lookup,
        imports_dir=boot.get_imports_dir(),
    )
    yield boot, orchestrator
    mp.undo()


def test_the_shipped_recipes_were_found(capsys):
    print(f"shipped recipes found: {len(SHIPPED)}: {[p.stem for p in SHIPPED]}")
    assert SHIPPED, "no shipped recipe found: the discovery is broken, not the recipes"
    assert DEMO in [p.stem for p in SHIPPED]


def test_the_local_deployment_follows_the_recipe_paths(local):
    boot, orchestrator = local
    assert boot.data_lookup == "data_analysis_recipe_paths"
    assert orchestrator.discover_by_dataset_id is False
    assert Path(boot.get_location("raw_data")).resolve() == (REPO / "assets" / "test_data").resolve()


@pytest.mark.parametrize("recipe_path", SHIPPED, ids=lambda p: p.stem)
def test_each_table_reads_the_file_its_source_path_names(local, recipe_path):
    boot, orchestrator = local
    recipe_id = recipe_path.stem
    if recipe_id in boot.rejected_data_analysis_recipes:
        reason = "; ".join(str(p) for p in boot.rejected_data_analysis_recipes[recipe_id]["problems"][:2])
        pytest.skip(f"the load gate rejects '{recipe_id}': {reason}")
    schemas = orchestrator.dataset_schemas(recipe_id)
    assert schemas, f"'{recipe_id}' has no table"
    declared_tables = 0
    for table, schema in schemas.items():
        source = (schema or {}).get("source") or {}
        declared = source.get("path")
        if not declared:
            continue  # a table with no source.path is found by its id in raw_data: test_a_table_with_no_source_path_is_found_by_its_id
        declared_tables += 1
        expected = (REPO / declared).resolve()
        located = orchestrator.locate_dataset_file(recipe_id, table, schema)
        assert located is not None, f"{recipe_id}/{table}: the file '{declared}' that the recipe names is not found"
        assert Path(located).resolve() == expected, f"{recipe_id}/{table}: reads {located}, the recipe names {declared}"
        assert expected.is_file(), f"{recipe_id}/{table}: {declared} does not exist"
        assert REPO in expected.parents, f"{recipe_id}/{table}: {declared} is outside the repository"
        # a path under assets/test_data is the repository's test data; the other examples (reference data, a library's test data) stay inside the repository
        if "assets/test_data" in str(declared):
            assert (REPO / "assets" / "test_data").resolve() in expected.parents
        # the file `get_source_files` hashes for the session key is that same file
        assert Path(orchestrator.get_source_files(recipe_id)[table]).resolve() == expected
        # the place where Data Import writes is that same file
        assert Path(orchestrator.file_place(recipe_id, table, schema)).resolve() == expected
    assert declared_tables, f"'{recipe_id}': no table declares a source.path"


def test_two_tables_that_name_the_same_file_read_the_same_file(local):
    _, orchestrator = local
    schemas = orchestrator.dataset_schemas(DEMO)
    a = orchestrator.locate_dataset_file(DEMO, "Summary", schemas["Summary"])
    b = orchestrator.locate_dataset_file(DEMO, "Summary_quality", schemas["Summary_quality"])
    assert a is not None and Path(a).resolve() == Path(b).resolve()


def test_the_demo_table_really_reads_the_declared_file(local):
    """A real read, not only a path: the rows and the sample ids that come out of the orchestrator are those of the declared file."""
    _, orchestrator = local
    schemas = orchestrator.dataset_schemas(DEMO)
    declared = REPO / schemas["Summary_quality"]["source"]["path"]
    direct = pl.read_csv(declared, separator="\t", infer_schema=False)
    assert direct.height >= 40  # the example is not a stub (42 rows today)
    recipe = load_data_analysis_recipe(RECIPES_DIR / f"{DEMO}.yaml").raw
    for lf in (
        orchestrator.read_source(DEMO, "Summary_quality"),
        # tier 1 of Summary_quality has no step: its T1 is the file as the ingestion reads it
        orchestrator.prepare_ingredient("Summary_quality", schemas["Summary_quality"], DEMO, recipe=recipe),
    ):
        got = lf.collect()
        assert got.height == direct.height
        assert sorted(got["sample_id"].cast(pl.String).to_list()) == sorted(direct["sample_id"].to_list())


# --- priority: what exists today ---------------------------------------------------------------------------------

def _world(tmp_path: Path, *, with_path: bool = True, declared_exists: bool = True):
    """One table A, a recipe that names a file (or not), a raw_data folder, a deployment-like orchestrator."""
    raw = tmp_path / "raw"
    raw.mkdir()
    declared = tmp_path / "declared" / "a.tsv"
    declared.parent.mkdir()
    if declared_exists:
        declared.write_text("sample_id\tcountry\ns1\tNO\ns2\tSE\n")
    source = f"source: {{type: local_tsv, path: {declared}}}" if with_path else "source: {type: local_tsv}"
    recipes = tmp_path / "recipes"
    recipes.mkdir()
    (recipes / "proj.yaml").write_text(dedent(f"""
        id: proj
        data_engine: python-polars
        plot_engine: python-plotnine
        data_schemas:
          A:
            {source}
            null_values: []
            strip: false
            input_fields:
              sample_id: {{type: Categorical}}
              country: {{type: Categorical}}
            tier1:
              steps: []
        analysis_groups:
          g:
            ui_label: G
            plots:
              p:
                ui_label: P
                target_dataset: A
                mapping: {{x: country}}
                layers:
                  - name: geom_bar
        """))
    return recipes, raw, declared


def _orch(recipes, raw, **kw):
    return DataOrchestrator(recipes, raw, data_lookup="data_analysis_recipe_paths", **kw)


def _ids(orchestrator):
    return sorted(orchestrator.read_source("proj", "A").collect()["sample_id"].cast(pl.String).to_list())


def test_with_nothing_selected_the_recipe_path_is_read_and_a_file_of_the_same_name_in_raw_data_is_ignored(tmp_path):
    recipes, raw, declared = _world(tmp_path)
    (raw / "A.tsv").write_text("sample_id\tcountry\nx1\tDK\n")  # a decoy: another file of the same table name
    orchestrator = _orch(recipes, raw)
    assert Path(orchestrator.locate_dataset_file("proj", "A", orchestrator.dataset_schemas("proj")["A"])) == declared
    assert _ids(orchestrator) == ["s1", "s2"]


def test_a_file_replaced_by_data_import_is_the_file_read(tmp_path):
    """Data Import writes at `file_place`: the recipe's own path. Today that is the only way a user's file wins over the recipe's example."""
    recipes, raw, declared = _world(tmp_path)
    orchestrator = _orch(recipes, raw)
    schema = orchestrator.dataset_schemas("proj")["A"]
    place = Path(orchestrator.file_place("proj", "A", schema))
    assert place == declared
    place.write_text("sample_id\tcountry\nu1\tFI\n")
    assert _ids(orchestrator) == ["u1"]


def test_a_recipe_imported_from_a_bundle_reads_the_folder_of_its_import_not_its_path(tmp_path):
    recipes, raw, declared = _world(tmp_path)
    imports = tmp_path / "imports"
    (imports / "proj" / "data").mkdir(parents=True)
    (imports / "proj" / "data" / "A.tsv").write_text("sample_id\tcountry\nb1\tIS\n")
    orchestrator = _orch(recipes, raw, imports_dir=imports)
    assert _ids(orchestrator) == ["b1"]
    assert orchestrator.file_place("proj", "A", orchestrator.dataset_schemas("proj")["A"]) is None  # Data Import cannot replace it


# --- edge cases --------------------------------------------------------------------------------------------------

def test_a_table_with_no_source_path_is_found_by_its_id_in_raw_data(tmp_path):
    recipes, raw, _ = _world(tmp_path, with_path=False, declared_exists=False)
    (raw / "A.tsv").write_text("sample_id\tcountry\nr1\tSE\n")
    assert _ids(_orch(recipes, raw)) == ["r1"]


def test_a_declared_file_that_is_missing_is_never_replaced_by_a_file_of_the_same_table_name(tmp_path):
    recipes, raw, declared = _world(tmp_path, declared_exists=False)
    (raw / "A.tsv").write_text("sample_id\tcountry\nx1\tDK\n")  # the decoy that must NOT be read silently
    orchestrator = _orch(recipes, raw)
    schema = orchestrator.dataset_schemas("proj")["A"]
    assert orchestrator.locate_dataset_file("proj", "A", schema) is None
    assert "A" not in orchestrator.get_source_files("proj")
    with pytest.raises(IngestionError) as error:
        orchestrator.read_source("proj", "A")
    assert "A" in str(error.value) and declared.name in str(error.value)


def test_the_load_gate_rejects_a_recipe_whose_declared_file_is_missing_and_names_the_table_and_the_file(tmp_path):
    recipes, raw, declared = _world(tmp_path, declared_exists=False)
    (raw / "A.tsv").write_text("sample_id\tcountry\nx1\tDK\n")
    problems = validate_data_analysis_recipe_data(recipes / "proj.yaml", raw, data_lookup="data_analysis_recipe_paths")
    assert problems, "a recipe whose declared data file is missing passed the data check"
    text = " ".join(str(p) for p in problems)
    assert "A" in text and declared.name in text, text


def test_the_demo_recipe_in_the_shipped_folder_has_every_file_it_names(local):
    """The count the report quotes: tables with a declared path, over every shipped recipe, all exist."""
    _, orchestrator = local
    missing = []
    total = 0
    for path in SHIPPED:
        for table, schema in orchestrator.dataset_schemas(path.stem).items():
            declared = ((schema or {}).get("source") or {}).get("path")
            if declared:
                total += 1
                if not (REPO / declared).is_file():
                    missing.append(f"{path.stem}/{table}: {declared}")
    print(f"tables with a declared source.path: {total}")
    assert total > 0
    assert not missing, missing
