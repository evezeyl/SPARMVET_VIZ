"""Data Import check (HOME, Data Import panel): a file is accepted if and only if the engine's ingestion reads it (D-0034, DEC24, DEC25; D-0050).

Everything runs on copies under pytest's `tmp_path`; nothing is written into `config/` or `assets/`. The apply path is `apply_import` (the handler only wires it).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_data_import_check.py -q
"""
import contextlib
import io
import shutil
from pathlib import Path

import polars as pl
import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.data_import_check import Candidate, DataImportWriteError, apply_import, check_candidates, store_all
from app.modules.orchestrator import DataOrchestrator
from utils.errors import IngestionError

ROOT = Path(__file__).resolve().parents[2]
RECIPES_ROOT = ROOT / "config" / "data_analysis_recipes"

# T: headers in the file differ from the slugs (original_name); U: no original_name (the slug is the header); W: a recipe path whose file does not exist yet
RECIPE = """id: tiny
info: {{display_name: Tiny}}
data_engine: python-polars
plot_engine: python-plotnine
data_schemas:
  T:
    source: {{type: local_tsv, path: {t_path}}}
    null_values: []
    strip: false
    input_fields:
      sample_id: {{original_name: Sample ID, type: String, label: Sample, is_entity_key: true}}
      country: {{original_name: Country, type: String, label: Country}}
      year: {{original_name: Year, type: Int64, label: Year}}
    tier1: {{steps: []}}
  U:
    source: {{type: local_tsv, path: {u_path}}}
    null_values: []
    strip: false
    input_fields:
      id: {{type: String, label: Id, is_entity_key: true}}
      value: {{type: Float64, label: Value}}
    tier1: {{steps: []}}
  W:
    source: {{type: local_tsv, path: {w_path}}}
    null_values: []
    strip: false
    input_fields:
      id: {{type: String, label: Id, is_entity_key: true}}
    tier1: {{steps: []}}
analysis_groups:
  g:
    ui_label: G
    plots:
      p:
        ui_label: P
        target_dataset: T
        mapping: {{x: country}}
        layers:
          - name: geom_bar
            params: {{}}
"""

T_OWN = "Sample ID\tCountry\tYear\ns1\tNO\t2020\ns2\tSE\t2021\n"          # the recipe's own headers
T_SLUGS = "sample_id\tcountry\tyear\ns1\tNO\t2020\ns2\tSE\t2021\n"        # the slugs: not what the engine reads
U_OK = "id\tvalue\nu1\t1.5\nu2\t2.5\n"


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


class World:
    def __init__(self, root: Path, data_lookup: str = "data_analysis_recipe_paths", imported: bool = False):
        self.root = root
        self.recipes, self.raw, self.up = root / "recipes", root / "raw_data", root / "uploads"
        self.data = root / "data"
        for d in (self.recipes, self.raw, self.up, self.data):
            d.mkdir(parents=True, exist_ok=True)
        self.t, self.u = self.data / "T.tsv", self.data / "U.tsv"
        self.t.write_text(T_OWN)
        self.u.write_text(U_OK)
        (self.recipes / "tiny.yaml").write_text(RECIPE.format(t_path=self.t, u_path=self.u, w_path=self.data / 'W.tsv'))
        self.imports = root / "imports"
        if imported:
            (self.imports / "tiny" / "data").mkdir(parents=True)
            (self.imports / "tiny" / "data" / "T.tsv").write_text(T_OWN)
            (self.imports / "tiny" / "data" / "U.tsv").write_text(U_OK)
            (self.imports / "tiny" / "data" / "W.tsv").write_text("id\nw1\n")
        self.orch = DataOrchestrator(self.recipes, self.raw, data_lookup=data_lookup, imports_dir=self.imports)

    def upload(self, name: str, text: str | bytes, ds_id: str) -> Candidate:
        path = self.up / f"{len(list(self.up.iterdir()))}_{name}"
        path.write_bytes(text if isinstance(text, bytes) else text.encode())
        return Candidate(name=name, tmp_path=path, ds_id=ds_id)

    def read(self, ds_id: str) -> pl.DataFrame:
        with contextlib.redirect_stdout(io.StringIO()):
            return self.orch.read_source("tiny", ds_id).collect()


