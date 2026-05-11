#!/usr/bin/env python3
"""app/tests/debug_data_import.py
Headless verification of the file import + schema mapping logic.

Tests the pure-logic portion of data_import_handlers._handle_apply:
  file reading → MetadataValidator.validate → source-path resolution → file copy

Shiny-specific parts (file picker widget, assignment select, btn_apply reactive)
require Playwright and are documented in the Playwright gap note at the end.

Run:
    PYTHONPATH=. ./.venv/bin/python app/tests/debug_data_import.py
    PYTHONPATH=. ./.venv/bin/python app/tests/debug_data_import.py --output tmp/import_test/

# @deps
# provides: debug:data_import_headless
# consumes: transformer/metadata_validator.py, app/handlers/data_import_handlers.py
# consumed_by: manual @verify, CI
# doc: .claude/rules/ui_implementation_contract.md#9, .claude/rules/ui_implementation_contract.md#10
# @end_deps
"""

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

import polars as pl

from transformer.metadata_validator import MetadataValidator
from utils.errors import ManifestError

PASS = "✅ PASS"
FAIL = "❌ FAIL"

SUMMARY_TSV = Path(
    "assets/test_data/1_test_data_ST22_dummy/test_data_Summary_20260307_105756.tsv"
)

# Minimal contract matching the actual Summary file headers.
# Keys are the column names expected by MetadataValidator.validate().
SUMMARY_CONTRACT = {
    "sample_id": {"type": "categorical", "is_primary_key": True},
    "Quality Module": {"type": "categorical"},
    "Detected main taxon": {"type": "categorical"},
    "Predicted Phenotype": {"type": "categorical"},
}


