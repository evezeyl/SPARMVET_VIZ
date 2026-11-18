"""EXPORT-FLAKE-1 in the browser: what the user sets in the Export panel stays set.

The Export panel used to be drawn again every time the plot tab changed (or `active_cfg()` updated) and every field of it
came back with its default: a ticked "Also include a reproducibility/reimport bundle" went back to unticked, and the
download then held no recipe and no data files while nothing on screen said so. These tests set every field of the panel,
change the plot tab, apply an exploration filter, wait, and read the fields back; one of them downloads the bundle and
reads what it records.

The static check of the same defect is `test_export_box_survives_plot_tab.py` (it reads the source and cannot see the
behaviour). The Export panel has no scope choice (D-0292): every export holds all plots.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_export_inputs_survive_plot_tab.py -v
"""
import io
import zipfile
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_shiny_smoke import (
    _load_data_analysis_recipe, _navigate_to_mlst_plot, _navigate_to_phenotype_plot, _open_filters_panel, _wait_shiny,
)

PHENOTYPE_PLOT = "phenotype_genome_length_fragmentation"
MLST_PLOT = "mlst_bar"


def _open_export_panel(page: Page) -> None:
    if not page.locator("#export_bundle_download").is_visible():
        page.locator("#nav_accordion").get_by_text("Export").first.click()
        _wait_shiny(page)


def _download(page: Page) -> zipfile.ZipFile:
    with page.expect_download(timeout=120_000) as info:
        page.locator("#export_bundle_download").click()
    return zipfile.ZipFile(io.BytesIO(Path(info.value.path()).read_bytes()))


def _fields(page: Page) -> dict:
    """Every field of the Export panel as the page shows it now."""
    return {
        "label": page.locator("#export_user_name").input_value(),
        "box": page.locator("#export_include_reproducibility").is_checked(),
        "preset": page.locator("input[name=export_preset]:checked").get_attribute("value"),
        "plot_format": page.locator("input[name=export_plot_format]:checked").get_attribute("value"),
        "report_format": page.locator("input[name=export_report_format]:checked").get_attribute("value"),
        "width": page.locator("#export_plot_width").input_value(),
        "height": page.locator("#export_plot_height").input_value(),
    }


def _wait_plot_tab_open(page: Page) -> None:
    """The plot tab change is over: the page is idle and the Export panel is on screen."""
    _wait_shiny(page)
    expect(page.locator("#export_bundle_download")).to_be_visible(timeout=15_000)


_DEFAULTS = {"label": "", "box": False, "preset": "web", "plot_format": "svg", "report_format": "html",
             "width": "8", "height": "5"}


def _set_defaults(page: Page) -> None:
    """Put every field back (the page is shared by the tests of the module)."""
    page.locator("#export_user_name").fill("")
    page.locator("#export_include_reproducibility").uncheck(force=True)
    page.locator("input[name=export_preset][value=web]").check(force=True)
    page.locator("input[name=export_plot_format][value=svg]").check(force=True)
    page.locator("input[name=export_report_format][value=html]").check(force=True)
    page.locator("#export_plot_width").fill("8")
    page.locator("#export_plot_height").fill("5")
    _wait_shiny(page)


@pytest.fixture(scope="module")
def loaded(page: Page, shiny_app: ShinyAppProc):
    _load_data_analysis_recipe(page, shiny_app.url)
    _open_export_panel(page)
    return page


@pytest.fixture()
def clean_panel(loaded):
    _open_export_panel(loaded)
    _set_defaults(loaded)
    yield loaded
    _open_export_panel(loaded)
    _set_defaults(loaded)


