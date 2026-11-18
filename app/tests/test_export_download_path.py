"""The export's download path RUNS headless: what is yielded when a table was built while the files changed (STALE-KEY-STORE-1).

D-0005 "export refuses when files changed since the view", D-0050 "No silent error that is the rule". The real generator of
`export_bundle_download` (`app/handlers/export_handlers.py`) is called, without a browser, on a real orchestrator and a real tiny
recipe. During the first build of a table the data file changes. The only thing the generator yields must be the zip with
`EXPORT_NOT_CREATED.txt`; a control without a change yields the bundle.

Mutation index (grep "MUTATION"; each seen failing):
  MUTATION X1  the refusal is computed but not yielded (`yield _build_refusal` removed)
  MUTATION X2  `_on_build_change` records nothing

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_export_download_path.py -q
"""
import asyncio
import io
import subprocess
import zipfile
from types import SimpleNamespace
from unittest import mock

import polars as pl
import pytest
from shiny import reactive, render, ui

from app.handlers import export_handlers
from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe
from app.tests.test_cache_chain import World
from viz_factory.viz_factory import VizFactory

NEW_DATA = "sample_id\tgroup\ns1\tA\ns2\tA\ns3\tB\ns4\tA\n"


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


class _Bootloader:
    """What the export reads of the Bootloader."""

    def __init__(self, world, flags=(), deployment_contact=None):
        self.deployment_contact = deployment_contact
        self.world = world
        self.flags = set(flags)
        self.rejected_data_analysis_recipes = {}
        self.available_data_analysis_recipes = {"tiny": world.data_analysis_recipes_dir / "tiny.yaml"}

    def get_location(self, key):
        return self.world.root / "user"

    def get_contact(self):
        return self.deployment_contact

    def get_default_data_analysis_recipe(self):
        return "tiny"

    def is_enabled(self, flag):
        return flag in self.flags


def _download_function(world, view_keys, notes, monkeypatch, tier1_anchor=None, extra_values=None, flags=(), info=None, deployment_contact=None, **handler_kwargs):
    """`define_export_server` with the smallest set of real and fake parts; returns the generator function of the download."""
    captured = {}

    def download(filename=None, **kwargs):
        def register(fn):
            captured["fn"] = fn
            return fn
        return register

    monkeypatch.setattr(render, "download", download)
    monkeypatch.setattr(reactive, "Effect", lambda fn: fn)
    monkeypatch.setattr(reactive, "event", lambda *a, **k: (lambda fn: fn))
    monkeypatch.setattr(reactive, "effect", lambda fn=None, **k: fn if fn is not None else (lambda f: f))   # the priority effects
    monkeypatch.setattr(ui, "notification_show", lambda message, **kw: notes.append((kw.get("type"), str(message))))
    real_run = subprocess.run
    monkeypatch.setattr(subprocess, "run", lambda args, *a, **k: subprocess.CompletedProcess(args, 1, "", "no render in this test")
                        if args and args[0] == "quarto" else real_run(args, *a, **k))
    cfg = load_data_analysis_recipe(world.data_analysis_recipes_dir / "tiny.yaml").config
    if info is not None:
        cfg.raw_config["info"] = info
    # the pictures are read as PNG by most tests, so the harness chooses png; a value of None is "not touched" (the real
    # safe_input gives the default then), which is how the tests of the default plot format run
    values = {"export_user_name": "test", "export_preset": "web", "export_plot_format": "png",
              **(extra_values or {})}
    export_handlers.define_export_server(
        SimpleNamespace(import_bundle_upload=None, export_field_change=None), lambda fn: fn, None,
        bootloader=_Bootloader(world, flags, deployment_contact), orchestrator=world.orch, viz_factory=VizFactory(),
        current_app_features=SimpleNamespace(get=lambda: "qa"), active_cfg=lambda: cfg,
        tier1_anchor=tier1_anchor or (lambda: pl.DataFrame().lazy()), tier_toggle=SimpleNamespace(get=lambda: "T2"),
        **{"home_state": None, **handler_kwargs},
        safe_input=lambda _input, key, default: default if values.get(key) is None else values[key], view_keys=lambda: view_keys)
    return captured["fn"]


def _run(generator_function):
    async def collect():
        return [chunk async for chunk in generator_function()]
    return asyncio.run(collect())


def _change_the_data_during_the_first_build(world, monkeypatch):
    real = world.orch.prepare_ingredient
    state = {"done": False}

    def ingest_then_the_file_changes(*args, **kwargs):
        lf = real(*args, **kwargs)
        if not state["done"]:
            state["done"] = True
            world.write_data(NEW_DATA)
        return lf

    monkeypatch.setattr(world.orch, "prepare_ingredient", ingest_then_the_file_changes)


