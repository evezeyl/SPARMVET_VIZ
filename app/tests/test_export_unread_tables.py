"""The export writes a data file for every table of the recipe, also a table that no plot reads (D-0457).

D-0457 (her words): "Must be and yes must be viewabøenin the data preview"; earlier the same evening: "maybe export should export all the
tables if there are included in a recipe even if no plot". The real export generator is run headless (as `test_export_download_path.py`
runs it) on a small recipe with tables that no plot reads: a source nobody links (`U`), a source only a join reads (`T`, `V`) and a join no
plot reads (`D`). Only tier 1 can exist for such a table: the recipe check refuses tier-2 steps on a table or join no plot reads (S07 and
J14, `app/tests/test_schema_tier2.py`), so the export writes `<table>/T1_data.tsv` for it.

PROVISIONAL (not decided, D-0457 reading to be confirmed): "a table of the recipe" is read as every source table and every join, so a
source that a join reads also gets its file; the export has no scope any more (D-0292), so this holds for every export. The wording of
the sentences added to README.txt and report.qmd is PROVISIONAL.

Mutation index (grep "MUTATION"; each seen failing):
  MUTATION U1  the export writes no file for a table no plot reads (the new loop is skipped)
  MUTATION U2  the new tables are built without the keys of the export (`keys=None`), so the key check does not hold for them
  MUTATION U3  a table that cannot be loaded is skipped without a trace (no *_ERROR.txt)

# @deps
# consumes: app/handlers/export_handlers.py (export_bundle_download, tables_no_plot_reads), app/tests/test_export_download_path.py
# doc: .claude/rules/ui_implementation_contract.md#72
# @end_deps

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_export_unread_tables.py -q
"""
import io
import re
import zipfile
from types import SimpleNamespace

import polars as pl
import pytest

from app.handlers.export_handlers import tables_no_plot_reads
from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe
from app.tests.audit_export_harness import FLAGS, audit_kwargs
from app.tests.audit_nodes import filter_nodes
from app.tests.test_cache_chain import World, bump
from app.tests.test_export_download_path import _download_function, _run


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def _source(name: str, field: str, ftype: str = "String", file: str | None = None, entity: bool = True) -> str:
    """A source table whose data file is `data/<file or name>.tsv` (`DATA/` is replaced by the data folder of the world). `entity=False`: the table declares no entity id, so it
    takes no part in the completion of the ids (a look-up)."""
    plain = name.strip("'")
    marker = re.sub(r"\W", lambda m: f"_{ord(m.group()):02x}_", plain)   # one marker per table, whatever the characters of its id (two tables never share one, E06)
    completion = f"    completion: {{marker: {marker}_not_in_original_data, meaning: no result for this entity}}\n" if entity else ""
    entity_mark = ", is_entity_id: true" if entity else ""
    return f"""  {name}:
    source: {{type: local_tsv, path: DATA/{file or plain}.tsv}}
    null_values: []
    strip: false
{completion}    input_fields:
      sample_id: {{original_name: sample_id, type: Categorical, ui_label: Sample{entity_mark}}}
      {field}: {{original_name: {field}, type: {ftype}, ui_label: {field}}}
    tier1: {{steps: []}}
"""


class Wide(World):
    """T (read by the join C, plotted), U (linked to nothing), V (read by the join D) and D (a join no plot reads). One plot reads C."""

    extra_sources = ""
    plot_target = "C"

    def write_data_analysis_recipe(self, **_ignored) -> None:
        for name, text in {"U": "sample_id\tweight\nu1\t1.5\nu2\t2.5\nu3\t3.5\n", "V": "sample_id\tcolor\nv1\tred\nv2\tblue\n"}.items():
            (self.data_dir / f"{name}.tsv").write_text(text)
        entry = self.data_analysis_recipes_dir / "tiny.yaml"
        entry.write_text(("""id: tiny
info: {ui_label: Tiny}
data_engine: python-polars
plot_engine: python-plotnine
data_schemas:
""" + _source("T", "group")
                          + _source("U", "weight", "Float64") + _source("V", "color") + self.extra_sources
                          + f"""joins:
  C:
    ingredients:
      - dataset_id: T
    tier1: {{steps: []}}
  D:
    ingredients:
      - dataset_id: V
    tier1: {{steps: []}}
analysis_groups:
  g:
    ui_label: G
    plots:
      p:
        ui_label: P
        target_dataset: {self.plot_target}
        mapping: {{x: group}}
        layers:
          - name: geom_bar
            params: {{}}
""").replace("DATA/", str(self.data_dir) + "/"))
        bump(entry)


