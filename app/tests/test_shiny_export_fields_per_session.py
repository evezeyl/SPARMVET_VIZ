"""The Export fields belong to the loaded recipe and its session (D-0288, D-0289, D-0291, D-0294, D-0296), in the browser.

Quality, plot format, report format, plot width, plot height and the mode tick are remembered while the app runs, one set per
session (recipe plus data batch): recipe A, then B, then A shows A's choices again; a first visit shows the defaults; nothing
leaks from one session to another; Home to Blueprint and back keeps them. The bundle label is the one field that is NOT
remembered: it is empty on every load, switch and return. The Export button stays grey from a value the SERVER sets
(a recipe switch) until the server holds the shown values (D-0270). Every export holds all plots of the recipe (D-0292, D-0295).

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_export_fields_per_session.py -v
"""
import io
import re
import zipfile
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.modules.cache_keys import load_data_analysis_recipe
from app.src.bootloader import bootloader
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_shiny_smoke import _choose_recipe, _open_app, _wait_shiny

A = "1_test_data_ST22_dummy"
B = "2_test_data_ST22_dummy"
BTN = "#export_bundle_download"
DEFAULTS = {"label": "", "box": False, "preset": "web", "plot_format": "svg", "report_format": "html",
            "width": "8", "height": "5"}


def _open_export_panel(page: Page) -> None:
    if not page.locator(BTN).is_visible():
        page.locator("#nav_accordion").get_by_text("Export").first.click()
        _wait_shiny(page)


def _fields(page: Page) -> dict:
    return {
        "label": page.locator("#export_user_name").input_value(),
        "box": page.locator("#export_include_reproducibility").is_checked(),
        "preset": page.locator("input[name=export_preset]:checked").get_attribute("value"),
        "plot_format": page.locator("input[name=export_plot_format]:checked").get_attribute("value"),
        "report_format": page.locator("input[name=export_report_format]:checked").get_attribute("value"),
        "width": page.locator("#export_plot_width").input_value(),
        "height": page.locator("#export_plot_height").input_value(),
    }


def _set(page: Page, *, label="", box=False, preset="web", plot_format="svg", report_format="html", width="8", height="5"):
    page.locator("#export_user_name").fill(label)
    (page.locator("#export_include_reproducibility").check if box else page.locator("#export_include_reproducibility").uncheck)(force=True)
    page.locator(f"input[name=export_preset][value={preset}]").check(force=True)
    page.locator(f"input[name=export_plot_format][value={plot_format}]").check(force=True)
    page.locator(f"input[name=export_report_format][value={report_format}]").check(force=True)
    page.locator("#export_plot_width").fill(width)
    page.locator("#export_plot_height").fill(height)
    _wait_shiny(page)
    expect(page.locator(BTN)).not_to_have_class(re.compile("export-not-ready"), timeout=15_000)


def _expect_fields(page: Page, expected: dict, why: str) -> None:
    """The fields read back as expected; a server-side update arrives a moment after the switch, so wait for it."""
    try:
        page.wait_for_function(
            """(e) => {
                const v = (s) => document.querySelector(s);
                const c = (n) => { const r = document.querySelector(`input[name=${n}]:checked`); return r && r.value; };
                return v('#export_user_name').value === e.label && v('#export_include_reproducibility').checked === e.box
                    && c('export_preset') === e.preset && c('export_plot_format') === e.plot_format
                    && c('export_report_format') === e.report_format && v('#export_plot_width').value === e.width
                    && v('#export_plot_height').value === e.height;
            }""", arg=expected, timeout=15_000)
    except Exception:
        pass
    _wait_shiny(page)
    assert _fields(page) == expected, why


def _download(page: Page) -> zipfile.ZipFile:
    with page.expect_download(timeout=180_000) as info:
        page.locator(BTN).click()
    return zipfile.ZipFile(io.BytesIO(Path(info.value.path()).read_bytes()))


def _readme(z: zipfile.ZipFile) -> str:
    return next(z.read(n).decode() for n in z.namelist() if n.endswith("README.txt"))


def _pictures(z: zipfile.ZipFile) -> dict:
    out = {}
    for n in z.namelist():
        m = re.search(r"/plots/([^/]+)\.(png|svg|pdf)$", n)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def _plot_ids_of(recipe_id: str) -> set:
    cfg = load_data_analysis_recipe(bootloader.available_data_analysis_recipes[recipe_id]).config.raw_config
    return {p for g in cfg["analysis_groups"].values() for p in g.get("plots", {})}


@pytest.fixture(scope="module")
def on_a(page: Page, shiny_app: ShinyAppProc):
    _open_app(page, shiny_app.url)
    _choose_recipe(page, A)
    page.wait_for_selector(".nav-link:has-text('Quality Control')", timeout=60_000)
    _wait_shiny(page)
    _open_export_panel(page)
    return page


