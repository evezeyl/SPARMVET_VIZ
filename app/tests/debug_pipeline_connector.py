#!/usr/bin/env python3
"""app/tests/debug_pipeline_connector.py
Headless verification of the production connector path (prefer_discovery mode).

Tests the full pipeline from profile load → connector → orchestrator → tier1 assembly
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

PIPELINE_TEST_PROFILE = ROOT / "config/deployment/pipeline_test/pipeline_test_profile.yaml"

PERSONAS = {
    "pipeline-static":             ROOT / "config/ui/templates/pipeline-static_template.yaml",
    "pipeline-exploration-simple": ROOT / "config/ui/templates/pipeline-exploration-simple_template.yaml",
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


# ── 1. Profile exists ──────────────────────────────────────────────────────
section("1. Profile")

if PIPELINE_TEST_PROFILE.exists():
    record("pipeline_test_profile.yaml exists", PASS)
else:
    record("pipeline_test_profile.yaml exists", FAIL, str(PIPELINE_TEST_PROFILE))
    sys.exit(1)

# ── 2. Boot with pipeline_test profile ────────────────────────────────────
section("2. Bootloader")

os.environ["SPARMVET_PROFILE"] = str(PIPELINE_TEST_PROFILE)
os.environ["SPARMVET_PERSONA"] = str(PERSONAS["pipeline-static"])

try:
    # Re-import fresh (clear module-level singleton)
    if "app.src.bootloader" in sys.modules:
        del sys.modules["app.src.bootloader"]
    from app.src.bootloader import bootloader  # noqa: E402

    raw_data_dir = bootloader.get_location("raw_data")
    manifests_dir = bootloader.get_location("manifests")
    prefer_discovery = bootloader.connector_config.get("prefer_discovery", False)

    record("Bootloader initialised", PASS)
    record("prefer_discovery flag", PASS if prefer_discovery else FAIL, str(prefer_discovery))
    record("raw_data_dir", INFO, str(raw_data_dir))
    record("manifests_dir", INFO, str(manifests_dir))
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
    import yaml

    manifest_id = bootloader.get_manifest_selector().get("fixed_manifest", "1_test_data_ST22_dummy")
    manifest_path = manifests_dir / f"{manifest_id}.yaml"
    record("Manifest path", PASS if manifest_path.exists() else FAIL, str(manifest_path))

    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)

    all_schemas: dict = {}
    all_schemas.update(manifest.get("data_schemas", {}))
    if "metadata_schema" in manifest:
        all_schemas["metadata_schema"] = manifest["metadata_schema"]
    all_schemas.update(manifest.get("additional_datasets_schemas", {}))

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
section("5. Full tier1 assembly (prefer_discovery=True)")

try:
    from app.modules.orchestrator import DataOrchestrator

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "anchor.parquet"

        orchestrator = DataOrchestrator(
            manifests_dir=manifests_dir,
            raw_data_dir=raw_data_dir,
            prefer_discovery=prefer_discovery,
        )

        lf = orchestrator.materialize_tier1(
            project_id=manifest_id,
            collection_id=list(manifest.get("join_manifests", {}).keys())[0],
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
section("6. Persona: pipeline-exploration-simple (same profile)")

os.environ["SPARMVET_PERSONA"] = str(PERSONAS["pipeline-exploration-simple"])
try:
    if "app.src.bootloader" in sys.modules:
        del sys.modules["app.src.bootloader"]
    from app.src.bootloader import bootloader as bl2  # noqa: E402

    ms = bl2.get_manifest_selector()
    record("Persona loaded", PASS, bl2.persona_display_name)
    record("manifest_selector.fixed_manifest", INFO, str(ms.get("fixed_manifest")))
    record("prefer_discovery", INFO, str(bl2.connector_config.get("prefer_discovery", False)))
    record("testing_mode", INFO, str(bl2.get_testing_mode()))
except Exception as e:
    record("Persona loaded", FAIL, str(e))
    traceback.print_exc()

# ── Summary ────────────────────────────────────────────────────────────────
section("Summary")

passes = sum(1 for _, s, _ in results if "PASS" in s)
fails  = sum(1 for _, s, _ in results if "FAIL" in s)
warns  = sum(1 for _, s, _ in results if "WARN" in s)
print(f"  {passes} pass  |  {warns} warn  |  {fails} fail\n")