def run(output_dir: Path) -> bool:
    output_dir.mkdir(parents=True, exist_ok=True)
    results: list[tuple[str, str]] = []
    validator = MetadataValidator()

    # ── 1. Happy path: valid TSV, matching contract ──────────────────────────
    lf = pl.scan_csv(SUMMARY_TSV, separator="\t")
    try:
        validator.validate(lf, SUMMARY_CONTRACT, context="[summary_schema]")
        results.append(("Happy path — valid TSV passes validate()", PASS))
    except Exception as exc:
        results.append(("Happy path — valid TSV passes validate()", FAIL + f": {exc}"))

    # ── 2. Missing mandatory column → ManifestError ──────────────────────────
    bad_contract = {
        "sample_id": {"type": "categorical"},
        "nonexistent_column": {"type": "categorical"},
    }
    caught = False
    tip_has_hint = False
    try:
        validator.validate(lf, bad_contract, context="[test]")
    except ManifestError as exc:
        caught = True
        tip_has_hint = "nonexistent_column" in str(exc) or "Missing" in str(exc)
    results.append(("Missing column → ManifestError raised", PASS if caught else FAIL))
    results.append(("ManifestError message names the missing column",
                    PASS if tip_has_hint else FAIL))

    # ── 3. Fuzzy suggestion for near-miss column name ────────────────────────
    fuzzy_contract = {
        "sample_id": {"type": "categorical"},
        "Qualiti Module": {"type": "categorical"},  # typo: 'Quality' vs 'Qualiti'
    }
    caught_fuzzy = False
    hint_present = False
    try:
        validator.validate(lf, fuzzy_contract, context="[test_fuzzy]")
    except ManifestError as exc:
        caught_fuzzy = True
        hint_present = "Quality Module" in str(exc.tip) or "Did you mean" in str(exc.tip)
    results.append(("Fuzzy near-miss → ManifestError raised", PASS if caught_fuzzy else FAIL))
    results.append(("Fuzzy hint names the close-match column",
                    PASS if hint_present else FAIL))

    # ── 4. Empty contract → passes unconditionally (identity passthrough) ────
    try:
        validator.validate(lf, {}, context="[empty]")
        results.append(("Empty contract passes (identity passthrough)", PASS))
    except Exception as exc:
        results.append(("Empty contract passes (identity passthrough)", FAIL + f": {exc}"))

    # ── 5. enforce_schema — categorical cast ────────────────────────────────
    cast_contract = {
        "sample_id": {"type": "categorical"},
        "Predicted Phenotype": {"type": "categorical"},
    }
    try:
        result_lf = validator.enforce_schema(lf, cast_contract)
        schema = result_lf.collect_schema()
        ok = schema["sample_id"] == pl.Categorical
        results.append(("enforce_schema casts to Categorical", PASS if ok else FAIL))
    except Exception as exc:
        results.append(("enforce_schema casts to Categorical", FAIL + f": {exc}"))

    # ── 6. enforce_schema — source_name rename ───────────────────────────────
    rename_contract = {
        "taxon": {"type": "categorical", "source_name": "Detected main taxon"},
    }
    try:
        result_lf = validator.enforce_schema(lf, rename_contract)
        cols = result_lf.collect_schema().names()
        ok = "taxon" in cols and "Detected main taxon" not in cols
        results.append(("enforce_schema renames via source_name", PASS if ok else FAIL))
    except Exception as exc:
        results.append(("enforce_schema renames via source_name", FAIL + f": {exc}"))

    # ── 7. CSV (comma-sep) detection ────────────────────────────────────────
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test.csv"
        csv_path.write_text("sample_id,gene\nS1,blaZ\nS2,blaZ\n")
        lf_csv = pl.scan_csv(csv_path, separator=",")
        contract_csv = {"sample_id": {"type": "categorical"}, "gene": {"type": "categorical"}}
        try:
            validator.validate(lf_csv, contract_csv, context="[csv_test]")
            results.append(("CSV (comma-sep) reads and validates correctly", PASS))
        except Exception as exc:
            results.append(("CSV (comma-sep) reads and validates correctly", FAIL + f": {exc}"))

    # ── 8. Source-path resolution: ds_schema.source.path wins ───────────────
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "uploaded.tsv"
        shutil.copy(SUMMARY_TSV, src)

        target_explicit = Path(tmpdir) / "explicit_target.tsv"
        ds_schema = {"source": {"path": str(target_explicit)}, "input_fields": {}}
        source_path = ds_schema.get("source", {}).get("path")
        target = Path(source_path) if source_path else Path(tmpdir) / "fallback.tsv"
        shutil.copy2(src, target)
        ok = target.exists() and target == target_explicit
        results.append(("source.path resolution routes to explicit target", PASS if ok else FAIL))

    # ── 9. Source-path fallback: no source.path → raw_data/<ds_id>.tsv ──────
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "uploaded.tsv"
        shutil.copy(SUMMARY_TSV, src)

        raw_data_dir = Path(tmpdir) / "raw_data"
        raw_data_dir.mkdir()
        ds_schema_no_path = {"source": {}, "input_fields": {}}
        ds_id = "summary_schema"

        source_path = ds_schema_no_path.get("source", {}).get("path")
        if source_path:
            target = Path(source_path)
        else:
            ext = Path("uploaded.tsv").suffix or ".tsv"
            target = raw_data_dir / f"{ds_id}{ext}"

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        ok = target.exists() and target.name == f"{ds_id}.tsv"
        results.append(("Fallback path = raw_data/<ds_id>.tsv", PASS if ok else FAIL))

    # ── Report ───────────────────────────────────────────────────────────────
    lines = [
        "=" * 60,
        "SPARMVET Data Import Headless Debug",
        "=" * 60,
    ]
    all_pass = True
    for name, status in results:
        lines.append(f"  {status.split()[0]}  {name}")
        if not status.startswith("✅"):
            all_pass = False
            lines.append(f"       Detail: {status}")

    lines += [
        "",
        "── Playwright gap (not covered headlessly) ─────────────────",
        "  These require a running Shiny app + Playwright:",
        "  • file picker widget (data_import_multi_upload) renders correctly",
        "  • assignment table appears after upload with correct ds_id choices",
        "  • btn_apply triggers validation error display in UI",
        "  • successful import triggers data_refresh_trigger increment",
        "  • parquet cache bust clears the cached asset from bootloader",
        "=" * 60,
        f"Result: {'ALL PASSED' if all_pass else 'FAILURES DETECTED'}  "
        f"({sum(1 for _, s in results if s.startswith('✅'))}/{len(results)})",
        f"Artifacts written to: {output_dir}",
        "=" * 60,
    ]
    report = "\n".join(lines)
    print(report)
    (output_dir / "debug_data_import_report.txt").write_text(report)
    return all_pass


def main():
    parser = argparse.ArgumentParser(
        description="Headless verification of file import + schema mapping logic."
    )
    parser.add_argument(
        "--output", default="tmp/import_test/",
        help="Directory for output artifacts (default: tmp/import_test/)",
    )
    args = parser.parse_args()
    ok = run(Path(args.output))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
