"""Data Import check (HOME, Data Import panel): a file is accepted when its name has the format of the stored file and the engine's ingestion reads ALL of it,
for every table of the recipe that reads that file (D-0034, DEC24, DEC25; D-0050).

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
from app.modules import data_import_check
from app.modules.data_import_check import (BY_DATASET_ID_REFUSAL, Candidate, DataImportWriteError, apply_import, check_candidates,
                                           refresh_replaced, store_all)
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
      sample_id: {{original_name: Sample ID, type: String, label: Sample, is_entity_id: true}}
      country: {{original_name: Country, type: String, label: Country}}
      year: {{original_name: Year, type: Int64, label: Year}}
    tier1: {{steps: []}}
  U:
    source: {{type: local_tsv, path: {u_path}}}
    null_values: []
    strip: false
    input_fields:
      id: {{type: String, label: Id, is_entity_id: true}}
      value: {{type: Float64, label: Value}}
    tier1: {{steps: []}}
  W:
    source: {{type: {w_type}, path: {w_path}}}
    null_values: []
    strip: false
    input_fields:
      id: {{type: String, label: Id, is_entity_id: true}}
    tier1: {{steps: []}}
{extra}analysis_groups:
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
U_OK_INT = "id\tvalue\nu1\t1\nu2\t2\n"        # the file of U in a recipe where S (Int64) shares it

# S shares the data file of U and declares `value` as Int64: a file with decimals is readable for U and not for S
SHARED = """  S:
    source: {{type: local_tsv, path: {u_path}}}
    null_values: []
    strip: false
    input_fields:
      id: {{type: String, label: Id}}
      value: {{type: Int64, label: Value}}
    tier1: {{steps: []}}
