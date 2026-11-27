"""The audited table files of an export made in Audit mode (owner, 2026-11-24; PROVISIONAL form) and the audit steps of the three tiers in one export.

The real download generator is run headless (as `test_export_download_path.py` runs it) on the recipe of `test_export_unread_tables.Wide`: the sources T (read by the join C,
plotted by `p`), U (read by nothing), V (read by the join D) and D (a join no plot reads). The audit steps are nodes written at a place, handed to the export the way HOME hands
them (`audit_export_harness.audit_kwargs`: the same `PlaceAudit`).

What is proved:
- an export made in Audit mode writes, for every table an audit step changes (the table of the place and every table built from it), the audited table at each tier beside the
  original: `T1_data_audited.tsv` beside `T1_data.tsv`, `T2_data_audited.tsv`; the original file is the file of an export with no audit step, byte for byte;
- a table beside the place has no audited file (U, V and D for a step at T1 of T); a step at the tier 3 of a plot changes no table, so no audited table file;
- the audited file equals the audited table the audit copy gives (the table HOME's plot reads): same rows, same columns;
- an export made in Exploration mode keeps today's table files: the originals only, whatever audit steps exist; the plots and the T3 file of the plot are audited in both modes;
- README.txt and report.qmd say, in one sentence per table, which file is which and which steps made the difference; and say it when no audited file exists and why;
- the steps of the three tiers together (T1 of T, T2 of C, T3 of p): the exported T3 file of the plot equals the table HOME reads in Audit mode, and the steps are listed in
  t3_steps.yaml with their places.

Mutation index (each seen failing): MUTATION A1 `_write_audited` writes nothing (the audited files are missing); MUTATION A2 `in_audit` is ignored (an export made in Exploration mode writes them);
MUTATION A3 `AuditRun.audited_frames` lists every table (a table beside the place gets an audited file).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_export_audited_tables.py -q
"""
import io
import zipfile

import polars as pl
import pytest

from app.modules.audit_view import PlaceAudit
from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.session_manager import make_audit_step
from app.tests.audit_export_harness import FLAGS, audit_kwargs
from app.tests.test_export_download_path import _download_function, _run
from app.tests.test_export_unread_tables import Wide


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def step(place, column="group", op="eq", value="A", reason="keep group A"):
    return make_audit_step("filter_row", {"column": column, "op": op, "value": value, "dtype": "Categorical", "na": "remove"}, reason=reason,
                           place=place, started_from="subtab_p")


def export(root, monkeypatch, nodes, in_audit):
    """The bundle of one export of a fresh world: `{name without the folder of the export: bytes}` and the world."""
    world = Wide(root)
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    yielded = _run(_download_function(world, view, [], monkeypatch, flags=FLAGS, **audit_kwargs(world, nodes, in_audit=in_audit)))
    archive = zipfile.ZipFile(io.BytesIO(yielded[0]))
    assert "EXPORT_NOT_CREATED.txt" not in archive.namelist(), archive.namelist()
    return {n.split("/", 1)[-1]: archive.read(n) for n in archive.namelist()}, world


def tsv(members, name):
    return pl.read_csv(io.BytesIO(members[name]), separator="\t", infer_schema_length=0)


def audited_names(members):
    return sorted(n for n in members if n.endswith("_audited.tsv"))


def test_in_audit_mode_a_table_an_audit_step_changes_has_its_audited_file_beside_its_original(tmp_path, monkeypatch):
    plain, _ = export(tmp_path / "plain", monkeypatch, [], in_audit=True)
    members, world = export(tmp_path / "audit", monkeypatch, [step("T1:T")], in_audit=True)
    assert audited_names(plain) == [], "no step, no audited file"
    assert audited_names(members) == ["C/T1_data_audited.tsv", "T/T1_data_audited.tsv"], "the table of the place and the table built from it"
    for table in ("T", "C"):
        original, audited = tsv(members, f"{table}/T1_data.tsv"), tsv(members, f"{table}/T1_data_audited.tsv")
        assert original.height > audited.height > 0, table
        assert set(audited["group"]) == {"A"} and set(original["group"]) > {"A"}
        assert audited.columns == original.columns
        assert members[f"{table}/T1_data.tsv"] == plain[f"{table}/T1_data.tsv"], "the original file is what an export with no audit step writes"


def test_a_table_beside_the_place_has_no_audited_file(tmp_path, monkeypatch):
    members, _ = export(tmp_path, monkeypatch, [step("T1:T")], in_audit=True)
    for beside in ("U", "V", "D"):
        assert f"{beside}/T1_data.tsv" in members and f"{beside}/T1_data_audited.tsv" not in members, beside


