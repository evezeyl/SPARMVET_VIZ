"""Walk through the automatable steps of the retest procedure in a real browser.

It starts the app with the retest deployment (tmp/RETEST is deleted first), then runs, in order:
RT-01 load and row counts, RT-02 stored files, RT-03 reuse, RT-04 change one tier 2 step,
RT-05 move the step to tier 1, RT-06 change the data, RT-07 export refused after a change,
RT-30 renamed header and its fix, RT-31 select step with a misspelled column and its fix (both are refused by the
load gate at startup and listed as unavailable; after the fix the app is restarted, because the gate runs once per start).
It edits the retest files and puts them back afterwards, also on a failure.

The edits are the functions `with_...` below: text in, text out, and an error when the text to change is not found.
`app/tests/test_retest_data_analysis_recipes.py` checks them without a browser.

Needs the app environment (.venv) and Playwright. It is what a person would do by hand in
.claude/workflows/retest_procedure.md, so a failure here is a finding.

Example:
  PYTHONPATH=. .venv/bin/python assets/scripts/retest_walkthrough.py
"""
import argparse
import io
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

from playwright.sync_api import sync_playwright

from utils import action_names

REPO = Path(__file__).resolve().parents[2]
RETEST_TIER2 = REPO / "config/data_analysis_recipes/retest/retest_tier2.yaml"
BROKEN = REPO / "config/data_analysis_recipes/retest/retest_broken_header.yaml"
BAD_SELECT = REPO / "config/data_analysis_recipes/retest/retest_bad_select_column.yaml"
SAMPLES = REPO / "assets/test_data/retest/samples.tsv"
ANCHORS = REPO / "tmp/RETEST/user/anchors"
results = []

# The lines of retest_tier2.yaml that the edits of RT-04 and RT-05 look for (they carry the EDIT HERE marks).
TIER1_LINE = "      tier1: []            # EDIT HERE (RT-05): move the tier2 step below up to this list\n"
TIER2_LINE = "      tier2:               # EDIT HERE (RT-04): change value: 10 to value: 20\n"
THRESHOLD_LINE = "          value: 10\n"
NEXT_JOIN_LINE = "  All_samples:\n"


def _replace_once(text: str, old: str, new: str) -> str:
    """Replace the one place where `old` stands; fail when it is not there exactly once."""
    if text.count(old) != 1:
        raise ValueError(f"the retest recipe was reworded: {old.strip()!r} is found {text.count(old)} times, "
                         "expected once. Bring this script and the retest procedure in line with the recipe.")
    return text.replace(old, new)


def with_tier2_threshold(text: str, value: int) -> str:
    """RT-04: the tier 2 step of the join Result keeps the rows from `value` up, not from 10 up."""
    return _replace_once(text, THRESHOLD_LINE, f"          value: {value}\n")


def with_step_moved_to_tier1(text: str) -> str:
    """RT-05: the tier 2 step of the join Result is cut and put in its tier 1 list; tier 2 is left empty."""
    for line in (TIER1_LINE, TIER2_LINE, NEXT_JOIN_LINE):
        _replace_once(text, line, line)
    start = text.index(TIER2_LINE)
    end = text.index(NEXT_JOIN_LINE)
    step = text[start + len(TIER2_LINE):end]
    moved = text[:start] + "      tier2: []\n" + text[end:]
    return _replace_once(moved, TIER1_LINE, "      tier1:\n" + step)


def with_header_fixed(text: str) -> str:
    """RT-30: the recipe reads the file whose header has the declared column."""
    return _replace_once(text, "retest/genes_renamed_header.tsv", "retest/genes.tsv")


def with_select_column_fixed(text: str) -> str:
    """RT-31: the select step names the column the dataset has."""
    return _replace_once(text, "exprs: [sample_id, gene, phenotype]", "exprs: [sample_id, gene, predicted_phenotype]")


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}", flush=True)