"""


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


class World:
    def __init__(self, root: Path, data_lookup: str = "data_analysis_recipe_paths", imported: bool = False, w_parquet: bool = False, shared: bool = False):
        self.root = root
        self.recipes, self.raw, self.up = root / "recipes", root / "raw_data", root / "uploads"
        self.data = root / "data"
        for d in (self.recipes, self.raw, self.up, self.data):
            d.mkdir(parents=True, exist_ok=True)
        self.t, self.u = self.data / "T.tsv", self.data / "U.tsv"
        self.t.write_text(T_OWN)
        self.u.write_text(U_OK_INT if shared else U_OK)
        self.w = self.data / ("W.parquet" if w_parquet else "W.tsv")
        if w_parquet:
            pl.DataFrame({"id": ["a"]}).write_parquet(self.w)
        extra = SHARED.format(u_path=self.u) if shared else ""
        (self.recipes / "tiny.yaml").write_text(RECIPE.format(t_path=self.t, u_path=self.u, w_path=self.w,
                                                              w_type="local_parquet" if w_parquet else "local_tsv", extra=extra))
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
    error = out.verdicts[0].error
    assert not out.ok and "'T.tsv' is empty" in error and "NoDataError" not in error and "Failed to read" not in error
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
    w = World(tmp_path, w_parquet=True)
    out = run(w, w.upload("W.tsv", "id\nz\n", "W"))
    assert not out.ok and "Parquet" in out.verdicts[0].error
    assert w.w.exists() and not (w.data / "W.tsv").exists()


def test_a_parquet_file_replaces_a_parquet_dataset_and_the_engine_reads_it(tmp_path):
    w = World(tmp_path, w_parquet=True)
    new = w.up / "new.parquet"
    pl.DataFrame({"id": ["z1", "z2"]}).write_parquet(new)
    out = run(w, Candidate("W.parquet", new, "W"))
    assert out.ok and out.written == [w.w]
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


def test_a_deployment_that_finds_its_data_by_table_name_is_refused_and_the_real_file_is_unchanged(tmp_path):
    w = World(tmp_path, data_lookup="by_dataset_id")
    (w.raw / "T.tsv").write_text(T_OWN)
    real, src = (w.raw / "T.tsv").read_bytes(), w.t.read_bytes()
    out = run(w, w.upload("T.tsv", "Sample ID\tCountry\tYear\nnew\tDK\t1\n", "T"))
    assert not out.ok and out.written == [] and out.tables_written == []
    reason, _, way_out = out.verdicts[0].error.partition(" — ")
    assert reason == BY_DATASET_ID_REFUSAL and "delivered by the pipeline" in reason and way_out
    assert not any(word in out.verdicts[0].error for word in ("by_dataset_id", "original_name", "slug"))
    assert (w.raw / "T.tsv").read_bytes() == real and w.t.read_bytes() == src      # neither the real file nor the recipe's path is written
    assert not list(w.raw.glob("*.import-tmp")) and not list(w.data.glob("*.import-tmp"))


def test_a_deployment_by_table_name_with_no_file_yet_is_refused_too(tmp_path):
    w = World(tmp_path, data_lookup="by_dataset_id")
    out = run(w, w.upload("W.tsv", "id\nw\n", "W"))
    assert not out.ok and BY_DATASET_ID_REFUSAL in out.verdicts[0].error and not list(w.raw.iterdir())


def test_the_refusal_by_table_name_holds_with_a_good_file_and_a_second_good_file_is_not_written(tmp_path):
    w = World(tmp_path, data_lookup="by_dataset_id")
    before = w.u.read_bytes()
    out = run(w, w.upload("U.tsv", "id\tvalue\nq\t3\n", "U"), w.upload("T.tsv", T_OWN, "T"))
    assert not out.ok and all(BY_DATASET_ID_REFUSAL in v.error for v in out.verdicts) and w.u.read_bytes() == before


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


# -- the whole file is read: what the engine fails on at the next build is refused here (D-0050) ----------------------

DAMAGED = [
    ("a row with one field too many, String-only dataset", "W", b"id\nw1\nw2\textra\n"),
    ("a row with one field too many, typed dataset", "T", b"Sample ID\tCountry\tYear\ns1\tNO\t2020\ns2\tSE\t2021\textra\n"),
    ("a byte that is not UTF-8, String-only dataset", "W", b"id\nw\xff\n"),
    ("a byte that is not UTF-8 in a String column of a typed dataset", "T", b"Sample ID\tCountry\tYear\ns1\tN\xffO\t2020\n"),
    ("a byte that is not UTF-8 in a column the recipe does not declare", "T", b"Sample ID\tCountry\tYear\tnotes\ns1\tNO\t2020\tz\xff\n"),
    ("a quote that is never closed, String-only dataset", "W", b'id\n"abc\nw2\n'),
    ("a quote that is never closed, typed dataset", "T", b'Sample ID\tCountry\tYear\n"s1\tNO\t2020\ns2\tSE\t2021\n'),
]


@pytest.mark.parametrize("label,ds_id,content", DAMAGED, ids=[d[0] for d in DAMAGED])
def test_a_file_the_engine_cannot_read_in_full_is_refused_and_the_old_file_is_unchanged(tmp_path, label, ds_id, content):
    w = World(tmp_path / "check")
    w.w.write_text("id\nold\n")
    place = {"T": w.t, "W": w.w}[ds_id]
    before = place.read_bytes()
    out = run(w, w.upload(f"{ds_id}.tsv", content, ds_id))
    error = out.verdicts[0].error
    assert not out.ok and out.written == [] and out.tables_written == []
    assert "cannot be read in full" in error and "ComputeError" not in error and "Failed to read" not in error
    assert place.read_bytes() == before and not list(w.data.glob("*.import-tmp"))
    # the same bytes at the place of the data file: the engine fails too, so the refusal is not stricter than the build
    e = World(tmp_path / "engine")
    {"T": e.t, "W": e.w}[ds_id].write_bytes(content)
    with pytest.raises(Exception):
        e.read(ds_id)


READABLE = [
    ("CRLF line ends", "T", b"Sample ID\tCountry\tYear\r\ns1\tNO\t2020\r\n"),
    ("a quoted field with a tab and a doubled quote", "T", b'Sample ID\tCountry\tYear\n"s\t1"\t"N""O"\t2020\n'),
    ("blank trailing lines", "T", b"Sample ID\tCountry\tYear\ns1\tNO\t2020\n\n\n"),
    ("a header and no rows", "T", b"Sample ID\tCountry\tYear\n"),
    ("a byte order mark on a String-only dataset", "W", b"\xef\xbb\xbfid\nw1\n"),
    ("an undeclared column that holds anything readable", "T", b"Sample ID\tCountry\tYear\tnotes\ns1\tNO\t2020\t\xc3\xa9\n"),
]


@pytest.mark.parametrize("label,ds_id,content", READABLE, ids=[d[0] for d in READABLE])
def test_a_file_that_looks_odd_but_the_engine_reads_is_accepted(tmp_path, label, ds_id, content):
    e = World(tmp_path / "engine")
    {"T": e.t, "W": e.w}[ds_id].write_bytes(content)
    engine = e.read(ds_id)                                    # the engine reads it
    w = World(tmp_path / "check")
    out = run(w, w.upload(f"{ds_id}.tsv", content, ds_id))
    assert out.ok and len(out.written) == 1
    assert w.read(ds_id).equals(engine)


# -- a file that is the data of more than one table -------------------------------------------------------------------

def test_a_file_shared_by_two_tables_is_checked_against_both_and_both_are_named_when_it_is_accepted(tmp_path):
    w = World(tmp_path, shared=True)
    out = run(w, w.upload("U.tsv", "id\tvalue\nq\t3\n", "U"))
    assert out.ok and out.verdicts[0].shared == ("S",) and out.verdicts[0].tables == ("U", "S")
    assert out.written == [w.u] and out.tables_written == ["U", "S"]
    assert w.read("U")["id"].to_list() == ["q"] and w.read("S")["value"].to_list() == [3]


def test_a_file_the_other_table_cannot_read_is_refused_naming_that_table_and_nothing_is_written(tmp_path):
    w = World(tmp_path, shared=True)
    before = w.u.read_bytes()
    out = run(w, w.upload("U.tsv", "id\tvalue\nq\t1.5\n", "U"))       # U declares Float64 and reads it; S declares Int64 and does not
    assert not out.ok and out.written == [] and out.tables_written == []
    error = out.verdicts[0].error
    assert "'S'" in error and "cannot read it" in error and "'value'" in error and "'1.5'" in error
    assert w.u.read_bytes() == before and w.read("S").height == 2


def test_the_same_file_uploaded_for_a_table_that_shares_it_is_checked_against_the_assigned_table_too(tmp_path):
    w = World(tmp_path, shared=True)
    out = run(w, w.upload("U.tsv", "id\tvalue\nq\t1.5\n", "S"))       # assigned to S: S refuses it itself
    assert not out.ok and "'value'" in out.verdicts[0].error and w.read("U").height == 2


def test_two_files_assigned_to_two_tables_that_share_one_file_are_both_refused(tmp_path):
    w = World(tmp_path, shared=True)
    before = w.u.read_bytes()
    out = run(w, w.upload("a.tsv", "id\tvalue\nq\t3\n", "U"), w.upload("b.tsv", "id\tvalue\nr\t4\n", "S"))
    assert not out.ok and out.written == []
    for v in out.verdicts:
        assert "same data file" in v.error and "'S'" in v.error and "'U'" in v.error
    assert w.u.read_bytes() == before


def test_two_files_for_two_tables_that_do_not_share_a_file_are_not_refused_for_sharing(tmp_path):
    w = World(tmp_path, shared=True)
    out = run(w, w.upload("T.tsv", T_OWN, "T"), w.upload("U.tsv", "id\tvalue\nq\t3\n", "U"))
    assert out.ok and out.tables_written == ["T", "U", "S"]


def test_in_the_demo_recipe_the_own_file_of_summary_is_accepted_and_names_summary_quality(tmp_path):
    recipe = "1_test_data_ST22_dummy"
    orch = DataOrchestrator(RECIPES_ROOT / "pipelines", ROOT / "assets" / "test_data")
    schemas = orch.dataset_schemas(recipe)
    located = orch.locate_dataset_file(recipe, "Summary", schemas["Summary"])
    assert located == orch.locate_dataset_file(recipe, "Summary_quality", schemas["Summary_quality"])      # one file, two tables
    copy = tmp_path / "copy.tsv"
    shutil.copyfile(located, copy)
    with contextlib.redirect_stdout(io.StringIO()):
        verdict = check_candidates(orch, recipe, [Candidate(located.name, copy, "Summary")])[0]
    assert verdict.ok and verdict.tables == ("Summary", "Summary_quality") and verdict.target == located


# -- writing: a failure leaves nothing partial and refreshes what was replaced --------------------------------------

def test_a_copy_that_fails_midway_leaves_no_partial_file_and_every_dataset_as_it_was(world, monkeypatch):
    t_before, u_before = world.t.read_bytes(), world.u.read_bytes()
    verdicts = check_candidates(world.orch, "tiny", [world.upload("T.tsv", "Sample ID\tCountry\tYear\nnew\tDK\t1\n", "T"), world.upload("U.tsv", "id\tvalue\nq\t3\n", "U")])
    assert all(v.ok for v in verdicts)
    real_copy, calls = shutil.copyfile, []

    def dies_midway(src, dst):
        calls.append(dst)
        if len(calls) == 2:
            Path(dst).write_bytes(b"half a fi")          # a partial file is on disk when the copy fails
            raise OSError("disk full")
        return real_copy(src, dst)

    monkeypatch.setattr(data_import_check.shutil, "copyfile", dies_midway)
    with pytest.raises(DataImportWriteError, match="Nothing was imported") as err:
        store_all(verdicts)
    assert err.value.replaced == []
    assert not list(world.data.glob("*.import-tmp"))
    assert world.t.read_bytes() == t_before and world.u.read_bytes() == u_before


def test_when_a_later_replace_fails_the_first_stays_replaced_is_named_and_is_refreshed(world, monkeypatch, tmp_path):
    t_before, u_before = world.t.read_bytes(), world.u.read_bytes()
    real_replace, calls = data_import_check.os.replace, []

    def second_fails(src, dst):
        calls.append(dst)
        if len(calls) == 2:
            raise OSError("permission denied")
        return real_replace(src, dst)

    monkeypatch.setattr(data_import_check.os, "replace", second_fails)
    new_t = "Sample ID\tCountry\tYear\nnew\tDK\t1\n"
    out = run(world, world.upload("T.tsv", new_t, "T"), world.upload("U.tsv", "id\tvalue\nq\t3\n", "U"))
    assert out.ok                                                  # both were accepted by the check; the write of the second failed
    assert out.written == [world.t] and out.tables_written == ["T"]
    assert str(world.t) in out.write_error and "Files already replaced" in out.write_error and "permission denied" in out.write_error
    assert world.t.read_text() == new_t and world.u.read_bytes() == u_before
    assert not list(world.data.glob("*.import-tmp"))
    # what was replaced is refreshed, what was not is left alone
    anchors = tmp_path / "anchors"
    anchors.mkdir()
    (anchors / "T.parquet").write_bytes(b"x")
    (anchors / "U.parquet").write_bytes(b"x")
    dropped = []
    assert refresh_replaced(out, "tiny", anchors, lambda *args: dropped.append(args)) is True
    assert not (anchors / "T.parquet").exists() and (anchors / "U.parquet").exists()
    assert dropped == [("tiny", "T", "anchor", "lf", None)]
    assert t_before != world.t.read_bytes()


def test_refresh_replaced_refreshes_every_table_of_a_shared_file_and_nothing_when_nothing_was_written(tmp_path):
    w = World(tmp_path / "w", shared=True)
    out = run(w, w.upload("U.tsv", "id\tvalue\nq\t3\n", "U"))
    anchors = tmp_path / "anchors"
    anchors.mkdir()
    for name in ("U", "S", "T"):
        (anchors / f"{name}.parquet").write_bytes(b"x")
    seen = []
    assert refresh_replaced(out, "tiny", anchors, lambda r, d, *rest: seen.append(d)) is True
    assert seen == ["U", "S"] and (anchors / "T.parquet").exists() and not (anchors / "U.parquet").exists() and not (anchors / "S.parquet").exists()
    refused = run(w, w.upload("U.tsv", "id\tvalue\nq\tnot a number\n", "U"))
    assert refresh_replaced(refused, "tiny", anchors, lambda *a: seen.append("never")) is False and "never" not in seen


# -- the words a HOME user reads ----------------------------------------------------------------------------------------

def test_the_headers_refusal_tells_the_user_to_correct_the_headers_of_the_file_not_the_recipe(world):
    out = run(world, world.upload("T.tsv", T_SLUGS, "T"))
    error = out.verdicts[0].error
    first, _, way_out = error.partition(" — ")
    assert "'Sample ID'" in first and "'Country'" in first and "'Year'" in first              # which headers are expected
    assert "Correct the column headers of the file" in way_out
    for word in ("original_name", "slug", "remove the declaration", "input_fields"):
        assert word not in way_out


def test_the_other_refusals_keep_the_ingestions_own_way_out(world):
    out = run(world, world.upload("T.tsv", "Sample ID\tCountry\tYear\ns1\tNO\tabc\n", "T"))
    assert "Suggestion" in out.verdicts[0].error