def test_the_audited_file_equals_the_audited_table_the_audit_copy_gives_for_the_plot(tmp_path, monkeypatch):
    nodes = [step("T1:T")]
    members, world = export(tmp_path, monkeypatch, nodes, in_audit=True)
    audit = PlaceAudit(world.orch, world.root / "user" / "anchors", world.root / "user" / "audit_anchors")
    home = audit.plot_lazy("tiny", "p", nodes).collect()                      # the table HOME's plot reads in Audit mode (p reads C, which has no tier 2)
    exported = tsv(members, "C/T1_data_audited.tsv")
    assert exported.columns == home.columns
    assert exported["sample_id"].to_list() == home["sample_id"].cast(pl.String).to_list()
    assert exported.equals(tsv(members, "C/T3_data_p.tsv")), "the plot is drawn from the audited table: its T3 file is the same rows"


def test_in_exploration_mode_the_table_files_stay_the_originals_whatever_audit_steps_exist(tmp_path, monkeypatch):
    plain, _ = export(tmp_path / "plain", monkeypatch, [], in_audit=False)
    members, _ = export(tmp_path / "expl", monkeypatch, [step("T1:T")], in_audit=False)
    assert audited_names(members) == []
    for table in ("T", "C", "U", "V", "D"):
        assert members[f"{table}/T1_data.tsv"] == plain[f"{table}/T1_data.tsv"], table
    assert "C/T3_data_p.tsv" in members and tsv(members, "C/T3_data_p.tsv").height < tsv(members, "C/T1_data.tsv").height, "the plot and its T3 file are audited in both modes"
    readme = members["README.txt"].decode()
    assert "Exploration mode, where the table files are not audited" in readme


def test_a_step_at_the_tier3_of_a_plot_changes_no_table_so_no_audited_table_file(tmp_path, monkeypatch):
    members, _ = export(tmp_path, monkeypatch, [step("T3:p")], in_audit=True)
    assert audited_names(members) == []
    assert "no audit step changes a table here" in members["README.txt"].decode()
    assert tsv(members, "C/T3_data_p.tsv").height < tsv(members, "C/T1_data.tsv").height


def test_a_step_at_the_tier2_of_a_table_gives_an_audited_tier2_and_an_unchanged_tier1(tmp_path, monkeypatch):
    members, _ = export(tmp_path, monkeypatch, [step("T2:C")], in_audit=True)
    assert audited_names(members) == ["C/T2_data_audited.tsv"], "tier 1 of C is the original's: no audited tier 1"
    readme = members["README.txt"].decode()
    assert "the original tier 2 of this table is its tier 1 (C/T1_data.tsv" in readme, "the recipe has no tier-2 step for C: its tier 2 is its tier 1"


def test_readme_and_report_say_which_file_is_which_and_which_steps_made_the_difference(tmp_path, monkeypatch):
    node = step("T1:T")
    members, _ = export(tmp_path, monkeypatch, [node], in_audit=True)
    readme = members["README.txt"].decode()
    assert "This export was made in Audit mode" in readme
    assert "T/T1_data_audited.tsv is the T1 table of 'T' with the audit steps applied; T/T1_data.tsv is the original" in readme
    assert f"{node['id']} (at Table T (tier 1))" in readme and "C/T1_data_audited.tsv is the T1 table of 'C'" in readme
    report = members["report.qmd"].decode()
    assert "come twice, the original and the audited one" in report and "T/T1_data_audited.tsv" in report
    assert "[Audited raw data (T1)](C/T1_data_audited.tsv)" in report
    assert "Audit mode" in readme and "audited_files" not in readme


def test_the_steps_of_the_three_tiers_in_one_export_the_t3_file_equals_the_table_home_reads(tmp_path, monkeypatch):
    nodes = [step("T1:T", column="group", value="A"), step("T2:C", column="sample_id", op="ne", value="s1", reason="s1 failed"), step("T3:p", column="sample_id", op="ne", value="s2", reason="s2 failed")]
    members, world = export(tmp_path, monkeypatch, nodes, in_audit=True)
    audit = PlaceAudit(world.orch, world.root / "user" / "anchors", world.root / "user" / "audit_anchors")
    home = audit.plot_lazy("tiny", "p", nodes).collect()
    exported = tsv(members, "C/T3_data_p.tsv")
    assert exported["sample_id"].to_list() == home["sample_id"].cast(pl.String).to_list() and exported.columns == home.columns
    original = tsv(members, "C/T1_data.tsv")
    assert exported.height < original.height and "s1" not in exported["sample_id"].to_list() and "s2" not in exported["sample_id"].to_list()
    import yaml
    record = yaml.safe_load(members["t3_steps.yaml"])
    assert [(r["id"], r["written_at"]) for r in record["steps_by_place"]] == [(n["id"], n["place"]) for n in nodes]
    assert audited_names(members) == ["C/T1_data_audited.tsv", "C/T2_data_audited.tsv", "T/T1_data_audited.tsv"]
    assert tsv(members, "C/T2_data_audited.tsv").height == tsv(members, "C/T1_data_audited.tsv").height - 1, "the step at tier 2 of C removes s1 there and no more"