def _export(world, monkeypatch, notes=None, **kw):
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    return _run(_download_function(world, view, [] if notes is None else notes, monkeypatch, **kw)), view


def _zip(yielded) -> zipfile.ZipFile:
    assert len(yielded) == 1
    return zipfile.ZipFile(io.BytesIO(yielded[0]))


def _members(z: zipfile.ZipFile) -> dict:
    """{name without the first folder (it holds the time of the export): bytes}"""
    return {n.split("/", 1)[-1]: z.read(n) for n in z.namelist()}


def _table_tsv(world, table: str, tmp_path) -> bytes:
    """What `materialize_tier1` gives for the table, read independently of the export, as the TSV the export writes."""
    keys = world.orch.compute_data_analysis_recipe_keys("tiny")
    lf = world.orch.materialize_tier1("tiny", table, tmp_path / "scratch" / f"{table}.parquet", keys=keys)
    return lf.collect().write_csv(separator="\t").encode()


# -- which tables ---------------------------------------------------------------------------

def test_the_tables_no_plot_reads_are_every_source_and_join_that_no_plot_targets(tmp_path):
    world = Wide(tmp_path)
    raw = load_data_analysis_recipe(world.data_analysis_recipes_dir / "tiny.yaml").raw
    assert tables_no_plot_reads(raw) == ["T", "U", "V", "D"], "sources in the order of the recipe, then the joins; C is plotted"


def test_a_recipe_where_every_table_is_plotted_has_none(tmp_path):
    world = Wide(tmp_path)
    recipe = world.data_analysis_recipes_dir / "tiny.yaml"
    raw = load_data_analysis_recipe(recipe).raw
    raw_plots = {"T": "x", "U": "x", "V": "x", "C": "x", "D": "x"}
    raw["analysis_groups"]["g"]["plots"] = {f"p_{t}": {"ui_label": t, "target_dataset": t, "mapping": {"x": c}} for t, c in raw_plots.items()}
    assert tables_no_plot_reads(raw) == []


def test_a_recipe_with_no_joins_and_no_schemas_has_none():
    assert tables_no_plot_reads({"analysis_groups": {}}) == []


# -- what the bundle holds ----------------------------------------------------------------

def test_the_bundle_holds_a_tier1_file_for_each_table_no_plot_reads(tmp_path, monkeypatch):
    """MUTATION U1 fails here. Each file has the rows and columns of `materialize_tier1` for that table, byte for byte."""
    world = Wide(tmp_path)
    yielded, _ = _export(world, monkeypatch)
    members = _members(_zip(yielded))
    assert "EXPORT_NOT_CREATED.txt" not in members
    for table in ("T", "U", "V", "D"):
        assert members[f"{table}/T1_data.tsv"] == _table_tsv(world, table, tmp_path), table
    # U keeps its three lines as they are and gets one marked line for each id of the other tables (the completion of the ids): the lines of T (s1, s2, s3) and of V (v1, v2)
    assert members["U/T1_data.tsv"].decode().splitlines() == [
        "sample_id\tweight\tU_not_in_original_data", "u1\t1.5\tfalse", "u2\t2.5\tfalse", "u3\t3.5\tfalse",
        "s1\t\ttrue", "s2\t\ttrue", "s3\t\ttrue", "v1\t\ttrue", "v2\t\ttrue"]
    assert not [n for n in members if n.startswith(("T/", "U/", "V/", "D/")) and n != f"{n.split('/')[0]}/T1_data.tsv"], \
        "tier 1 only: no T2 or T3 file, no plot folder, for a table no plot reads"


def test_the_plotted_table_keeps_its_files_and_every_other_member_is_unchanged(tmp_path, monkeypatch):
    world = Wide(tmp_path)
    members = _members(_zip(_export(world, monkeypatch)[0]))
    assert members["C/T1_data.tsv"] == _table_tsv(world, "C", tmp_path)
    assert "C/plots/p.png" in members
    assert "C/T2_data.tsv" not in members, "C has no tier 2 steps"
    new = {f"{t}/T1_data.tsv" for t in "TUVD"}
    assert sorted(set(members) - new) == sorted(
        ["C/T1_data.tsv", "C/plots/p.png", "README.txt", "report.qmd", "effective_run.yaml", "lineage/lineage_graph.json", "id_log.yaml"]
        + [n for n in members if n.startswith("report_")]), sorted(members)


