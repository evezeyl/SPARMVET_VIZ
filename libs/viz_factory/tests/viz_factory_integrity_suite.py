#!/usr/bin/env python3
# @deps
# provides: script:viz_factory_integrity_suite
# consumes: libs/viz_factory/tests/debug_runner.py, libs/viz_factory/tests/test_data/, libs/viz_factory/src/viz_factory/
# consumed_by: CI / manual audit
# doc: .claude/rules/rules_data_engine.md
# @end_deps
import os
import sys
import subprocess
import datetime
import yaml
import argparse
from pathlib import Path
from typing import List, Dict

# Ensure project root is in sys.path for fallback
project_root = Path(__file__).resolve().parent.parent.parent.parent
# Add libs/viz_factory to sys.path to enable 'from viz_factory...'
# STRICT BAN: sys.path.append / sys.path.insert are explicitly forbidden. Rely on pip install -e.

try:
    # Now that 'viz_factory' symlink exists pointing to 'src', this works
    from viz_factory.registry import PLOT_COMPONENTS
    # Trigger registration via sub-packages
    import viz_factory.geoms
    import viz_factory.scales
    import viz_factory.themes
    import viz_factory.coords
    import viz_factory.facets
    import viz_factory.positions
    import viz_factory.guides
except ImportError as e:
    print(f"❌ ERROR: [Integrity Suite] Failed to load registry. {e}")
    sys.exit(1)

# Paths
test_runner = project_root / "libs/viz_factory/tests/debug_runner.py"
test_data_dir = project_root / "libs/viz_factory/tests/test_data"


def run_suite(output_dir: Path = None):
    report_lines = []
    out_root = output_dir or (project_root / "tmp" / "viz_factory")
    output_report = out_root / "viz_factory_integrity_report.txt"
    report_lines = []

    def log(msg: str):
        print(msg)
        report_lines.append(msg)

    log(f"[{'='*60}]")
    log(f" 🛡️  VIZ FACTORY MASTER INTEGRITY SUITE (Artist Pillar)")
    log(f" Date: {datetime.datetime.now().isoformat()}")
    log(f"[{'='*60}]\n")

    # 1. CATEGORIZED INVENTORY
    log("📋 COMPONENT INVENTORY (Artist Registry)")
    log(f"{'Category':<15} | {'Component Name':<35}")
    log("-" * 55)

    registered = PLOT_COMPONENTS.keys()
    categorized = {}

    for comp in registered:
        # Infer category from prefix (geom_, scale_, theme_, etc.)
        cat = comp.split('_')[0] if '_' in comp else "other"
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append(comp)

    for cat in sorted(categorized.keys()):
        for comp in sorted(categorized[cat]):
            log(f"{cat:<15} | {comp:<35}")
    log("\n")

    # 2. VALIDATION LOOP
    log("🧪 COMPONENT VALIDATION (1:1:1 Evidence Loop)")
    log(f"{'Component Name':<35} | {'Status':<10} | {'Details'}")
    log("-" * 75)

    results = []
    for comp in sorted(registered):
        manifest_path = test_data_dir / f"{comp}_test.yaml"
        # The triplet expects {comp}_test.tsv as well, but test_runner handles that.

        if not manifest_path.exists():
            status = "NO TEST"
            log(f"{comp:<35} | 🟡 {status:<8} | Missing manifest in test_data/")
            results.append((comp, status, "No manifest"))
            continue

        cmd = [sys.executable, str(test_runner), str(manifest_path),
               "--output_dir", str(out_root)]
        try:
            res = subprocess.run(cmd, capture_output=True,
                                 text=True, timeout=20)
            if res.returncode == 0:
                status = "PASSED"
                log(f"{comp:<35} | 🟢 {status:<8} | Logic Verified")
                results.append((comp, status, "Success"))
            else:
                status = "FAILED"
                err_msg = res.stderr.strip().split(
                    '\n')[-1] if res.stderr else "Unknown failure"
                log(f"{comp:<35} | 🔴 {status:<8} | {err_msg}")
                results.append((comp, status, err_msg))
        except Exception as e:
            status = "ERROR"
            log(f"{comp:<35} | 🛑 {status:<8} | {str(e)}")
            results.append((comp, status, str(e)))

    # 3. FINAL SUMMARY
    passed = len([r for r in results if r[1] == "PASSED"])
    failed = len([r for r in results if r[1] in ["FAILED", "ERROR"]])
    no_test = len([r for r in results if r[1] == "NO TEST"])

    log(f"\n[{'='*60}]")
    log(" 📊 FINAL INTEGRITY SUMMARY")
    log(f" Total Registered Components: {len(registered)}")
    log(f" Passed:                      {passed}")
    log(f" Failed:                      {failed}")
    log(f" No Test Data:                {no_test}")
    log(f"[{'='*60}]\n")

    # Save the report
    os.makedirs(os.path.dirname(output_report), exist_ok=True)
    with open(output_report, "w") as f:
        f.write('\n'.join(report_lines))
    print(f"✅ Integrity Report Saved: {output_report}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Viz Factory Master Integrity Suite (Artist Pillar)")
    parser.add_argument("--output_dir", type=str, default=None,
                        help="Root directory to materialize PNG plots and report.")
    args = parser.parse_args()

    run_suite(Path(args.output_dir) if args.output_dir else None)