# -------------------------------------------------------------------------------------- the audit recipe of the bundle (D-0622)
def test_an_export_made_in_audit_mode_holds_the_audit_recipe_and_running_it_alone_gives_the_exported_tables(tmp_path, monkeypatch):
    """The recipe in `audit_recipe/`, written to a folder of its own and run by a fresh orchestrator, builds the audited tables and the table of the plot that the bundle holds."""
    import yaml
    from app.modules.cache_keys import load_data_analysis_recipe
    from app.modules.orchestrator import DataOrchestrator
    nodes = [step("T1:T", column="group", value="A", reason="keep group A"), step("T2:C", column="sample_id", op="ne", value="s1", reason="s1 failed"),
             step("T3:p", column="sample_id", op="ne", value="s2", reason="s2 failed")]
    members, world = export(tmp_path / "audit", monkeypatch, nodes, in_audit=True)
    assert [n for n in members if n.startswith("audit_recipe/")] == ["audit_recipe/tiny_audited.yaml"]
    folder = tmp_path / "from_the_bundle"
    folder.mkdir()
    (folder / "tiny_audited.yaml").write_bytes(members["audit_recipe/tiny_audited.yaml"])
    recipe = yaml.safe_load(members["audit_recipe/tiny_audited.yaml"])
    assert recipe["id"] == "tiny_audited" and "audit recipe of 'tiny'" in recipe["info"]["description"]
    for node, words in zip(nodes, ("keep group A", "s1 failed", "s2 failed")):
        assert any(node["id"] in str(s.get("comment", "")) and words in str(s.get("comment", "")) for s in _all_steps(recipe)), f"the step {node['id']} is visible with its reason"
    clear_data_analysis_recipe_cache()
    fresh = DataOrchestrator(folder, world.data_dir)
    anchors = tmp_path / "alone"
    t1_c = fresh.materialize_tier1("tiny_audited", "C", anchors / "C.parquet").collect()
    t2_c = fresh.materialize_tier2("tiny_audited", "C", anchors / "C.parquet").collect()
    plot = fresh.materialize_tier3("tiny_audited", "p", anchors).collect()
    as_text = lambda frame: frame.with_columns(pl.all().cast(pl.String))
    assert as_text(t1_c).equals(tsv(members, "C/T1_data_audited.tsv")) and as_text(t2_c).equals(tsv(members, "C/T2_data_audited.tsv"))
    assert as_text(plot).equals(tsv(members, "C/T3_data_p.tsv")), "the table of the plot, from the audit recipe alone, is the exported T3 file"
    assert load_data_analysis_recipe(folder / "tiny_audited.yaml").raw["id"] == "tiny_audited"
    clear_data_analysis_recipe_cache()


def _all_steps(recipe):
    for body in list(recipe.get("data_schemas", {}).values()) + list(recipe.get("joins", {}).values()):
        for tier in ("tier1", "tier2"):
            yield from (body.get(tier) or {}).get("steps", [])
    for group in recipe.get("analysis_groups", {}).values():
        for entry in group["plots"].values():
            yield from (entry.get("tier3") or {}).get("steps", [])


def test_the_readme_and_the_report_say_where_the_audit_recipe_is_and_what_running_it_gives(tmp_path, monkeypatch):
    members, _ = export(tmp_path, monkeypatch, [step("T1:T")], in_audit=True)
    readme, report = members["README.txt"].decode(), members["report.qmd"].decode()
    for text in (readme, report):
        assert "audit_recipe/tiny_audited.yaml is the audit recipe of 'tiny'" in text
        assert "a recipe like any other" in text and "gives the audited tables and plots of this export" in text
    assert "audit_recipe/<id>_audited.yaml" in readme.split("Contents:")[1]


def test_no_audit_recipe_in_an_export_with_no_step_or_made_in_exploration_mode(tmp_path, monkeypatch):
    for label, nodes, in_audit in (("nostep", [], True), ("expl", [step("T1:T")], False)):
        members, _ = export(tmp_path / label, monkeypatch, nodes, in_audit=in_audit)
        assert not any(n.startswith("audit_recipe/") for n in members), label
        assert "audit_recipe" not in members["README.txt"].decode().replace("audit_recipe_", ""), label