def test_a_recipe_with_no_such_table_gives_the_same_bundle_as_before(tmp_path, monkeypatch):
    """Nothing changes where no table is unread: the member list is the old one and README and report carry no sentence about it."""
    world = Wide(tmp_path)
    recipe = world.data_analysis_recipes_dir / "tiny.yaml"
    text = recipe.read_text()
    # every table is plotted: one plot per table
    plots = "\n".join(f"      p_{t}:\n        ui_label: {t}\n        target_dataset: {t}\n        mapping: {{x: {c}}}\n        layers:\n"
                      "          - name: geom_bar\n            params: {}"
                      for t, c in {"T": "group", "U": "weight", "V": "color", "C": "group", "D": "color"}.items())
    recipe.write_text(text[:text.index("      p:\n")] + plots + "\n")
    bump(recipe)
    clear_data_analysis_recipe_cache()
    members = _members(_zip(_export(world, monkeypatch)[0]))
    assert sorted(n for n in members if n.endswith(".tsv")) == sorted(f"{t}/T1_data.tsv" for t in "TUVCD")
    for name in ("README.txt", "report.qmd"):
        assert "no plot reads" not in members[name].decode().lower(), name


# -- traceability (rule 5) -------------------------------------------------------------------

def test_readme_and_report_record_the_keys_of_the_new_tables_and_say_that_no_plot_reads_them(tmp_path, monkeypatch):
    world = Wide(tmp_path)
    yielded, view = _export(world, monkeypatch)
    members = _members(_zip(yielded))
    readme, report = members["README.txt"].decode(), members["report.qmd"].decode()
    for table in ("T", "U", "V", "D"):
        key = view.tier1_key_of(table)
        assert f"  {table}: tier1_key={key}" in readme, table
        assert f"  {table}: tier2_key=none (T2 equals T1)" in readme, table
        assert f"Tier 1 key ({table})" in report and key in report, table
    assert "  C: tier1_key=" in readme, "the plotted table is recorded as before"
    assert "Tables that no plot reads" in readme and "Tables that no plot reads" in report
    import re
    for text in (readme, report):
        assert "PROVISIONAL" not in text and not re.search(r"D-0\d+", text), "no internal marker in the written text"
    sentence = [ln for ln in readme.splitlines() if "read by no plot" in ln]
    assert sentence, "one plain line says that these tables are read by no plot"
    for table in ("T", "U", "V", "D"):
        assert f"{table}/T1_data.tsv" in readme


def test_the_new_tables_are_read_through_the_orchestrator_with_the_keys_of_the_export(tmp_path, monkeypatch):
    """MUTATION U2 fails here: a table is built with the keys of the export (key-checked), never an anchor served by its file name."""
    world = Wide(tmp_path)
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    calls = []
    real = world.orch.materialize_tier1

    def spy(*args, **kw):
        calls.append((kw["collection_id"], kw["keys"]))
        return real(*args, **kw)

    monkeypatch.setattr(world.orch, "materialize_tier1", spy)
    _run(_download_function(world, view, [], monkeypatch))
    by_table = dict(calls)
    assert {"T", "U", "V", "D", "C"} <= set(by_table), sorted(by_table)
    assert all(k is not None and k.tier1_key_of("U") == view.tier1_key_of("U") for k in by_table.values()), "the same keys object for every table"


# -- edge cases (rules_verification_testing section 9) ----------------------------------------------

def test_a_table_no_plot_reads_that_cannot_be_loaded_is_written_as_an_error_and_told_plainly(tmp_path, monkeypatch):
    """MUTATION U3 fails here. Same as a plot's table that fails today: an `*_ERROR.txt` in the bundle (naming the table and the reason)
    and an error notification; the rest of the bundle is complete, nothing is skipped silently (D-0050)."""
    class Bad(Wide):
        extra_sources = _source("W", "n", "Int64", entity=False)   # a look-up: it takes no part in the completion, so its failure does not stop the other tables

        def write_data_analysis_recipe(self, **kw):
            super().write_data_analysis_recipe(**kw)
            (self.data_dir / "W.tsv").write_text("sample_id\tn\nw1\tabc\n")

    world = Bad(tmp_path)
    notes = []
    members = _members(_zip(_export(world, monkeypatch, notes)[0]))
    assert "W/T1_data.tsv" not in members
    error = members["W/T1_data_ERROR.txt"].decode()
    assert "T1 data export failed" in error and "abc" in error, error
    assert "C/T1_data.tsv" in members and "U/T1_data.tsv" in members, "the other tables are written"
    assert [m for t, m in notes if t == "error" and "'W'" in m and "T1 data" in m], notes