@pytest.fixture
def world(tmp_path):
    return World(tmp_path)


def run(world, *candidates):
    with contextlib.redirect_stdout(io.StringIO()):
        return apply_import(world.orch, "tiny", list(candidates))


# -- the format of the file is the engine's: the recipe's own headers ------------------------------------------------

def test_the_file_with_the_recipes_own_headers_is_accepted_and_the_engine_reads_what_was_written(world):
    new = "Sample ID\tCountry\tYear\ns9\tDK\t1999\n"
    out = run(world, world.upload("T.tsv", new, "T"))
    assert out.ok and out.written == [world.t]
    assert world.t.read_text() == new
    got = world.read("T")
    assert got.columns == ["sample_id", "country", "year"] and got["sample_id"].to_list() == ["s9"] and got["year"].to_list() == [1999]


def test_the_file_with_slug_headers_is_refused_with_the_ingestions_reason_and_nothing_is_written(world):
    before = world.t.read_bytes()
    out = run(world, world.upload("T.tsv", T_SLUGS, "T"))
    assert not out.ok and out.written == []
    error = out.verdicts[0].error
    assert "expected file headers" in error and "'Sample ID'" in error and "'Country'" in error and "'Year'" in error
    assert "Did you mean" not in error and "rename" not in error.lower().replace("original_name", "")
    assert world.t.read_bytes() == before


def test_what_the_check_refuses_the_engine_cannot_read_and_what_it_accepts_the_engine_reads(world):
    # the two definitions cannot differ: the check IS the ingestion's read
    from ingestion.ingestor import DataIngestor
    schema = world.orch.dataset_schemas("tiny")["T"]
    for text, accepted in ((T_OWN, True), (T_SLUGS, False)):
        cand = world.upload("T.tsv", text, "T")
        verdict = check_candidates(world.orch, "tiny", [cand])[0]
        engine_ok = True
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                DataIngestor(str(world.raw)).ingest("T", {**schema, "source": {"type": "local_tsv", "path": str(cand.tmp_path)}})[0].collect()
        except IngestionError:
            engine_ok = False
        assert verdict.ok is accepted is engine_ok


def test_a_dataset_without_original_name_is_read_by_its_slug(world):
    assert run(world, world.upload("U.tsv", "id\tvalue\nx\t9\n", "U")).ok
    assert world.read("U")["value"].to_list() == [9.0]
    out = run(world, world.upload("U.tsv", "Id\tValue\nx\t9\n", "U"))     # other case: exact match, as the ingestion
    assert not out.ok and "'id'" in out.verdicts[0].error


def test_a_value_that_does_not_fit_the_declared_type_names_the_column_and_the_value(world):
    before = world.t.read_bytes()
    out = run(world, world.upload("T.tsv", "Sample ID\tCountry\tYear\ns1\tNO\tabc\n", "T"))
    assert not out.ok
    assert "'year'" in out.verdicts[0].error and "'abc'" in out.verdicts[0].error
    assert world.t.read_bytes() == before


def test_a_declared_column_the_file_lacks_is_refused(world):
    out = run(world, world.upload("T.tsv", "Sample ID\tCountry\ns1\tNO\n", "T"))
    assert not out.ok and "'Year'" in out.verdicts[0].error


def test_an_undeclared_extra_column_is_accepted_as_the_ingestion_does_and_is_not_imported(world):
    out = run(world, world.upload("T.tsv", "Sample ID\tCountry\tYear\tnotes\ns1\tNO\t2020\thello\n", "T"))
    assert out.ok
    assert world.read("T").columns == ["sample_id", "country", "year"]


