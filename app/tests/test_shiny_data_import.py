"""Data Import accepts the file the engine reads and refuses the file it cannot read, in a real browser (D-0034, D-0050).

# @deps
# consumes: app/handlers/data_import_handlers.py, app/modules/data_import_check.py, app/tests/test_shiny_smoke.py
# @end_deps

The demo recipe `1_test_data_ST22_dummy` is open; the dataset is `metadata_schema` (the single file Data Import can replace under every
interactive app features file). The upload is the recipe's OWN data file, so a successful import replaces the file by an identical copy;
the test restores the original bytes in `finally` whatever happens, so the tracked test data is never left changed. The refused file has
the slug headers (`source`, `year`, `country`) instead of the file headers the recipe reads (`Source`, `Year`, `Country`): it must be
refused with the ingestion's reason and must not be written.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_data_import.py -q
"""
import os
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.conftest import shiny_app  # noqa: F401 — re-exports fixture
from app.tests.test_shiny_smoke import _INTERACTIVE_APP_FEATURES, _load_data_analysis_recipe, _wait_shiny

_LAUNCH_APP_FEATURES = os.environ.get("SPARMVET_APP_FEATURES", "developer")
REPO = Path(__file__).resolve().parents[2]
OWN_FILE = REPO / "assets" / "test_data" / "1_test_data_ST22_dummy" / "test_metadata_20260307_105756.tsv"


def _open_data_import(page: Page, url: str) -> None:
    _load_data_analysis_recipe(page, url)
    page.locator("#nav_accordion").get_by_text("Data Import").first.click()
    _wait_shiny(page)
    page.wait_for_selector("#data_import_multi_upload", state="attached", timeout=10_000)


def _assign_and_apply(page: Page, upload: Path) -> None:
    page.set_input_files("#data_import_multi_upload", str(upload))
    page.wait_for_selector("#data_import_assign_0", timeout=15_000)
    page.select_option("#data_import_assign_0", "metadata_schema")
    _wait_shiny(page)
    page.locator("#data_import_apply").click()


@pytest.mark.skipif(_LAUNCH_APP_FEATURES not in _INTERACTIVE_APP_FEATURES, reason="the upload controls only exist for interactive app features files")
def test_the_recipes_own_file_is_accepted_and_a_file_with_slug_headers_is_refused_and_not_written(page: Page, shiny_app: ShinyAppProc, tmp_path):
    original = OWN_FILE.read_bytes()
    slugs = tmp_path / "metadata_with_slug_headers.tsv"
    header, _, rest = original.decode().partition("\n")
    assert header == "sample_id\tSource\tYear\tCountry"
    slugs.write_text("sample_id\tsource\tyear\tcountry\n" + rest)
    try:
        _open_data_import(page, shiny_app.url)

        # the file with the slug headers: refused with the ingestion's reason, the data file is not written
        _assign_and_apply(page, slugs)
        error = page.locator(".spv-import-error")
        expect(error).to_contain_text("expected file headers", timeout=30_000)
        expect(error).to_contain_text("'Source'")
        assert "Did you mean" not in error.inner_text()
        assert OWN_FILE.read_bytes() == original

        # the recipe's own file: accepted, written, and the success notice names the file and its place
        _assign_and_apply(page, OWN_FILE)
        expect(page.locator("body")).to_contain_text("1 file(s) imported", timeout=60_000)
        _wait_shiny(page, 60_000)
        assert OWN_FILE.read_bytes() == original
    finally:
        OWN_FILE.write_bytes(original)
