"""A real export download from the running app (EXPORT-CHECK-1, partly automated).

Opens the app (qa app features), loads the dummy project, clicks the export button, unzips the bundle
and checks what the user is promised: the keys are recorded, the data files exist, and nothing
is refused. The refusal path (a file changed after the view was opened) is tested here too, by
changing a data file on disk after the view is open and restoring it afterwards.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_export_download.py -v
"""
import io
import re
import zipfile
from pathlib import Path

from PIL import Image, ImageChops

import pytest
from playwright.sync_api import Page
from shiny.run import ShinyAppProc

from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_shiny_smoke import _load_project, _navigate_to_mlst_plot, _open_filters_panel, _wait_shiny

DATA_DIR = Path("assets/test_data/1_test_data_ST22_dummy")


def _download(page: Page) -> zipfile.ZipFile:
    page.locator("#export_user_name").fill("autotest")
    with page.expect_download(timeout=120_000) as info:
        page.locator("#export_bundle_download").click()
    path = info.value.path()
    return zipfile.ZipFile(io.BytesIO(Path(path).read_bytes()))


def _open_export_panel(page: Page) -> None:
    if not page.locator("#export_bundle_download").is_visible():
        page.locator("#nav_accordion").get_by_text("Export").first.click()
        _wait_shiny(page)


@pytest.fixture(scope="module")
def loaded(page: Page, shiny_app: ShinyAppProc):
    _load_project(page, shiny_app.url)
    _open_export_panel(page)
    return page


def test_the_bundle_records_the_keys_and_has_the_data(loaded):
    z = _download(loaded)
    names = z.namelist()
    assert not any(n.endswith("EXPORT_NOT_CREATED.txt") for n in names), "the export was refused"
    readme = next(z.read(n).decode() for n in names if n.endswith("README.txt"))
    assert re.search(r"tier1_key=[0-9a-f]{64}", readme)
    assert re.search(r"tier2_key=([0-9a-f]{64}|none)", readme)
    assert re.search(r"Manifest SHA256\s*: [0-9a-f]{64}", readme)
    assert re.search(r"Data batch hash\s*: [0-9a-f]{64}", readme)
    assert any(n.endswith("T1_data.tsv") for n in names)
    assert any("/plots/" in n and not n.endswith("_ERROR.txt") for n in names)
    errors = {n: z.read(n).decode() for n in names if n.endswith("_ERROR.txt")}
    assert not errors, errors


def test_the_bundle_has_no_my_view_content_when_the_user_is_on_result(loaded):
    """Both plot and data choices start on Result: no T3 files, no filter trace."""
    names = _download(loaded).namelist()
    assert not any("T3_data" in n for n in names)
    assert not any(n.endswith("FILTERS.txt") for n in names)


def _plots(z: zipfile.ZipFile) -> dict:
    return {n.split("/plots/")[-1]: z.read(n) for n in z.namelist() if "/plots/" in n and n.endswith(".png")}


def test_exploration_filters_are_never_exported(loaded):
    """A filter tried while exploring (not sent to audit) must not change the bundle, from any view.

    The filter removes every row of the plot's dataset (year < 1900). If it leaked into the export, the
    plot of that dataset would be empty and differ from the export made without the filter.
    """
    before = _download(loaded)
    _open_filters_panel(loaded)
    _navigate_to_mlst_plot(loaded)
    loaded.wait_for_function("() => Array.from(document.querySelectorAll('#fb_col option')).some(o => o.value === 'year')",
                             timeout=30_000)
    loaded.locator("#fb_col").select_option("year"); _wait_shiny(loaded)
    loaded.locator("#fb_op").select_option("lt"); _wait_shiny(loaded)
    loaded.locator("#fb_value").fill("1900"); loaded.wait_for_timeout(200)
    loaded.locator("#filter_add_row").click(); _wait_shiny(loaded)
    loaded.locator("#filter_apply").click(); loaded.wait_for_timeout(1_500); _wait_shiny(loaded)
    for view in ("T3", "T2"):                              # looking at My view, then at Result
        loaded.locator(f"#plot_view input[value={view}]").check(force=True); _wait_shiny(loaded)
        _open_export_panel(loaded)
        after = _download(loaded)
        names = after.namelist()
        assert not any(n.endswith("FILTERS.txt") for n in names), "exploration filters were written to the bundle"
        assert not any("T3_data" in n for n in names), "T3 data written without an audited step"
        old, new = _plots(before), _plots(after)
        assert old.keys() == new.keys() and old
        for name in old:
            diff = ImageChops.difference(Image.open(io.BytesIO(old[name])).convert("RGB"),
                                         Image.open(io.BytesIO(new[name])).convert("RGB")).getbbox()
            assert diff is None, f"plot {name} changed by an exploration filter (plot view {view})"


def test_a_data_change_after_the_view_is_opened_blocks_the_export(loaded):
    files = {f: f.read_bytes() for f in DATA_DIR.rglob("*.tsv")}
    assert files, "no data file found to change"
    try:
        for f, original in files.items():
            f.write_bytes(original + b"\n")      # content changes, so the data hash changes
        z = _download(loaded)
        assert z.namelist() == ["EXPORT_NOT_CREATED.txt"]
        text = z.read("EXPORT_NOT_CREATED.txt").decode()
        assert "the data files" in text and "Reload the page" in text
    finally:
        for f, original in files.items():
            f.write_bytes(original)