def test_the_fields_follow_the_session_and_the_label_is_never_remembered(on_a):
    page = on_a
    # a first visit shows the defaults (SVG and HTML, D-0294)
    _expect_fields(page, DEFAULTS, "first visit of A")
    chosen_a = {"label": "labelA", "box": True, "preset": "publication", "plot_format": "png", "report_format": "docx",
                "width": "9", "height": "6"}
    _set(page, **chosen_a)
    _expect_fields(page, chosen_a, "A as set")

    # recipe B: its own session, its own (default) fields, an empty label
    _choose_recipe(page, B)
    _expect_fields(page, DEFAULTS, "B must start from the defaults: nothing of A leaks into B, and the label is empty")
    chosen_b = {"label": "labelB", "box": False, "preset": "web", "plot_format": "pdf", "report_format": "html",
                "width": "11", "height": "5"}
    _set(page, **chosen_b)

    # back to A: A's choices, the label empty
    _choose_recipe(page, A)
    _expect_fields(page, {**chosen_a, "label": ""}, "back on A: A's choices are shown again, the label is not remembered")
    # back to B: B's choices, the label empty
    _choose_recipe(page, B)
    _expect_fields(page, {**chosen_b, "label": ""}, "back on B: B's choices, no value of A")

    # Home to Blueprint and back keeps the fields and empties the label
    page.locator("#export_user_name").fill("typed before leaving")
    page.locator("#sidebar_nav").get_by_text("Blueprint Architect").first.click()
    _wait_shiny(page)
    page.get_by_text("Home", exact=True).first.click()
    _wait_shiny(page)
    _open_export_panel(page)
    _expect_fields(page, {**chosen_b, "label": ""}, "Home -> Blueprint -> Home: the fields are kept, the label is empty")

    # the export of A holds A's values and ALL plots of A
    _choose_recipe(page, A)
    _expect_fields(page, {**chosen_a, "label": ""}, "A again before the export")
    page.locator("#export_user_name").fill("labelA")
    _wait_shiny(page)
    expect(page.locator(BTN)).not_to_have_class(re.compile("export-not-ready"), timeout=15_000)
    z = _download(page)
    names = z.namelist()
    assert not any(n.endswith("EXPORT_NOT_CREATED.txt") for n in names)
    pictures = _pictures(z)
    assert set(pictures.values()) == {"png"}, "the plot format of A (png) is in the bundle"
    assert set(pictures) == _plot_ids_of(A), "the bundle holds ALL plots of the recipe"
    readme = _readme(z)
    assert "publication (DPI=600, 9.0×6.0 in)" in readme and "Plot format      : png" in readme
    assert "Reproducibility  : included" in readme
    assert any("data_analysis_recipes_reproducibility/" in n for n in names), "the mode tick of A is in the bundle"
    assert any(n.endswith("report.docx") or n.endswith("report_RENDER_FAILED.txt") and "report.docx" in z.read(n).decode()
               for n in names), "the report format of A (docx) is in the bundle"


def test_the_mode_tick_does_not_change_which_plots_are_exported(on_a):
    page = on_a
    _choose_recipe(page, B)
    _open_export_panel(page)
    _set(page, label="plain", box=False)
    plain = _pictures(_download(page))
    _set(page, label="ticked", box=True)
    ticked = _pictures(_download(page))
    _set(page, box=False)
    assert set(plain) == set(ticked) == _plot_ids_of(B), (plain, ticked)


_HOOK = """() => {
    // a press on Export in the very instant the page applies the plot format that the SERVER set
    window.__presses = [];
    window.jQuery(document).on('shiny:inputchanged', (e) => {
        if (e.name !== 'export_plot_format' || window.__presses.length) return;
        const ev = new MouseEvent('click', {bubbles: true, cancelable: true});
        document.querySelector('#export_bundle_download').dispatchEvent(ev);
        window.__presses.push({prevented: ev.defaultPrevented,
                               grey: document.querySelector('#export_bundle_download').classList.contains('export-not-ready')});
    });
}"""


def test_a_value_set_by_the_server_greys_the_button_until_the_server_holds_it(on_a):
    """A recipe switch makes the server set the fields. A press at the instant the page applies them is refused; when the
    button is ready again, the bundle holds the SHOWN values (B's defaults), not the values of the recipe left."""
    page = on_a
    _choose_recipe(page, A)
    _open_export_panel(page)
    _set(page, label="", box=False, plot_format="png")
    downloads = []
    page.on("download", lambda d: downloads.append(d))
    page.evaluate(_HOOK)
    page.locator("#data_analysis_recipe_id").select_option(B)
    page.wait_for_function("() => window.__presses && window.__presses.length > 0", timeout=30_000)
    press = page.evaluate("() => window.__presses[0]")
    assert press == {"prevented": True, "grey": True}, f"the button was usable while the server did not hold the shown values: {press}"
    _wait_shiny(page, 30_000)
    expect(page.locator(BTN)).not_to_have_class(re.compile("export-not-ready"), timeout=15_000)
    assert downloads == [], "the press on the grey button started a download"
    expect(page.locator("input[name=export_plot_format][value=svg]")).to_be_checked()
    z = _download(page)
    assert set(_pictures(z).values()) == {"svg"}, "the bundle holds what the panel shows (B's default), not A's png"
    assert set(_pictures(z)) == _plot_ids_of(B)
    _choose_recipe(page, A)