def mtime(name: str) -> int:
    p = ANCHORS / name
    return p.stat().st_mtime_ns if p.exists() else 0


def wait_idle(page, timeout=20000):
    page.wait_for_function("() => !document.documentElement.classList.contains('shiny-busy')", timeout=timeout)
    time.sleep(1.2)
    page.wait_for_function("() => !document.documentElement.classList.contains('shiny-busy')", timeout=timeout)


def open_data_analysis_recipe(page, url, data_analysis_recipe):
    page.goto(url)
    page.wait_for_selector("#data_analysis_recipe_id", timeout=30000)
    page.locator("#data_analysis_recipe_id").select_option(data_analysis_recipe)
    wait_idle(page)
    time.sleep(2)
    wait_idle(page)


def rows(page, tier: str) -> int:
    page.locator(f"input[name=tier_toggle][value={tier}]").check(force=True)
    wait_idle(page)
    time.sleep(1.5)
    return page.locator("table tbody tr").count()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--headed", action="store_true", help="show the browser")
    args = ap.parse_args()

    originals = {p: p.read_text(encoding="utf-8") for p in (RETEST_TIER2, BROKEN, BAD_SELECT, SAMPLES)}
    shutil.rmtree(REPO / "tmp/RETEST", ignore_errors=True)
    env = {**os.environ, "PYTHONPATH": ".", "SPARMVET_DEPLOYMENT": "config/deployment/local/retest.yaml",
           "SPARMVET_APP_FEATURES": "qa"}
    srv = None

    def start_server():
        # The load gate (ADR-094) runs once per process, so a fixed recipe needs a new process.
        nonlocal srv
        if srv is not None:
            srv.terminate()
            srv.wait(timeout=20)
        port = free_port()
        srv = subprocess.Popen([str(REPO / ".venv/bin/shiny"), "run", "app/src/main.py", "--port", str(port)],
                               cwd=REPO, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        address = f"http://127.0.0.1:{port}/"
        for _ in range(60):
            try:
                urllib.request.urlopen(address, timeout=2)
                break
            except Exception:
                time.sleep(1)
        return address

    try:
        url = start_server()
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=not args.headed)
            page = browser.new_page(viewport={"width": 1700, "height": 950}, accept_downloads=True)

            # RT-01
            open_data_analysis_recipe(page, url, "retest_tier2")
            raw, result = rows(page, "T1"), rows(page, "T2")
            check("RT-01 Raw shows 12 rows, Result 8", (raw, result) == (12, 8), f"raw={raw} result={result}")
            check("RT-01 audit panel lists the tier 2 step", f"[Tier 2] {action_names.FILTER}" in page.inner_text("body"))
            # RT-02
            names = sorted(p.name for p in ANCHORS.glob("*.parquet"))
            check("RT-02 stored files: tier 1 and tier 2 of Result, no tier 2 for the unchanged join",
                  "Result__T2.parquet" in names and "Result.parquet" in names
                  and not any(n.endswith("__T2.parquet") and not n.startswith("Result") for n in names), str(names))
            # RT-03
            t2_0, t1_0 = mtime("Result__T2.parquet"), mtime("Result.parquet")
            rows(page, "T1"); rows(page, "T2"); open_data_analysis_recipe(page, url, "retest_tier2")
            check("RT-03 nothing is rewritten when nothing changed",
                  (mtime("Result__T2.parquet"), mtime("Result.parquet")) == (t2_0, t1_0))

            # RT-04
            RETEST_TIER2.write_text(with_tier2_threshold(originals[RETEST_TIER2], 20), encoding="utf-8")
            open_data_analysis_recipe(page, url, "retest_tier2")
            res = rows(page, "T2")
            check("RT-04 changing only the tier 2 step: Result shows 3 rows", res == 3, f"rows={res}")
            check("RT-04 tier 2 file rewritten, tier 1 file kept",
                  mtime("Result__T2.parquet") > t2_0 and mtime("Result.parquet") == t1_0)

            # RT-05
            RETEST_TIER2.write_text(with_step_moved_to_tier1(originals[RETEST_TIER2]), encoding="utf-8")
            open_data_analysis_recipe(page, url, "retest_tier2")
            raw5 = rows(page, "T1")
            check("RT-05 step moved to tier 1: Raw shows 8 rows", raw5 == 8, f"raw={raw5}")
            check("RT-05 the stored tier 2 file is gone", not (ANCHORS / "Result__T2.parquet").exists())

            # RT-06
            RETEST_TIER2.write_text(originals[RETEST_TIER2], encoding="utf-8")
            SAMPLES.write_text(originals[SAMPLES].rstrip("\n") + "\ns13\tA\t40\t2024\n", encoding="utf-8")
            open_data_analysis_recipe(page, url, "retest_tier2")
            raw6, res6 = rows(page, "T1"), rows(page, "T2")
            check("RT-06 new data row: Raw 13, Result 9", (raw6, res6) == (13, 9), f"raw={raw6} result={res6}")
            SAMPLES.write_text(originals[SAMPLES], encoding="utf-8")

            # RT-07
            open_data_analysis_recipe(page, url, "retest_tier2")
            rows(page, "T2")
            if not page.locator("#export_bundle_download").is_visible():
                page.locator("#nav_accordion").get_by_text("Export").first.click()
                wait_idle(page)
            SAMPLES.write_text(originals[SAMPLES].rstrip("\n") + "\ns14\tB\t50\t2024\n", encoding="utf-8")
            page.locator("#export_user_name").fill("walkthrough")
            with page.expect_download(timeout=120000) as dl:
                page.locator("#export_bundle_download").click()
            z = zipfile.ZipFile(io.BytesIO(Path(dl.value.path()).read_bytes()))
            only = [n for n in z.namelist() if not n.endswith("/")]
            check("RT-07 export refused after a change: only EXPORT_NOT_CREATED.txt",
                  len(only) == 1 and only[0].endswith("EXPORT_NOT_CREATED.txt"), str(only))
            SAMPLES.write_text(originals[SAMPLES], encoding="utf-8")

            # RT-30 and RT-31: the load gate lists a recipe it refuses, with the reason
            open_data_analysis_recipe(page, url, "retest_tier2")
            body = page.inner_text("body")
            check("RT-30 renamed header: the recipe is listed as unavailable, with the dataset and the column",
                  "retest_broken_header" in body
                  and "Column(s) ['predicted_phenotype'] declared in input_fields for 'Genes' not found" in body)
            check("RT-31 select step with a misspelled column: listed as unavailable, with the message of the engine",
                  "retest_bad_select_column" in body and 'unable to find column "phenotype"' in body)
            options = page.locator("#data_analysis_recipe_id option").evaluate_all("els => els.map(e => e.value)")
            check("RT-30 and RT-31 a refused recipe cannot be selected",
                  "retest_broken_header" not in options and "retest_bad_select_column" not in options, str(options))
            BROKEN.write_text(with_header_fixed(originals[BROKEN]), encoding="utf-8")
            BAD_SELECT.write_text(with_select_column_fixed(originals[BAD_SELECT]), encoding="utf-8")
            url = start_server()
            open_data_analysis_recipe(page, url, "retest_tier2")
            options = page.locator("#data_analysis_recipe_id option").evaluate_all("els => els.map(e => e.value)")
            check("RT-30 after the fix and a restart the recipe is selectable", "retest_broken_header" in options,
                  str(options))
            check("RT-31 after the fix and a restart the recipe is selectable", "retest_bad_select_column" in options,
                  str(options))
            browser.close()
    except Exception:
        srv.terminate()
        print("---- app output (tail) ----")
        print((srv.stdout.read() or "")[-3000:])
        raise
    finally:
        srv.terminate()
        for path, text in originals.items():
            path.write_text(text, encoding="utf-8")

    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)} of {len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
