"""D-0269: the export collects the warnings of the pictures it draws and writes them into its record.

HOME reports a plot warning (a missing font ...) through `on_warning`; the export drew its pictures without telling the
reader of the bundle. The real download generator runs headless as in `test_export_download_path.py`. The README says it in
plain words (same text as HOME's Alerts panel, `plot_warning_text`); `effective_run.yaml` holds it per plot for a machine.

Cases: no warning; one; several on one plot; the same warning on two plots (written for each, not merged); a plot that HOME
never showed (the export draws every plot of the scope); the real missing-font warning of the library; the export still
succeeds with a warning.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_export_plot_warnings.py -q
"""
import io
import zipfile

import pytest
import yaml

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.plot_issue_reporter import plot_warning_text
from app.tests.test_cache_chain import World
from app.tests.test_export_download_path import _download_function, _run
from utils.pipeline_error import PipelineError
from viz_factory.viz_factory import VizFactory


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def _warning(problem: str, location: str = "plot") -> PipelineError:
    return PipelineError(component="VizFactory", problem=problem, location=location,
                         fix="Suggestion: do the thing.", who="data_analysis_recipe_author", category="visualization",
                         surface="notification", severity="warning")


def _two_plots(world: World) -> None:
    recipe = world.data_analysis_recipes_dir / "tiny.yaml"
    text = recipe.read_text()
    block = text.split("      p:\n", 1)[1]
    recipe.write_text(text + "      q:\n" + block)
    clear_data_analysis_recipe_cache()


def _export(tmp_path, monkeypatch, warnings_by_plot, two_plots=False, recipe_edit=None):
    """Run the real download generator; `warnings_by_plot` is added to the plot the library returns for that plot id."""
    world = World(tmp_path)
    if two_plots:
        _two_plots(world)
    if recipe_edit:
        recipe_edit(world)
    real_render = VizFactory.render

    def render(self, lf, cfg, plot_id, *a, **k):
        plot = real_render(self, lf, cfg, plot_id, *a, **k)
        plot._sparmvet.warnings.extend(warnings_by_plot.get(plot_id, []))
        return plot

    monkeypatch.setattr(VizFactory, "render", render)
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    z = zipfile.ZipFile(io.BytesIO(_run(_download_function(world, view, [], monkeypatch))[0]))
    run = yaml.safe_load(z.read(next(n for n in z.namelist() if n.endswith("effective_run.yaml"))).decode())
    readme = z.read(next(n for n in z.namelist() if n.endswith("/README.txt"))).decode()
    return z, run, readme


def test_no_warning_says_none_and_writes_an_empty_record(tmp_path, monkeypatch):
    z, run, readme = _export(tmp_path, monkeypatch, {})
    assert run["plot_warnings"] == {}
    assert "Plot warnings    : none" in readme
    assert "Plot warnings (these plots" not in readme
    assert not any(n.endswith("_ERROR.txt") for n in z.namelist())


def test_one_warning_is_in_the_readme_in_plain_words_and_in_the_record(tmp_path, monkeypatch):
    w = _warning("The font 'X' is not installed on this machine; 'DejaVu Sans' is used instead.")
    z, run, readme = _export(tmp_path, monkeypatch, {"p": [w]})
    text = plot_warning_text(w)
    assert "Plot warnings    : 1 (listed under 'Plot warnings' below)" in readme
    assert f"  p: {text}" in readme
    assert run["plot_warnings"]["p"] == [{"text": text, "problem": w.problem, "fix": w.fix,
                                           "component": "VizFactory", "location": "plot"}]
    assert any("/plots/p.png" in n for n in z.namelist()), "the picture is still exported"


def test_several_warnings_on_one_plot_are_all_written(tmp_path, monkeypatch):
    ws = [_warning("first problem"), _warning("second problem"), _warning("third problem")]
    _z, run, readme = _export(tmp_path, monkeypatch, {"p": ws})
    assert [r["problem"] for r in run["plot_warnings"]["p"]] == ["first problem", "second problem", "third problem"]
    assert "Plot warnings    : 3" in readme
    for w in ws:
        assert f"  p: {plot_warning_text(w)}" in readme


def test_the_same_warning_on_two_plots_is_written_for_each_plot(tmp_path, monkeypatch):
    w = _warning("same problem")
    _z, run, readme = _export(tmp_path, monkeypatch, {"p": [w], "q": [w]}, two_plots=True)
    assert set(run["plot_warnings"]) == {"p", "q"}
    assert "Plot warnings    : 2" in readme
    assert f"  p: {plot_warning_text(w)}" in readme and f"  q: {plot_warning_text(w)}" in readme


def test_only_the_plot_that_has_a_warning_is_named(tmp_path, monkeypatch):
    """A plot HOME never showed (nothing opened it) is drawn by the export and its warning is still collected; the
    plot beside it that has none is not named."""
    _z, run, readme = _export(tmp_path, monkeypatch, {"q": [_warning("only q")]}, two_plots=True)
    assert list(run["plot_warnings"]) == ["q"]
    assert "  q: only q" in readme and "  p: only q" not in readme


def test_the_real_missing_font_warning_of_the_library_reaches_the_bundle(tmp_path, monkeypatch):
    """No fake: the recipe asks for a font that is not installed; the library's own warning is written."""
    def ask_for_a_missing_font(world):
        recipe = world.data_analysis_recipes_dir / "tiny.yaml"
        text = recipe.read_text()
        assert "              params: {}\n" in text
        recipe.write_text(text.replace(
            "              params: {}\n",
            "              params: {}\n            - name: theme_bw\n              params: {base_family: NoSuchFontFamilyXyz}\n", 1))
        clear_data_analysis_recipe_cache()
    _z, run, readme = _export(tmp_path, monkeypatch, {}, recipe_edit=ask_for_a_missing_font)
    rows = run["plot_warnings"].get("p")
    assert rows and "NoSuchFontFamilyXyz" in rows[0]["text"], run["plot_warnings"]
    assert "NoSuchFontFamilyXyz" in readme