def test_an_empty_file_is_refused_with_a_plain_reason(world):
    before = world.t.read_bytes()
    out = run(world, world.upload("T.tsv", b"", "T"))
    assert not out.ok and "Failed to read 'T.tsv'" in out.verdicts[0].error
    assert world.t.read_bytes() == before


def test_a_tsv_whose_content_is_comma_separated_is_refused_by_the_ingestions_reason(world):
    out = run(world, world.upload("T.tsv", "Sample ID,Country,Year\ns1,NO,2020\n", "T"))
    assert not out.ok and "expected file headers" in out.verdicts[0].error


# -- formats the stored path cannot hold ------------------------------------------------------------------------------

@pytest.mark.parametrize("name,words", [("T.csv", "comma-separated"), ("T.xlsx", "Excel"), ("T.xls", "Excel"), ("T.parquet", "Parquet"), ("T.txt", "not a file type")])
def test_a_file_the_stored_tsv_cannot_hold_is_refused_with_why_and_what_to_do(world, name, words):
    before = world.t.read_bytes()
    out = run(world, world.upload(name, T_OWN.replace("\t", ",") if name.endswith("csv") else T_OWN, "T"))
    assert not out.ok and out.written == []
    reason, _, way_out = out.verdicts[0].error.partition(" — ")
    assert words in reason and "tab-separated" in (reason + way_out)
    assert world.t.read_bytes() == before


def test_a_csv_with_the_recipes_own_headers_is_refused_not_copied_raw_over_the_tsv(world):
    before = world.t.read_bytes()
    out = run(world, world.upload("T.csv", "Sample ID,Country,Year\ns1,NO,2020\n", "T"))
    assert not out.ok and "Convert it to a tab-separated file" in out.verdicts[0].error
    assert world.t.read_bytes() == before
    assert world.read("T").height == 2      # the recipe still builds


def test_a_tsv_cannot_replace_a_parquet_dataset_and_the_reverse(tmp_path):
    w = World(tmp_path, data_lookup="by_dataset_id")
    pl.DataFrame({"id": ["a"]}).write_parquet(w.raw / "W.parquet")
    out = run(w, w.upload("W.tsv", "id\nz\n", "W"))
    assert not out.ok and "Parquet" in out.verdicts[0].error
    assert w.raw.joinpath("W.parquet").exists() and not w.raw.joinpath("W.tsv").exists()


def test_a_parquet_file_replaces_a_parquet_dataset_and_the_engine_reads_it(tmp_path):
    w = World(tmp_path, data_lookup="by_dataset_id")
    pl.DataFrame({"id": ["a"]}).write_parquet(w.raw / "W.parquet")
    new = w.up / "new.parquet"
    pl.DataFrame({"id": ["z1", "z2"]}).write_parquet(new)
    out = run(w, Candidate("W.parquet", new, "W"))
    assert out.ok and out.written == [w.raw / "W.parquet"]
    assert w.read("W")["id"].to_list() == ["z1", "z2"]
    refused = run(w, Candidate("W.parquet", new, "U"))
    assert not refused.ok and "Parquet file" in refused.verdicts[0].error


# -- all files of one Apply: nothing is written unless every one passes -----------------------------------------------

def test_when_the_second_file_fails_the_first_is_not_written(world):
    t_before, u_before = world.t.read_bytes(), world.u.read_bytes()
    good = world.upload("T.tsv", "Sample ID\tCountry\tYear\nnew\tDK\t1\n", "T")
    bad = world.upload("U.tsv", "id\tvalue\nx\tnot_a_number\n", "U")
    out = run(world, good, bad)
    assert not out.ok and out.written == []
    assert out.verdicts[0].ok and not out.verdicts[1].ok          # each file gets its own verdict
    assert "'value'" in out.verdicts[1].error
    assert world.t.read_bytes() == t_before and world.u.read_bytes() == u_before


