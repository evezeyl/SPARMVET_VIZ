#!/usr/bin/env python3
"""app/tests/debug_pipeline_connector.py
Headless verification of the production connector path (data_lookup by_dataset_id).

Tests the full pipeline from deployment load → connector → orchestrator → tier1 assembly
without starting the Shiny UI. Confirms which schemas are discovered, which are
skipped, and what the assembled anchor looks like.

Run:
    PYTHONPATH=. python app/tests/debug_pipeline_connector.py

# @deps
# provides: debug:pipeline_connector_headless
# consumes: app/src/bootloader.py, app/modules/orchestrator.py
# consumed_by: manual @verify
# @end_deps
"""
import os
import sys
import tempfile
import traceback
from pathlib import Path

ROOT = Path(__file__).parents[2]

PASS = "✅ PASS"
FAIL = "❌ FAIL"
WARN = "⚠️  WARN"
INFO = "   "

PIPELINE_TEST_DEPLOYMENT = ROOT / "config/deployment/pipeline_test/pipeline_test.yaml"

APP_FEATURES = {
    "pipeline-static":             ROOT / "config/app_features/pipeline-static.yaml",
    "pipeline-exploration-simple": ROOT / "config/app_features/pipeline-exploration-simple.yaml",
}

results: list[tuple[str, str, str]] = []  # (test_name, status, detail)


def record(name, status, detail=""):
    results.append((name, status, detail))
    parts = status.split()
    icon = parts[0] if parts else "•"
    print(f"  {icon}  {name}" + (f": {detail}" if detail else ""))


def section(title):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


# ── 1. Deployment exists ──────────────────────────────────────────────────────
section("1. Deployment")

if PIPELINE_TEST_DEPLOYMENT.exists():
    record("pipeline_test.yaml exists", PASS)
else:
    record("pipeline_test.yaml exists", FAIL, str(PIPELINE_TEST_DEPLOYMENT))
    sys.exit(1)

# ── 2. Boot with pipeline_test deployment ────────────────────────────────────
section("2. Bootloader")

os.environ["SPARMVET_DEPLOYMENT"] = str(PIPELINE_TEST_DEPLOYMENT)
os.environ["SPARMVET_APP_FEATURES"] = str(APP_FEATURES["pipeline-static"])

try:
    # Re-import fresh (clear module-level singleton)
    if "app.src.bootloader" in sys.modules:
        del sys.modules["app.src.bootloader"]
    from app.src.bootloader import bootloader  # noqa: E402

    raw_data_dir = bootloader.get_location("raw_data")
    data_analysis_recipes_dir = bootloader.get_location("data_analysis_recipes")
    data_lookup = bootloader.data_lookup

    record("Bootloader initialised", PASS)
    record("data_lookup", PASS if data_lookup == "by_dataset_id" else FAIL, data_lookup)
    record("raw_data_dir", INFO, str(raw_data_dir))
    record("data_analysis_recipes_dir", INFO, str(data_analysis_recipes_dir))
    record("raw_data_dir exists", PASS if raw_data_dir.exists() else FAIL, str(raw_data_dir))
except Exception as e:
    record("Bootloader initialised", FAIL, str(e))
    traceback.print_exc()
    sys.exit(1)

# ── 3. Files in raw_data_dir ───────────────────────────────────────────────
section("3. Files in raw_data_dir (simulated pipeline output)")

files = sorted(raw_data_dir.glob("*.tsv")) if raw_data_dir.exists() else []
if files:
    record(f"{len(files)} TSV files found", PASS)
    for f in files:
        print(f"        {f.name}")
else:
    record("TSV files in raw_data_dir", FAIL, "none found")

# ── 4. Schema discovery dry-run ────────────────────────────────────────────
section("4. Schema → file discovery (ingestor.find_file)")

