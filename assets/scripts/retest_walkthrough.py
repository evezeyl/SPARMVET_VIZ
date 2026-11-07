"""Walk through the automatable steps of the retest procedure in a real browser.

It starts the app with the retest deployment (tmp/RETEST is deleted first), then runs, in order:
RT-01 load and row counts, RT-02 stored files, RT-03 reuse, RT-04 change one tier 2 step,
RT-05 move the step to tier 1, RT-06 change the data, RT-07 export refused after a change,
RT-30 renamed header and its fix, RT-31 declared field with no column.
It edits the retest files and puts them back afterwards, also on a failure.

Needs the app environment (.venv) and Playwright. It is what a person would do by hand in
.claude/tasks/retest_procedure_2026-11-06.md, so a failure here is a finding.

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

REPO = Path(__file__).resolve().parents[2]
RECIPE = REPO / "config/data_analysis_recipes/retest/retest_tier2.yaml"
BROKEN = REPO / "config/data_analysis_recipes/retest/retest_broken_header.yaml"
SAMPLES = REPO / "assets/test_data/retest/samples.tsv"
ANCHORS = REPO / "tmp/RETEST/user/anchors"
results = []


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


def open_project(page, url, project):
    page.goto(url)
    page.wait_for_selector("#data_analysis_recipe_id", timeout=30000)
    page.locator("#data_analysis_recipe_id").select_option(project)
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

    originals = {p: p.read_text(encoding="utf-8") for p in (RECIPE, BROKEN, SAMPLES)}
    shutil.rmtree(REPO / "tmp/RETEST", ignore_errors=True)
    port = free_port()
    url = f"http://127.0.0.1:{port}/"
    env = {**os.environ, "PYTHONPATH": ".", "SPARMVET_DEPLOYMENT": "config/deployment/local/retest.yaml",
           "SPARMVET_APP_FEATURES": "qa"}
    srv = subprocess.Popen([str(REPO / ".venv/bin/shiny"), "run", "app/src/main.py", "--port", str(port)],
                           cwd=REPO, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        for _ in range(60):
            try:
                urllib.request.urlopen(url, timeout=2)
                break
            except Exception:
                time.sleep(1)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=not args.headed)
            page = browser.new_page(viewport={"width": 1700, "height": 950}, accept_downloads=True)

            # RT-01
            open_project(page, url, "retest_tier2")
            raw, result = rows(page, "T1"), rows(page, "T2")
            check("RT-01 Raw shows 12 rows, Result 8", (raw, result) == (12, 8), f"raw={raw} result={result}")
            check("RT-01 audit panel lists the tier 2 step", "filter_range" in page.inner_text("body"))
            # RT-02
            names = sorted(p.name for p in ANCHORS.glob("*.parquet"))
            check("RT-02 stored files: tier 1 and tier 2 of Result, no tier 2 for the unchanged join",
                  "Result__T2.parquet" in names and "Result.parquet" in names
                  and not any(n.endswith("__T2.parquet") and not n.startswith("Result") for n in names), str(names))
            # RT-03
            t2_0, t1_0 = mtime("Result__T2.parquet"), mtime("Result.parquet")
            rows(page, "T1"); rows(page, "T2"); open_project(page, url, "retest_tier2")
            check("RT-03 nothing is rewritten when nothing changed",
                  (mtime("Result__T2.parquet"), mtime("Result.parquet")) == (t2_0, t1_0))

            # RT-04
            RECIPE.write_text(originals[RECIPE].replace("min: 10", "min: 20"), encoding="utf-8")
            open_project(page, url, "retest_tier2")
            res = rows(page, "T2")
            check("RT-04 changing only the tier 2 step: Result shows 3 rows", res == 3, f"rows={res}")
            check("RT-04 tier 2 file rewritten, tier 1 file kept",
                  mtime("Result__T2.parquet") > t2_0 and mtime("Result.parquet") == t1_0)

            # RT-05
            text = originals[RECIPE]
            text = text.replace("tier1: []            # EDIT HERE (test 3): move the tier2 step below up to this list",
                                "tier1:\n        - action: filter_range\n          columns: [value]\n          min: 10")
            i = text.index("tier2:", text.index("\njoins:"))
            j = text.index("min: 10", text.index("- action", i)) + len("min: 10")
            text = text[:i] + "tier2: []" + text[j:]
            RECIPE.write_text(text, encoding="utf-8")
            open_project(page, url, "retest_tier2")
            raw5 = rows(page, "T1")
            check("RT-05 step moved to tier 1: Raw shows 8 rows", raw5 == 8, f"raw={raw5}")
            check("RT-05 the stored tier 2 file is gone", not (ANCHORS / "Result__T2.parquet").exists())

            # RT-06
            RECIPE.write_text(originals[RECIPE], encoding="utf-8")
            SAMPLES.write_text(originals[SAMPLES].rstrip("\n") + "\ns13\tA\t40\t2024\n", encoding="utf-8")
            open_project(page, url, "retest_tier2")
            raw6, res6 = rows(page, "T1"), rows(page, "T2")
            check("RT-06 new data row: Raw 13, Result 9", (raw6, res6) == (13, 9), f"raw={raw6} result={res6}")
            SAMPLES.write_text(originals[SAMPLES], encoding="utf-8")

            # RT-07
            open_project(page, url, "retest_tier2")
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

            # RT-30
            open_project(page, url, "retest_broken_header")
            body = page.inner_text("body")
            check("RT-30 broken header: banner names the dataset and the missing column",
                  "Data Assembly Failed" in body and "Genes" in body and "predicted_phenotype" in body)
            BROKEN.write_text(originals[BROKEN].replace("genes_renamed_header.tsv", "genes.tsv"), encoding="utf-8")
            open_project(page, url, "retest_broken_header")
            check("RT-30 after the fix the banner is gone", "Data Assembly Failed" not in page.inner_text("body"))
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

    # RT-31 (no browser)
    from app.modules.data_analysis_recipe_validator import validate_data_analysis_recipe_data
    problems = validate_data_analysis_recipe_data(
        REPO / "config/data_analysis_recipes/retest/retest_bad_output_field.yaml", REPO / "assets/test_data")
    check("RT-31 the declared column with no data is found, with a tip",
          any("phenotype" in str(p) and "predicted_phenotype" in str(p) for p in problems), str(problems)[:120])

    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)} of {len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