def test_all_good_files_are_written_together(world):
    out = run(world, world.upload("T.tsv", "Sample ID\tCountry\tYear\nnew\tDK\t1\n", "T"), world.upload("U.tsv", "id\tvalue\nq\t3\n", "U"))
    assert out.ok and sorted(out.written) == sorted([world.t, world.u])
    assert world.read("T")["sample_id"].to_list() == ["new"] and world.read("U")["id"].to_list() == ["q"]
    assert not list(world.data.glob("*.import-tmp"))


def test_two_files_for_one_dataset_are_both_refused(world):
    before = world.t.read_bytes()
    out = run(world, world.upload("a.tsv", T_OWN, "T"), world.upload("b.tsv", T_OWN, "T"))
    assert not out.ok and all("More than one" in v.error for v in out.verdicts)
    assert world.t.read_bytes() == before


def test_no_dataset_chosen_and_a_dataset_the_recipe_lacks_are_refused(world):
    out = run(world, world.upload("a.tsv", T_OWN, ""), world.upload("b.tsv", T_OWN, "Nope"))
    assert "No dataset selected" in out.verdicts[0].error and "no dataset 'Nope'" in out.verdicts[1].error and out.written == []


def test_a_recipe_that_cannot_be_loaded_refuses_every_file_with_its_reason(world):
    (world.recipes / "tiny.yaml").write_text("id: tiny\ndata_schemas:\n  T: {}\n")
    before = world.t.read_bytes()
    out = run(world, world.upload("T.tsv", T_OWN, "T"))
    assert not out.ok and out.written == [] and "cannot load" in out.verdicts[0].error
    assert world.t.read_bytes() == before


def test_nothing_to_import_writes_nothing(world):
    assert run(world).written == [] and run(world).ok


def test_a_file_that_cannot_be_staged_leaves_every_dataset_as_it_was(world):
    (world.root / "blocker").write_text("a file where a folder must be")
    t_before = world.t.read_bytes()
    good_t = world.upload("T.tsv", "Sample ID\tCountry\tYear\nnew\tDK\t1\n", "T")
    verdicts = check_candidates(world.orch, "tiny", [good_t, world.upload("U.tsv", U_OK, "U")])
    assert all(v.ok for v in verdicts)
    from dataclasses import replace
    verdicts[1] = replace(verdicts[1], target=world.root / "blocker" / "U.tsv")      # its place cannot be created
    with pytest.raises(DataImportWriteError, match="Nothing was imported"):
        store_all(verdicts)
    assert world.t.read_bytes() == t_before and not list(world.data.glob("*.import-tmp"))


def test_store_all_refuses_a_refused_verdict(world):
    verdicts = check_candidates(world.orch, "tiny", [world.upload("T.tsv", T_SLUGS, "T")])
    with pytest.raises(ValueError):
        store_all(verdicts)


# -- the place is the one the orchestrator reads ----------------------------------------------------------------------

def test_a_recipe_imported_from_a_bundle_is_refused_and_nothing_changes(tmp_path):
    w = World(tmp_path, imported=True)
    folder_before = {p.name: p.read_bytes() for p in (w.imports / "tiny" / "data").iterdir()}
    src_before = w.t.read_bytes()
    out = run(w, w.upload("T.tsv", "Sample ID\tCountry\tYear\nnew\tDK\t1\n", "T"))
    assert not out.ok and out.written == []
    reason, _, way_out = out.verdicts[0].error.partition(" — ")
    assert "imported from a bundle" in reason and "cannot replace it here" in reason and str(w.imports / "tiny" / "data") in reason
    assert {p.name: p.read_bytes() for p in (w.imports / "tiny" / "data").iterdir()} == folder_before
    assert w.t.read_bytes() == src_before