def test_an_export_whose_table_was_built_while_the_data_changed_yields_only_the_refusal(tmp_path, monkeypatch):
    """MUTATION X1 and MUTATION X2 fail here: the generator, run for real, must hand over only EXPORT_NOT_CREATED.txt."""
    world = World(tmp_path)
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    notes = []
    function = _download_function(world, view, notes, monkeypatch)
    _change_the_data_during_the_first_build(world, monkeypatch)
    yielded = _run(function)
    assert len(yielded) == 1, "the refusal is the only thing handed over"
    archive = zipfile.ZipFile(io.BytesIO(yielded[0]))
    assert archive.namelist() == ["EXPORT_NOT_CREATED.txt"], "nothing else is in the zip"
    text = archive.read("EXPORT_NOT_CREATED.txt").decode()
    assert "while a table of this export was being built: the data files changed" in text and "nothing was exported" in text
    assert [t for t, m in notes if t == "error" and "Export blocked" in m and "being built" in m], notes


def test_the_same_export_without_a_change_hands_over_the_bundle(tmp_path, monkeypatch):
    """The control: the harness really runs the export to its end, so the refusal above is not an artefact of the harness."""
    world = World(tmp_path)
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    notes = []
    yielded = _run(_download_function(world, view, notes, monkeypatch))
    assert len(yielded) == 1
    names = zipfile.ZipFile(io.BytesIO(yielded[0])).namelist()
    assert "EXPORT_NOT_CREATED.txt" not in names
    assert any(n.endswith("/README.txt") for n in names) and any(n.endswith("report.qmd") for n in names)
    assert not [t for t, _ in notes if t == "error"]


def test_a_plot_with_no_target_table_reads_HOMES_stored_table_and_builds_nothing_in_the_export(tmp_path, monkeypatch):
    """Round 4 point 2, run: the export's fallback `tier1_anchor()` is a read of the table HOME stored (server.py: a scan of
    `anchor_path`), not a build, so there is no build of the export that could change under it and nothing to report to the refusal.
    What it reads is not key-checked against the export's keys: recorded for Eve in the report (a choice), not changed here."""
    world = World(tmp_path)
    recipe = world.data_analysis_recipes_dir / "tiny.yaml"
    recipe.write_text(recipe.read_text().replace("target_dataset: C", 'target_dataset: ""'))
    clear_data_analysis_recipe_cache()
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    reads = []
    builds = []
    monkeypatch.setattr(world.orch, "materialize_tier1", lambda *a, **k: builds.append("tier1"))
    monkeypatch.setattr(world.orch, "materialize_tier2", lambda *a, **k: builds.append("tier2"))
    function = _download_function(world, view, [], monkeypatch,
                                  tier1_anchor=lambda: reads.append("read") or pl.DataFrame({"x": [1]}).lazy())
    yielded = _run(function)
    assert reads, "the plot without a target reads HOME's table through tier1_anchor()"
    assert builds == [], "and the export builds no table for it"
    assert len(yielded) == 1


def _bundle_texts(tmp_path, monkeypatch, **kw):
    import yaml
    world = World(tmp_path)
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    yielded = _run(_download_function(world, view, [], monkeypatch, **kw))
    z = zipfile.ZipFile(io.BytesIO(yielded[0]))
    run = yaml.safe_load(z.read(next(n for n in z.namelist() if n.endswith("effective_run.yaml"))).decode())
    readme = z.read(next(n for n in z.namelist() if n.endswith("/README.txt"))).decode()
    return run, [ln for ln in readme.splitlines() if ln.startswith("Contact")]


def test_the_written_bundle_carries_the_contact_of_the_recipe(tmp_path, monkeypatch):
    run, lines = _bundle_texts(tmp_path, monkeypatch, info={"contact": " a@lab.org "}, deployment_contact="dep@x.org")
    assert run["contact"] == "a@lab.org" and run["contact_source"] == "recipe (info.contact)"
    assert lines == ["Contact          : a@lab.org (from the recipe (info.contact))"]


def test_the_written_bundle_says_so_when_there_is_no_contact(tmp_path, monkeypatch):
    run, lines = _bundle_texts(tmp_path, monkeypatch, info={"contact": "   "})
    assert run["contact"] is None and run["contact_source"] is None
    assert len(lines) == 1 and "names no contact" in lines[0]
