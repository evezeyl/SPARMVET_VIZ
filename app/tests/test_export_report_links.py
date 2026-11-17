"""Every data link of `report.qmd` points to a file that is in the bundle (VERIF-FIX-2, E4; D-0050 "No silent error that is the rule.").

The report linked `<dataset>/T3_data.tsv` for every dataset whenever any plot had audited steps, but the files are one per audited plot
(`T3_data_<plot>.tsv`, EXPORT-T3-1) and only for plots with audited steps; the T2 file that exists was never linked. A reader who clicked
got nothing and nothing said why. The figure links `_render/<plot>.<ext>` are not data links: they point to copies that exist only while
Quarto renders (a separate finding, listed in the report of this task); they are left out of the check, by name.

Mutation index (grep "MUTATION"; each seen failing):
  MUTATION L1  the report links `T3_data.tsv` for the dataset again
  MUTATION L2  the report links the T3 file of a plot that has no audited steps
  MUTATION L3  the report links no T2 file although one is in the bundle

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_export_report_links.py -q
"""
import io
import re
import zipfile
from types import SimpleNamespace
from urllib.parse import unquote

import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.session_manager import make_audit_step
from app.tests.test_cache_chain import FILTER_A, World
from app.tests.test_export_download_path import _download_function, _run

LINK = re.compile(r"\]\(([^)\s]+)\)")


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def _audited_export(world, monkeypatch, steps_for_plot=True):
    """The real download generator with one audited step on plot `p` (a filter, with its reason)."""
    step = make_audit_step("filter_row", {"column": "group", "op": "ne", "value": "B", "dtype": "String", "na": "remove"},
                           "subtab_p", "the group B samples failed quality control")
    state = {"t3_audit_steps_by_plot": {"subtab_p": [step]} if steps_for_plot else {}}
    rows = [{"column": "group", "op": "ne", "value": "B", "dtype": "String", "na": "remove"}] if steps_for_plot else []
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    notes = []
    function = _download_function(
        world, view, notes, monkeypatch, flags=("t3_sandbox_enabled",), home_state=SimpleNamespace(get=lambda: state),
        t3_filter_rows=lambda subtab: rows if subtab == "subtab_p" else [], t3_drop_columns=lambda subtab: [])
    archive = zipfile.ZipFile(io.BytesIO(_run(function)[0]))
    return archive, notes


def _data_links(archive):
    """`(bundle folder, links)`: the relative targets of `report.qmd` that are not Quarto's own `_render/` copies."""
    report = next(n for n in archive.namelist() if n.endswith("/report.qmd"))
    folder = report.rsplit("/", 1)[0]
    links = [unquote(t) for t in LINK.findall(archive.read(report).decode())
             if not t.startswith(("http", "#", "_render/"))]
    return folder, links


def test_every_data_link_of_the_report_points_to_a_file_of_the_bundle(tmp_path, monkeypatch):
    """MUTATION L1 fails here."""
    archive, _ = _audited_export(World(tmp_path), monkeypatch)
    folder, links = _data_links(archive)
    assert any(t.endswith("T3_data_p.tsv") for t in links), "the audited data of the plot is linked"
    names = set(archive.namelist())
    missing = [t for t in links if f"{folder}/{t}" not in names]
    assert missing == [], f"the report links files that are not in the bundle: {missing}"
    assert not any(t.endswith("/T3_data.tsv") for t in links)


def test_a_plot_without_audited_steps_gets_no_t3_link(tmp_path, monkeypatch):
    """MUTATION L2 fails here: nothing is audited, so no T3 file exists and none is linked."""
    archive, _ = _audited_export(World(tmp_path), monkeypatch, steps_for_plot=False)
    folder, links = _data_links(archive)
    assert [t for t in links if "T3_data" in t] == []
    assert all(f"{folder}/{t}" in set(archive.namelist()) for t in links)
    assert any(t.endswith("T1_data.tsv") for t in links), "the raw data is still linked"


def test_the_t2_file_is_linked_when_the_bundle_has_one(tmp_path, monkeypatch):
    """MUTATION L3 fails here: a table with tier 2 steps has a `T2_data.tsv` and the report links it."""
    world = World(tmp_path)
    world.write_data_analysis_recipe(steps_tier2=[FILTER_A])
    clear_data_analysis_recipe_cache()
    archive, _ = _audited_export(world, monkeypatch, steps_for_plot=False)
    names = archive.namelist()
    assert any(n.endswith("/C/T2_data.tsv") for n in names), "the harness really exports a T2 file"
    folder, links = _data_links(archive)
    assert any(t.endswith("T2_data.tsv") for t in links)
    assert all(f"{folder}/{t}" in set(names) for t in links)


def test_a_plot_with_no_target_table_links_the_data_where_it_is(tmp_path, monkeypatch):
    """A plot with no `target_dataset` has its plots in `__anchor__/` and its raw data in `__tier1_anchor__/`: the link follows the file."""
    import polars as pl
    world = World(tmp_path)
    recipe = world.data_analysis_recipes_dir / "tiny.yaml"
    recipe.write_text(recipe.read_text().replace("target_dataset: C", 'target_dataset: ""'))
    clear_data_analysis_recipe_cache()
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    function = _download_function(world, view, [], monkeypatch,
                                  tier1_anchor=lambda: pl.DataFrame({"group": ["A", "B"], "sample_id": ["s1", "s2"]}).lazy())
    archive = zipfile.ZipFile(io.BytesIO(_run(function)[0]))
    folder, links = _data_links(archive)
    names = set(archive.namelist())
    assert [t for t in links if f"{folder}/{t}" not in names] == [], links
    assert any(t.endswith("T1_data.tsv") for t in links)


def test_the_t1_file_is_linked_only_when_it_was_written(tmp_path, monkeypatch):
    """MUTATION L4 fails here (`if _data_key in exported_dfs` always true): a T1 write that fails leaves `T1_data_ERROR.txt` and no
    `T1_data.tsv`, so the report must not link it."""
    from unittest import mock
    world = World(tmp_path)
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    function = _download_function(world, view, [], monkeypatch)
    monkeypatch.setattr(world.orch, "materialize_tier1", mock.Mock(side_effect=RuntimeError("the tier 1 table broke")))
    archive = zipfile.ZipFile(io.BytesIO(_run(function)[0]))
    names = set(archive.namelist())
    assert any(n.endswith("T1_data_ERROR.txt") for n in names) and not any(n.endswith("/T1_data.tsv") for n in names)
    folder, links = _data_links(archive)
    assert not any(t.endswith("T1_data.tsv") for t in links), links
    assert [t for t in links if f"{folder}/{t}" not in names] == []