try:
    from ingestion.ingestor import DataIngestor
    from utils.config_loader import ConfigManager

    data_analysis_recipe_id = bootloader.get_data_analysis_recipe_selector().get("fixed_data_analysis_recipe", "1_test_data_ST22_dummy")
    data_analysis_recipe_path = data_analysis_recipes_dir / f"{data_analysis_recipe_id}.yaml"
    record("Data analysis recipe path", PASS if data_analysis_recipe_path.exists() else FAIL, str(data_analysis_recipe_path))

    # ConfigManager resolves the !include files, like the app does (plain yaml cannot).
    data_analysis_recipe = ConfigManager(str(data_analysis_recipe_path)).raw_config

    all_schemas: dict = {}
    all_schemas.update(data_analysis_recipe.get("data_schemas", {}))
    if "metadata_schema" in data_analysis_recipe:
        all_schemas["metadata_schema"] = data_analysis_recipe["metadata_schema"]
    all_schemas.update(data_analysis_recipe.get("additional_datasets_schemas", {}))

    ingestor = DataIngestor(data_dir=str(raw_data_dir))

    found, skipped = [], []
    for ds_id in all_schemas:
        hit = ingestor.find_file(ds_id)
        if hit and hit.exists():
            found.append((ds_id, hit.name))
        else:
            skipped.append(ds_id)

    record(f"{len(found)}/{len(all_schemas)} schemas discovered", PASS if not skipped else WARN)
    for ds_id, fname in found:
        print(f"        {PASS.split()[0]}  {ds_id:35s} → {fname}")
    for ds_id in skipped:
        print(f"        {FAIL.split()[0]}  {ds_id:35s} → not found")

except Exception as e:
    record("Schema discovery dry-run", FAIL, str(e))
    traceback.print_exc()

# ── 5. Full tier1 assembly ─────────────────────────────────────────────────
section("5. Full tier1 assembly (data_lookup=by_dataset_id)")

try:
    from app.modules.orchestrator import DataOrchestrator

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "anchor.parquet"

        orchestrator = DataOrchestrator(
            data_analysis_recipes_dir=data_analysis_recipes_dir,
            raw_data_dir=raw_data_dir,
            data_lookup=data_lookup,
        )

        lf = orchestrator.materialize_tier1(
            project_id=data_analysis_recipe_id,
            collection_id=list(data_analysis_recipe.get("joins", {}).keys())[0],
            output_path=out_path,
        )

        import polars as pl
        df = lf.collect()
        record("materialize_tier1 completed", PASS)
        record("Anchor shape", INFO, f"{df.shape[0]} rows × {df.shape[1]} cols")
        record("Anchor columns", INFO, ", ".join(df.columns[:10]) + ("…" if len(df.columns) > 10 else ""))

except Exception as e:
    record("materialize_tier1 completed", FAIL, str(e))
    traceback.print_exc()

# ── 6. Repeat for pipeline-exploration-simple ─────────────────────────────
section("6. App features: pipeline-exploration-simple (same deployment)")

os.environ["SPARMVET_APP_FEATURES"] = str(APP_FEATURES["pipeline-exploration-simple"])
try:
    if "app.src.bootloader" in sys.modules:
        del sys.modules["app.src.bootloader"]
    from app.src.bootloader import bootloader as bl2  # noqa: E402

    ms = bl2.get_data_analysis_recipe_selector()
    record("App features loaded", PASS, bl2.app_features_display_name)
    record("data_analysis_recipe_selector.fixed_data_analysis_recipe", INFO, str(ms.get("fixed_data_analysis_recipe")))
    record("data_lookup", INFO, bl2.data_lookup)
    record("testing_mode", INFO, str(bl2.get_testing_mode()))
except Exception as e:
    record("App features loaded", FAIL, str(e))
    traceback.print_exc()

# ── Summary ────────────────────────────────────────────────────────────────
section("Summary")

passes = sum(1 for _, s, _ in results if "PASS" in s)
fails  = sum(1 for _, s, _ in results if "FAIL" in s)
warns  = sum(1 for _, s, _ in results if "WARN" in s)
print(f"  {passes} pass  |  {warns} warn  |  {fails} fail\n")