def test_by_dataset_id_writes_the_file_the_orchestrator_reads_not_the_recipes_path(tmp_path):
    w = World(tmp_path, data_lookup="by_dataset_id")
    (w.raw / "T.tsv").write_text(T_OWN)
    src_before = w.t.read_bytes()
    new = "Sample ID\tCountry\tYear\nnew\tDK\t1\n"
    out = run(w, w.upload("T.tsv", new, "T"))
    assert out.ok and out.written == [w.raw / "T.tsv"]
    assert w.t.read_bytes() == src_before                      # the recipe's own path is not what the engine reads here
    assert w.read("T")["sample_id"].to_list() == ["new"]       # what was written is what is read
    assert w.orch.get_source_files("tiny")["T"] == w.raw / "T.tsv"


def test_by_dataset_id_with_no_file_yet_writes_it_where_the_orchestrator_will_look(tmp_path):
    w = World(tmp_path, data_lookup="by_dataset_id")
    out = run(w, w.upload("T.tsv", "Sample ID\tCountry\tYear\nnew\tDK\t1\n", "T"))
    assert out.ok and out.written == [w.raw / "T.tsv"]
    assert w.read("T")["sample_id"].to_list() == ["new"]


def test_a_dataset_with_two_files_by_id_is_refused_with_the_orchestrators_reason(tmp_path):
    w = World(tmp_path, data_lookup="by_dataset_id")
    (w.raw / "T.tsv").write_text(T_OWN)
    pl.DataFrame({"x": [1]}).write_parquet(w.raw / "T.parquet")
    out = run(w, w.upload("T.tsv", T_OWN, "T"))
    assert not out.ok and "more than one file" in out.verdicts[0].error


def test_a_recipe_path_whose_file_is_missing_is_created_where_the_recipe_reads_it(world):
    out = run(world, world.upload("W.tsv", "id\nw9\n", "W"))
    assert out.ok and out.written == [world.data / "W.tsv"] and world.read("W")["id"].to_list() == ["w9"]
    world.t.unlink()
    out = run(world, world.upload("T.tsv", T_OWN, "T"))
    assert out.ok and out.written == [world.t] and world.read("T").height == 2


def test_the_place_follows_the_orchestrator_for_every_dataset(world):
    for ds_id, schema in world.orch.dataset_schemas("tiny").items():
        place = world.orch.file_place("tiny", ds_id, schema)
        assert place == (world.orch.locate_dataset_file("tiny", ds_id, schema) or place)


# -- Data Import and the ingestor together, on every shipped recipe ---------------------------------------------------

def _shipped_datasets():
    found = []
    for recipe in sorted(RECIPES_ROOT.rglob("*.yaml")):
        if recipe.parent.name not in ("pipelines", "templates", "retest", "experimental"):
            continue
        found.append(recipe)
    return found


def test_the_recipes_own_data_file_is_accepted_for_every_shipped_recipe_whose_data_exists(tmp_path):
    checked = 0
    for recipe in _shipped_datasets():
        orch = DataOrchestrator(recipe.parent, ROOT / "assets" / "test_data")
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                schemas = orch.dataset_schemas(recipe.stem)
            except Exception:
                continue          # a retest or experimental recipe that does not load is not the subject here
            for ds_id, schema in schemas.items():
                located = orch.locate_dataset_file(recipe.stem, ds_id, schema)
                if located is None:
                    continue
                try:
                    with contextlib.redirect_stdout(io.StringIO()):
                        orch.read_source(recipe.stem, ds_id).collect()
                except Exception:
                    continue      # the engine itself cannot read it (a recipe made to fail): nothing to compare with
                copy = tmp_path / f"{recipe.stem}__{ds_id}{located.suffix}"
                shutil.copyfile(located, copy)
                verdict = check_candidates(orch, recipe.stem, [Candidate(located.name, copy, ds_id)])[0]
                assert verdict.ok, f"{recipe.stem}/{ds_id}: the engine reads {located}, Data Import refused it: {verdict.error}"
                assert verdict.target == located
                checked += 1
    assert checked >= 20, f"only {checked} dataset files were compared: the shipped data moved?"
