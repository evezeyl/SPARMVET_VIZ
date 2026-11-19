"""A real export download from the running app (EXPORT-CHECK-1, partly automated).

Opens the app (qa app features), loads the dummy data analysis recipe, clicks the export button, unzips the bundle
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
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_shiny_smoke import (
    _load_data_analysis_recipe, _navigate_to_mlst_plot, _navigate_to_phenotype_plot, _open_filters_panel, _wait_shiny,
)

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
    _load_data_analysis_recipe(page, shiny_app.url)
    _open_export_panel(page)
    return page


def test_the_bundle_records_the_keys_and_has_the_data(loaded):
    """ADR-097/#45 corrected split: Mode 1 alone never includes the recipe or raw data
    — effective_run.yaml (the shared, machine-comparable verification record) is what
    carries the hashes instead, written unconditionally."""
    import yaml as _yaml

    z = _download(loaded)
    names = z.namelist()
    assert not any(n.endswith("EXPORT_NOT_CREATED.txt") for n in names), "the export was refused"
    readme = next(z.read(n).decode() for n in names if n.endswith("README.txt"))
    # Mode 1 alone never contains the recipe (ADR-091: not steps/, not audit_steps/ either)
    assert not any("data_analysis_recipes_reproducibility/" in n for n in names)
    assert not any("/audit_steps/" in n or "/steps/" in n for n in names)
    assert "effective_run.yaml" in readme
    assert re.search(r"tier1_key=[0-9a-f]{64}", readme)
    assert re.search(r"tier2_key=([0-9a-f]{64}|none)", readme)

    run_entry = next(n for n in names if n.endswith("effective_run.yaml"))
    run = _yaml.safe_load(z.read(run_entry).decode())
    assert len(run["data_analysis_recipe_sha256"]) == 64
    assert len(run["data_batch_hash"]) == 64
    assert len(run["t3_audit_steps_sha256"]) == 64
    assert run["git_commit"]
    assert "contact" in run and "contact_source" in run
    assert len([ln for ln in readme.splitlines() if ln.startswith("Contact")]) == 1
    assert "not attempted" in run["t3_translation_skipped"]   # Mode 2 not requested here
    # D-0248: the engine of each tier and plot, the theme as applied and the library versions are in the record
    record = run["engines"]
    assert record["tables"] and all(t["tier1"] == "python-polars" for t in record["tables"].values())
    assert record["plots"] and all(p["plot_engine"] == "python-plotnine" and p["drawn"] for p in record["plots"].values())
    assert set(record["library_versions"]) == {"python-polars", "python-plotnine"}

    # D-0292, D-0294: no scope choice, every plot is exported, as SVG when the user did not choose a format
    pictures = {m.group(1): m.group(2) for n in names if (m := re.search(r"/plots/([^/]+)\.(png|svg|pdf)$", n))}
    assert set(pictures) == set(record["plots"]) and len(pictures) > 1, "the bundle holds every plot of the recipe"
    assert set(pictures.values()) == {"svg"}, pictures
    assert "export_scope" not in readme and "export_scope" not in run
    print(f"EXPORT_PLOTS={len(pictures)} FORMATS={sorted(set(pictures.values()))}")

    assert any(n.endswith("T1_data.tsv") for n in names)
    assert any("/plots/" in n and not n.endswith("_ERROR.txt") for n in names)
    errors = {n: z.read(n).decode() for n in names if n.endswith("_ERROR.txt")}
    assert not errors, errors


def test_a_table_plotted_directly_has_its_t2_table_and_a_real_tier2_key(loaded):
    """RECIPE-DATASET-TIER2-1 (issue 77): ResFinder is read by a plot directly (it is not a join) and has
    tier-2 steps of its own: the bundle holds its T2 table, and its tier2_key is a hash, never `none`."""
    z = _download(loaded)
    names = z.namelist()
    assert any(n.endswith("/ResFinder/T2_data.tsv") for n in names), names
    readme = next(z.read(n).decode() for n in names if n.endswith("README.txt"))
    assert re.search(r"ResFinder: tier2_key=[0-9a-f]{64}\n", readme), readme
    qmd = next(z.read(n).decode() for n in names if n.endswith("report.qmd"))
    assert re.search(r"Tier 2 key \(ResFinder\) \| `[0-9a-f]{64}`", qmd)


def test_the_rerun_of_a_directly_plotted_table_equals_the_result_table_of_home(loaded):
    """Export with the reproducibility bundle, import it (the re-run) and compare the re-run's tier-2 table of
    ResFinder with the Result table that HOME shows for the original recipe."""
    import shutil
    import polars as pl
    from app.modules.orchestrator import DataOrchestrator
    from app.modules.bundle_importer import import_bundle
    from app.src.bootloader import bootloader as _bl

    loaded.locator("#export_include_reproducibility").check(force=True)
    _wait_shiny(loaded)
    z = _download(loaded)
    loaded.locator("#export_include_reproducibility").uncheck(force=True)
    _wait_shiny(loaded)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as out:
        for name in z.namelist():
            out.writestr(name, z.read(name))
    original_id = "1_test_data_ST22_dummy"
    recipes_dir = Path(_bl.data_analysis_recipes_dir)
    raw = Path(_bl.get_location("raw_data"))
    result = import_bundle(buf.getvalue(), bootloader=_bl)
    work = Path(__import__("tempfile").mkdtemp(prefix="rerun_t2_"))
    try:
        home_orch = DataOrchestrator(recipes_dir, raw)
        home_keys = home_orch.compute_data_analysis_recipe_keys(original_id)
        home_t2 = home_orch.materialize_tier2(original_id, "ResFinder", work / "home.parquet",
                                              keys=home_keys) if home_orch.materialize_tier1(
            original_id, "ResFinder", work / "home.parquet", keys=home_keys) is not None else None
        home_df = home_t2.collect()
        re_orch = DataOrchestrator(recipes_dir, raw, imports_dir=Path(_bl.get_imports_dir()))
        re_keys = re_orch.compute_data_analysis_recipe_keys(result.recipe_id)
        re_orch.materialize_tier1(result.recipe_id, "ResFinder", work / "re.parquet", keys=re_keys)
        re_df = re_orch.materialize_tier2(result.recipe_id, "ResFinder", work / "re.parquet", keys=re_keys).collect()
        assert "total_gene_count" in home_df.columns
        assert re_df.columns == home_df.columns
        assert re_df.equals(home_df), "the re-run's tier-2 table differs from HOME's Result table"
    finally:
        shutil.rmtree(work, ignore_errors=True)
        result.imported_recipe_path.unlink(missing_ok=True)
        shutil.rmtree(_bl.get_imports_dir() / result.recipe_id, ignore_errors=True)
        for p in (_bl.get_location("user_data") / "_sessions").glob("*/assembly.json"):
            if result.recipe_id in p.read_text():
                shutil.rmtree(p.parent, ignore_errors=True)


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
    # the pictures are compared as images: PNG (the default plot format is SVG, D-0294)
    loaded.locator("input[name=export_plot_format][value=png]").check(force=True)
    _wait_shiny(loaded)
    before = _download(loaded)
    _open_filters_panel(loaded)
    _navigate_to_mlst_plot(loaded)
    loaded.wait_for_function("() => Array.from(document.querySelectorAll('#fb_col option')).some(o => o.value === 'year')",
                             timeout=30_000)
    loaded.locator("#fb_col").select_option("year"); _wait_shiny(loaded)
    loaded.wait_for_function("() => Array.from(document.querySelectorAll('#fb_op option')).some(o => o.value === 'lt')", timeout=20_000)
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


def test_mode2_checkbox_adds_the_reproducibility_bundle(loaded):
    """ADR-097/#45: opt-in, additive. Unchecked = unchanged bundle; checked = the new
    folders appear alongside everything that was already there."""
    import yaml as _yaml

    def _relative(names):
        # Each download's top folder is "<timestamp>_<label>/..." — strip it so two
        # downloads taken seconds apart (different timestamps) compare on content.
        return {n.split("/", 1)[1] if "/" in n else n for n in names}

    before = _download(loaded)
    before_names = _relative(before.namelist())

    loaded.locator("#export_include_reproducibility").check(force=True)
    _wait_shiny(loaded)
    after = _download(loaded)
    after_names_raw = after.namelist()
    after_names = _relative(after_names_raw)
    loaded.locator("#export_include_reproducibility").uncheck(force=True)
    _wait_shiny(loaded)

    # Additive — nothing from the unchecked bundle disappears.
    assert before_names <= after_names
    after_names = after_names_raw  # the rest of this test wants real zip entry names

    recipe_entries = [n for n in after_names if "/data_analysis_recipes_reproducibility/" in n
                       and n.endswith(".yaml") and not n.endswith("effective_run.yaml")]
    assert recipe_entries, after_names
    run_entries = [n for n in after_names if n.endswith("effective_run.yaml")]
    assert run_entries, after_names
    assert any("/data_reproducibility/" in n for n in after_names), after_names

    errors = {n: after.read(n).decode() for n in after_names if "reproducibility" in n and n.endswith("_ERROR.txt")}
    assert not errors, errors

    run = _yaml.safe_load(after.read(run_entries[0]).decode())
    assert len(run["data_analysis_recipe_sha256"]) == 64
    assert len(run["data_batch_hash"]) == 64
    assert len(run["t3_audit_steps_sha256"]) == 64
    assert run["engine_fingerprint"]
    assert isinstance(run["containerized"], bool)
    assert isinstance(run["data_source_paths"], dict) and run["data_source_paths"]
    assert "seeds_per_plot" in run
    # Mode 2 was requested in this download — the translator actually ran, so this is
    # a dict (possibly empty), not the "not attempted" placeholder.
    assert isinstance(run["t3_translation_skipped"], dict)

    # effective_run.yaml is unconditional — the earlier, Mode-1-only download must
    # already have one, with the same recipe/data hashes, but no translation attempted.
    before_run_entry = next(n for n in before.namelist() if n.endswith("effective_run.yaml"))
    before_run = _yaml.safe_load(before.read(before_run_entry).decode())
    assert before_run["data_analysis_recipe_sha256"] == run["data_analysis_recipe_sha256"]
    assert before_run["data_batch_hash"] == run["data_batch_hash"]
    assert "not attempted" in before_run["t3_translation_skipped"]

    # The frozen recipe copy must itself be valid, reloadable YAML with no leftover
    # ConfigManager-internal `plots:` mirror key (confirmed live earlier to break reload).
    frozen = _yaml.safe_load(after.read(recipe_entries[0]).decode())
    assert "plots" not in frozen
    assert "joins" in frozen


def test_import_a_bundle_reports_the_four_legs(loaded, tmp_path):
    """REPRO-IMPORT-1 (#48): round-trip a real Mode 2 bundle through the running app's
    own Import control (reachable from the Export panel, no test_lab_enabled/blueprint_enabled
    needed) and confirm it reports all four verification legs."""
    loaded.locator("#export_include_reproducibility").check(force=True)
    _wait_shiny(loaded)
    z = _download(loaded)
    loaded.locator("#export_include_reproducibility").uncheck(force=True)
    _wait_shiny(loaded)

    bundle_path = tmp_path / "bundle.zip"
    # Rebuild the zip bytes from the already-open ZipFile's entries (it doesn't expose
    # its original source bytes directly).
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as out:
        for name in z.namelist():
            out.writestr(name, z.read(name))
    bundle_path.write_bytes(buf.getvalue())

    loaded.locator("#import_bundle_upload").set_input_files(str(bundle_path))
    loaded.wait_for_function(
        "() => document.querySelector('#import_bundle_report') && "
        "document.querySelector('#import_bundle_report').textContent.includes('Imported as')",
        timeout=30_000,
    )
    _wait_shiny(loaded)
    report_text = loaded.locator("#import_bundle_report").inner_text()
    recipe_id_match = re.search(r"Imported as '([^']+)'", report_text)
    from app.src.bootloader import bootloader as _bl
    raw_before = {str(p) for p in DATA_DIR.parent.rglob("*")}
    try:
        # inside the try so a missing leg still runs the clean-up below
        for leg in ("data", "engine", "recipe", "t3 steps"):
            expect(loaded.locator("#import_bundle_report")).to_contain_text(leg, ignore_case=True, timeout=15_000)
        report_text = loaded.locator("#import_bundle_report").inner_text()
        assert "Imported as" in report_text
        for leg in ("data", "engine", "recipe", "t3 steps"):
            assert leg in report_text.lower(), report_text
        # IMPORT-PATH-1: the data of the import is stored by dataset id in the folder of its own import,
        # the recipe's path is untouched, and nothing is written into the deployment's raw data.
        recipe_id = recipe_id_match.group(1)
        import_data = _bl.get_imports_dir() / recipe_id / "data"
        assert import_data.is_dir() and any(import_data.glob("*.tsv")), import_data
        assert {str(p) for p in DATA_DIR.parent.rglob("*")} == raw_before
        # the importing user sees the data leg as match: the hash covers the files the recipe reads
        assert re.search(r"data\s*:\s*match", report_text, re.IGNORECASE), report_text
    finally:
        # Import writes real files into the project's own recipes and user_data locations
        # (not tmp_path) - clean up what this test created.
        if recipe_id_match:
            import shutil
            recipe_id = recipe_id_match.group(1)
            (_bl.data_analysis_recipes_dir / f"{recipe_id}.yaml").unlink(missing_ok=True)
            shutil.rmtree(_bl.get_imports_dir() / recipe_id, ignore_errors=True)
            for p in (_bl.get_location("user_data") / "_sessions").glob("*/assembly.json"):
                if recipe_id in p.read_text():
                    shutil.rmtree(p.parent, ignore_errors=True)


def test_the_export_records_the_seed_the_recipe_writes_and_writes_it_into_the_reproducibility_recipe(loaded):
    """SEED-HOLDS-1 (ADR-104, Eve 2026-11-15): the plot of the dummy recipe writes `random_state: 0` on its jitter
    layer. HOME draws no seed: the export draws the plot with that number, records it as `recipe`, and the
    reproducibility recipe carries it. The edge cases (no seed written, a pin, two sessions, the reference pane) are
    in test_shiny_seed_places.py, which runs its own apps."""
    import yaml as _yaml

    pid = "phenotype_genome_length_fragmentation"
    _navigate_to_phenotype_plot(loaded)
    _open_export_panel(loaded)
    loaded.locator("#export_include_reproducibility").check(force=True)
    _wait_shiny(loaded)
    try:
        z = _download(loaded)
    finally:
        loaded.locator("#export_include_reproducibility").uncheck(force=True)
        _wait_shiny(loaded)
        qc_tab = loaded.locator(".nav-link:has-text('Quality Control')")
        if qc_tab.count() > 0:
            qc_tab.first.click()
            _wait_shiny(loaded)
    run = _yaml.safe_load(z.read(next(n for n in z.namelist() if n.endswith("effective_run.yaml"))).decode())
    assert run["seeds_per_plot"][pid] == 0 and run["seed_source_per_plot"][pid] == "recipe"
    assert [(r["seed"], r["source"]) for r in run["seeds_per_layer"][pid]] == [(0, "recipe")]
    assert run["seeds_added_to_recipe"] == []
    recipe_name = next(n for n in z.namelist() if "/data_analysis_recipes_reproducibility/" in n
                       and n.endswith(".yaml") and not n.endswith("effective_run.yaml"))
    recipe = _yaml.safe_load(z.read(recipe_name).decode())
    spec = next(g["plots"][pid] for g in recipe["analysis_groups"].values() if pid in g["plots"])
    assert {l["params"].get("random_state") for l in spec["layers"]
            if (l.get("params") or {}).get("position") == "jitter"} == {0}


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
