"""The red warning of the ids in HOME, in the browser (D-0582, D-0585, D-0613).

Run (one process; the first test starts its own app on a staged copy of the demo recipe `1_test_data_ST22_dummy`, the second under `pipeline-static`):
    PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_id_warning_browser.py -q

What a person sees, and is proved here:
- at the opening, above the tabs, a red warning: "ResFinder: 4 entities missing in original table. The recipe says: ..." with the place of the log and the button
  "I have read this"; the plots and the tables work before any click (nothing is blocked);
- one click: the warning becomes the quiet line "Id warnings read on <date>.", the click is written in the log of the ids, the plots still work; "Show again"
  opens it, "Hide" closes it; a new page on the same data shows the quiet line at once;
- the Export panel says one line about the log (red until read) and the bundle's README.txt and report.qmd say "automatic, no user" before the click and "read in the
  app" after it; the export is never refused;
- a static app features file (no filters, no audit) shows the same warning with the same button.

NOT covered: the look at other window sizes (the warning is a block of the page's width), a log folder that cannot be written (headless tests cover the words; making
the folder unwritable in a running app is the deployment's).
"""
import io
import re
import zipfile
from pathlib import Path

import yaml
from playwright.sync_api import Page, expect

from app.tests import gate_stage as g
from app.tests.gate_stage import wait_shiny

WARNING = "#id_warning_ui .spv-id-warning"
QUIET = "#id_warning_ui .spv-id-quiet"


def log_entries() -> list:
    path = g.WORK / "user" / "_id_logs" / f"{g.STAGE}.id_log.yaml"
    return yaml.safe_load(path.read_text())["entries"] if path.exists() else []


def open_home(page: Page, url: str) -> None:
    page.goto(url)
    page.wait_for_selector(".nav-link:has-text('Quality Control')", timeout=240_000)
    wait_shiny(page, 120_000)


def download_bundle(page: Page) -> zipfile.ZipFile:
    if not page.locator("#export_bundle_download").is_visible():
        page.locator("#nav_accordion").get_by_text("Export").first.click()
        wait_shiny(page)
    page.locator("#export_user_name").fill("idwarning")
    with page.expect_download(timeout=180_000) as info:
        page.locator("#export_bundle_download").click()
    return zipfile.ZipFile(io.BytesIO(Path(info.value.path()).read_bytes()))


def test_the_warning_blocks_nothing_one_click_makes_it_quiet_and_the_log_and_the_export_say_so(page: Page, tmp_path):
    with g.running_app(tmp_path) as (url, log):
        open_home(page, url)
        warning = page.locator(WARNING)
        expect(warning).to_be_visible(timeout=60_000)
        text = warning.inner_text()
        assert "ResFinder: 4 entities missing in original table. The recipe says: " in text and "Not Found, counted as 0" in text, text
        assert "Check the ids before you use these results." in text and f"{g.STAGE}.id_log.yaml" in text and "Every export holds it" in text
        expect(page.locator("#id_warning_read")).to_have_text("I have read this")
        box = warning.bounding_box()
        assert box["y"] < page.locator(".nav-link:has-text('Quality Control')").first.bounding_box()["y"], "the warning is above the tabs"
        assert warning.evaluate("e => getComputedStyle(e).backgroundColor") == "rgb(255, 224, 224)"

        # nothing is blocked before the click: another tab opens, a plot shows
        page.locator(".nav-link:has-text('Quality Control')").first.click()
        wait_shiny(page)
        expect(page.locator("#dynamic_tabs img").first).to_be_visible(timeout=60_000)
        # the log was written at the opening, by the app, with no user
        entries = log_entries()
        assert [e["kind"] for e in entries] == ["checks"] and entries[0]["who"] == "automatic, no user"
        # the Export panel: one line, red until read
        page.locator("#nav_accordion").get_by_text("Export").first.click()
        wait_shiny(page)
        expect(page.locator(".spv-id-export-line")).to_have_text("This export includes the log of the ids: 1 warning(s). Not read yet: see the warning at the top of HOME.")
        z = download_bundle(page)
        names = z.namelist()
        assert not any(n.endswith("EXPORT_NOT_CREATED.txt") for n in names), "an unread warning never refuses the export"
        readme = next(z.read(n).decode() for n in names if n.endswith("README.txt"))
        qmd = next(z.read(n).decode() for n in names if n.endswith("report.qmd"))
        for body in (readme, qmd):
            assert "missing in original table" in body and "Not Found, counted as 0" in body and "automatic, no user" in body, body[:300]
        assert "## The ids of the tables" in qmd and any(n.endswith("id_log.yaml") for n in names)

        # the click
        page.locator("#id_warning_read").click()
        expect(page.locator(QUIET)).to_contain_text("Id warnings read on ", timeout=30_000)
        expect(page.locator(WARNING)).to_have_count(0)
        entries = log_entries()
        assert [e["kind"] for e in entries] == ["checks", "read"] and entries[1]["who"] == "read in the app", entries
        assert entries[1]["recipe_sha256"] == entries[0]["recipe_sha256"] and entries[1]["data_batch_hash"] == entries[0]["data_batch_hash"]
        expect(page.locator("#dynamic_tabs img").first).to_be_visible()
        expect(page.locator("#export_id_warning_ui")).to_contain_text("Read on ")
        # show again, hide
        page.get_by_text("Show again").click()
        expect(page.locator(WARNING)).to_be_visible(timeout=30_000)
        assert page.locator("#id_warning_read").count() == 0 and "Read on " in page.locator(WARNING).inner_text()
        page.locator("#id_warning_ui").get_by_text("Hide").click()
        expect(page.locator(QUIET)).to_be_visible(timeout=30_000)
        # the export after the click
        z = download_bundle(page)
        readme = next(z.read(n).decode() for n in z.namelist() if n.endswith("README.txt"))
        assert "was read in the app on" in readme and "automatic, no user" not in readme.split("id_log.yaml", 1)[1].split("effective_run.yaml")[0]
        # a new page on the same data: the quiet line at once, nothing written again
        open_home(page, url)
        expect(page.locator(QUIET)).to_be_visible(timeout=60_000)
        assert page.locator(WARNING).count() == 0 and [e["kind"] for e in log_entries()] == ["checks", "read"]
        assert "Traceback" not in log.read_text()


def test_a_static_app_features_file_shows_the_same_warning_and_the_same_button(page: Page, tmp_path):
    with g.running_app(tmp_path, features="pipeline-static") as (url, log):
        open_home(page, url)
        expect(page.locator(WARNING)).to_be_visible(timeout=60_000)
        assert "ResFinder: 4 entities missing in original table" in page.locator(WARNING).inner_text()
        assert page.locator("#sidebar_filters").count() == 0, "this app features file has no filters: the warning does not depend on it"
        page.locator("#id_warning_read").click()
        expect(page.locator(QUIET)).to_contain_text("Id warnings read on ", timeout=30_000)
        assert [e["kind"] for e in log_entries()] == ["checks", "read"]
        expect(page.locator("#dynamic_tabs img").first).to_be_visible()
        assert "Traceback" not in log.read_text()