def test_the_key_check_refuses_everything_when_a_file_changed_after_the_view(tmp_path, monkeypatch):
    """Rule 1: nothing is exported when the files changed, so none of the new files is written either."""
    world = Wide(tmp_path)
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    (world.data_dir / "U.tsv").write_text("sample_id\tweight\nu1\t9.9\n")      # the file of a table no plot reads
    bump(world.data_dir / "U.tsv")
    clear_data_analysis_recipe_cache()
    yielded = _run(_download_function(world, view, [], monkeypatch))
    assert _zip(yielded).namelist() == ["EXPORT_NOT_CREATED.txt"]


def test_a_table_no_plot_reads_that_changes_while_it_is_built_refuses_the_export(tmp_path, monkeypatch):
    world = Wide(tmp_path)
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    real = world.orch.prepare_ingredient
    state = {"done": False}

    def ingest_then_the_file_changes(ds_id, *a, **k):
        lf = real(ds_id, *a, **k)
        if ds_id == "U" and not state["done"]:
            state["done"] = True
            (world.data_dir / "U.tsv").write_text("sample_id\tweight\nu1\t9.9\n")
            bump(world.data_dir / "U.tsv")
        return lf

    monkeypatch.setattr(world.orch, "prepare_ingredient", ingest_then_the_file_changes)
    yielded = _run(_download_function(world, view, [], monkeypatch))
    assert _zip(yielded).namelist() == ["EXPORT_NOT_CREATED.txt"]


def test_audit_steps_of_the_plot_never_change_these_files(tmp_path, monkeypatch):
    """HOME writes an audit step only at a plot's table (T3 of the plot): the files of the tables no plot reads are the same."""
    plain = _members(_zip(_export(Wide(tmp_path / "a"), monkeypatch)[0]))
    world = Wide(tmp_path / "b")
    nodes = [{**n, "place": "T3:p", "plot_scope": "__places__", "created_at": "t"} for n in filter_nodes(
        [{"column": "group", "op": "eq", "value": "A", "dtype": "Categorical", "na": "remove"}])]
    audited = _members(_zip(_export(world, monkeypatch, flags=FLAGS, **audit_kwargs(world, nodes))[0]))
    assert "C/T3_data_p.tsv" in audited, "the audit step is applied to the plot's table"
    for table in ("T", "U", "V", "D"):
        assert audited[f"{table}/T1_data.tsv"] == plain[f"{table}/T1_data.tsv"], table


def test_two_tables_that_read_the_same_data_file_get_two_files_and_two_key_lines(tmp_path, monkeypatch):
    class Twin(Wide):
        extra_sources = _source("U2", "weight", "Float64", file="U")

    world = Twin(tmp_path)
    members = _members(_zip(_export(world, monkeypatch)[0]))
    # the same data file, read by two tables: the same table apart from the name of the marker column each one has (one marker per table)
    assert members["U/T1_data.tsv"].replace(b"U_not_in_original_data", b"marker") == members["U2/T1_data.tsv"].replace(b"U2_not_in_original_data", b"marker")
    readme = members["README.txt"].decode()
    assert "  U: tier1_key=" in readme and "  U2: tier1_key=" in readme


def test_two_tables_whose_folder_names_would_be_equal_are_not_mixed(tmp_path, monkeypatch):
    """`_safe_ds_name` turns `a b` and `a_b` into the same folder name: the second table gets its own folder, nothing is written over."""
    class Clash(Wide):
        extra_sources = _source("a_b", "weight", "Float64", file="U") + _source("'a b'", "weight", "Float64", file="Z")

        def write_data_analysis_recipe(self, **kw):
            (self.data_dir / "Z.tsv").write_text("sample_id\tweight\nz1\t7.5\n")
            super().write_data_analysis_recipe(**kw)

    world = Clash(tmp_path)
    members = _members(_zip(_export(world, monkeypatch)[0]))
    # each table has its own lines (marked false); the lines of the other table are added to it, marked true (the completion of the ids)
    assert b"u1\t1.5\tfalse" in members["a_b/T1_data.tsv"] and b"z1\t7.5\tfalse" not in members["a_b/T1_data.tsv"], "the first table keeps its folder and its data"
    assert b"z1\t7.5\tfalse" in members["a_b_2/T1_data.tsv"] and b"u1\t1.5\tfalse" not in members["a_b_2/T1_data.tsv"], "the second table has its own folder"
    readme = members["README.txt"].decode()
    assert "a b: a_b_2/T1_data.tsv" in readme and "a_b: a_b/T1_data.tsv" in readme