def test_every_field_of_the_panel_survives_a_plot_tab_change(clean_panel):
    """Set every field, change to another plot tab (another group), wait for any late update, read every field back."""
    page = clean_panel
    _navigate_to_mlst_plot(page)
    _open_export_panel(page)
    _wait_plot_tab_open(page)
    page.locator("#export_user_name").fill("keepme")
    page.locator("#export_include_reproducibility").check(force=True)
    page.locator("input[name=export_preset][value=publication]").check(force=True)
    page.locator("input[name=export_plot_format][value=pdf]").check(force=True)
    page.locator("input[name=export_report_format][value=pdf]").check(force=True)
    page.locator("#export_plot_width").fill("9")
    page.locator("#export_plot_height").fill("6")
    _wait_shiny(page)
    chosen = {"label": "keepme", "box": True, "preset": "publication", "plot_format": "pdf", "report_format": "pdf",
              "width": "9", "height": "6"}
    assert _fields(page) == chosen

    _navigate_to_phenotype_plot(page)          # another plot tab, in another group
    _wait_plot_tab_open(page)
    page.wait_for_timeout(3_000)               # a late reactive update would come in this time
    _wait_shiny(page)
    assert _fields(page) == chosen, "the Export panel lost what the user set when the plot tab changed"


def test_the_fields_survive_a_filter_applied_to_the_data(clean_panel):
    """An exploration filter changes the data the panels read; the Export panel keeps its fields."""
    page = clean_panel
    _navigate_to_mlst_plot(page)
    _open_export_panel(page)
    _wait_plot_tab_open(page)
    page.locator("#export_user_name").fill("afterfilter")
    page.locator("#export_include_reproducibility").check(force=True)
    page.locator("input[name=export_plot_format][value=png]").check(force=True)
    _wait_shiny(page)
    _open_filters_panel(page)
    page.wait_for_function("() => Array.from(document.querySelectorAll('#fb_col option')).some(o => o.value === 'year')",
                           timeout=30_000)
    page.locator("#fb_col").select_option("year"); _wait_shiny(page)
    page.locator("#fb_op").select_option("lt"); _wait_shiny(page)
    page.locator("#fb_value").fill("1900"); page.wait_for_timeout(200)
    page.locator("#filter_add_row").click(); _wait_shiny(page)
    try:
        page.locator("#filter_apply").click(); page.wait_for_timeout(2_000); _wait_shiny(page)
        _open_export_panel(page)
        got = _fields(page)
        assert (got["label"], got["box"], got["plot_format"]) == ("afterfilter", True, "png"), got
    finally:
        _open_filters_panel(page)
        reset = page.locator("#filter_reset")
        if reset.count() > 0 and reset.is_visible():
            reset.click(); _wait_shiny(page)


def test_a_ticked_box_after_a_tab_change_gives_the_reproducibility_part_and_the_bundle_says_so(clean_panel):
    """What the user would have met: tick, change the tab, download. The recipe and the data files are in the bundle and the
    README records the choice as the server read it; an unticked download records "not included"."""
    page = clean_panel
    _navigate_to_mlst_plot(page)
    _open_export_panel(page)
    _wait_plot_tab_open(page)
    page.locator("#export_user_name").fill("recorded")
    unticked = _download(page)
    readme_off = next(unticked.read(n).decode() for n in unticked.namelist() if n.endswith("README.txt"))
    assert "Reproducibility  : not included" in readme_off
    assert "Plot format      : svg" in readme_off
    assert not any("data_analysis_recipes_reproducibility/" in n for n in unticked.namelist())

    page.locator("#export_include_reproducibility").check(force=True)
    _wait_shiny(page)
    _navigate_to_phenotype_plot(page)
    _wait_plot_tab_open(page)
    page.wait_for_timeout(2_000)
    expect(page.locator("#export_include_reproducibility")).to_be_checked()
    ticked = _download(page)
    names = ticked.namelist()
    assert any("data_analysis_recipes_reproducibility/" in n for n in names)
    assert any("data_reproducibility/" in n for n in names)
    readme_on = next(ticked.read(n).decode() for n in names if n.endswith("README.txt"))
    assert "Reproducibility  : included" in readme_on
    # the confirmation the user sees after the download says it as well
    expect(page.locator(".shiny-notification").filter(has_text="Reproducibility part: included")).to_be_visible(
        timeout=15_000)
