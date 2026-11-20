"""Every export holds ALL plots of the recipe, and the plot format starts as SVG (D-0292, D-0295, D-0294). No browser.

The real download generator of `export_handlers.py` is run on a real tiny recipe with three plots in two groups
(the harness of `test_export_download_path.py`; Quarto is replaced there, the pictures are really drawn).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_export_all_plots_and_defaults.py -q
"""
import io
import re
import zipfile
from types import SimpleNamespace

import pytest
from shiny import render

from app.handlers import export_handlers
from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.export_fields_store import EXPORT_FIELD_DEFAULTS
from app.tests.test_cache_chain import World
from app.tests.test_export_download_path import _Bootloader, _download_function, _run

PLOTS = {"p", "q", "r"}


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def _three_plot_world(tmp_path) -> World:
    """The tiny recipe with a second group: plots p (group g), q and r (group h)."""
    world = World(tmp_path)
    recipe = world.data_analysis_recipes_dir / "tiny.yaml"
    plot = "        target_dataset: C\n        mapping: {x: group}\n        layers:\n          - name: geom_bar\n            params: {}\n"
    recipe.write_text(recipe.read_text() + (
        "  h:\n    ui_label: H\n    plots:\n"
        f"      q:\n        ui_label: Q\n{plot}"
        f"      r:\n        ui_label: R\n{plot}"))
    clear_data_analysis_recipe_cache()
    return world


def _picture_stems(archive: zipfile.ZipFile) -> dict:
    """{plot id: extension} of every picture under `<table>/plots/` (the error stubs are `*_ERROR.txt`, not pictures)."""
    found = {}
    for name in archive.namelist():
        m = re.search(r"/plots/([^/]+)\.(png|svg|pdf)$", name)
        if m:
            found[m.group(1)] = m.group(2)
    return found


def _bundle(tmp_path, monkeypatch, **values) -> zipfile.ZipFile:
    world = _three_plot_world(tmp_path)
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    yielded = _run(_download_function(world, view, [], monkeypatch, extra_values=values))
    assert len(yielded) == 1
    return zipfile.ZipFile(io.BytesIO(yielded[0]))


@pytest.mark.parametrize("tick", [False, True])
def test_the_bundle_holds_every_plot_of_the_recipe_with_and_without_the_mode_tick(tmp_path, monkeypatch, tick):
    archive = _bundle(tmp_path, monkeypatch, export_include_reproducibility=tick)
    assert "EXPORT_NOT_CREATED.txt" not in archive.namelist()
    assert set(_picture_stems(archive)) == PLOTS, "an export always holds all plots of the recipe, in both modes"
    readme = next(archive.read(n).decode() for n in archive.namelist() if n.endswith("/README.txt"))
    assert "Plots            : 3 (all plots of the recipe are exported)" in readme
    assert "Export scope" not in readme


def test_the_provenance_has_no_scope_key():
    """PROVISIONAL (drop the key / keep it as "global"): the key is dropped; nothing of the bundle import reads it."""
    import datetime
    prov = export_handlers.build_export_provenance(
        now=datetime.datetime(2026, 11, 18), data_analysis_recipe_id="tiny", safe_name="x", app_features="qa", preset="web",
        dpi=300, screen_view="Exploration mode, data view T3", all_plots=[], tiers_exported=["T1"], data_analysis_recipe_sha="m" * 64,
        data_sha="d" * 64, bootloader=SimpleNamespace(available_data_analysis_recipes={}))
    assert "export_scope" not in prov


def test_a_bundle_made_without_touching_the_plot_format_holds_svg_pictures(tmp_path, monkeypatch):
    """No value for the plot format (None), as for a user who never touched the field: the default is used."""
    assert EXPORT_FIELD_DEFAULTS["export_plot_format"] == "svg"
    archive = _bundle(tmp_path, monkeypatch, export_plot_format=None)
    assert set(_picture_stems(archive).values()) == {"svg"}, _picture_stems(archive)
    readme = next(archive.read(n).decode() for n in archive.namelist() if n.endswith("/README.txt"))
    assert "Plot format      : svg" in readme


def test_the_panel_shows_svg_and_html_selected_and_no_scope_choice(tmp_path, monkeypatch):
    """The panel as the user first sees it: SVG and HTML selected (D-0294), no Scope radio, no scope text."""
    world = World(tmp_path)
    shown = {}
    monkeypatch.setattr(render, "ui", lambda fn: shown.setdefault(fn.__name__, fn) and fn)
    monkeypatch.setattr(render, "download", lambda *a, **k: (lambda fn: fn))
    from shiny import reactive
    monkeypatch.setattr(reactive, "Effect", lambda fn: fn)
    monkeypatch.setattr(reactive, "event", lambda *a, **k: (lambda fn: fn))
    monkeypatch.setattr(reactive, "effect", lambda fn=None, **k: fn if fn is not None else (lambda f: f))   # the priority effects
    export_handlers.define_export_server(
        SimpleNamespace(import_bundle_upload=None, export_field_change=None), lambda fn: fn, None,
        bootloader=_Bootloader(world, ("export_enabled",)), orchestrator=world.orch, viz_factory=None,
        current_app_features=SimpleNamespace(get=lambda: "qa"), active_cfg=lambda: None, tier1_anchor=None,
        screen_view=lambda: "", home_state=None, safe_input=lambda _i, key, default: default, view_keys=lambda: None)
    html = str(shown["system_tools_ui"]())
    assert re.search(r'name="export_plot_format"[^>]*value="svg"[^>]*checked', html)
    assert re.search(r'name="export_report_format"[^>]*value="html"[^>]*checked', html)
    assert "export_scope" not in html and ">Scope<" not in html and "Active plot" not in html
