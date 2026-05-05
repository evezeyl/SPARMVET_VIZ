#!/usr/bin/env python3
# @deps
# provides: script:debug_decorator_suite
# consumes: libs/transformer/src/transformer/actions/, libs/transformer/tests/data/
# consumed_by: manual action-decorator testing
# doc: .claude/rules/rules_data_engine.md#3
# @end_deps
import os
import sys
import subprocess
import polars as pl
from pathlib import Path
from typing import List, Dict

# ADR-016: Use Package-First Authority
project_root = Path(__file__).resolve().parent.parent.parent.parent
wrangler_runner = project_root / "libs/transformer/tests/debug_wrangler.py"
test_data_dir = project_root / "libs/transformer/tests/data"
output_dir = project_root / "tmp/wrapper"

# Add transformer src to path for registry access
# STRICT BAN: sys.path.append / sys.path.insert are explicitly forbidden. Rely on pip install -e.

try:
    from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS
    # Import subpackages to trigger registration
    import transformer.actions.reshaping
    import transformer.actions.cleaning
    import transformer.actions.relational
    import transformer.actions.performance
    import transformer.actions.persistence
except ImportError as e:
    print(f"❌  ERROR: Could not load action registry. {e}")
    sys.exit(1)


def run_suite():
    """
    Automated Decorator Test Suite (Consolidated).
    Iterates through all actions in the registry and enforces the 1:1:1 naming law.
    Generates evidence in tmp/wrapper/ for manual @verify.
    """
    print(f"\n[{'='*60}]")
    print(f" 🧪 DECORATOR SUITE EXECUTION")
    print(f"[{'='*60}]\n")

    os.makedirs(output_dir, exist_ok=True)

    # Discovery from Registry
    registered_actions = sorted(list(AVAILABLE_WRANGLING_ACTIONS.keys()))
    # Skip relational actions (Layer 2)
    actions_to_test = [
        a for a in registered_actions if a not in ["join", "join_filter"]]

    results = []

    for action_id in actions_to_test:
        print(f"\n▶️  ACTION: {action_id}")

        manifest_path = test_data_dir / f"{action_id}_manifest.yaml"
        data_path = test_data_dir / f"{action_id}_test.tsv"
        output_file = output_dir / f"{action_id}_debug_view.tsv"

        # 1:1:1 Validation
        if not manifest_path.exists() or not data_path.exists():
            status = "NON-COMPLIANT"
            msg = "Missing manifest/data pair"
            results.append({"id": action_id, "status": status, "msg": msg})
            print(f"   └── ❌ {status}: {msg}")
            continue

        # Execution
        cmd = [
            sys.executable, str(wrangler_runner),
            "--manifest", str(manifest_path),
            "--output", str(output_file)
        ]

        try:
            # We run and let it print its own header/glimpse to our stdout
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"   └── ✅ PASS: Materialized to {output_file.name}")
                # Extract and print just the glimpse part from the child output
                output_lines = result.stdout.split('\n')
                glimpse_start = -1
                for i, line in enumerate(output_lines):
                    if "[TRANSFORMED DATA GLIMPSE" in line:
                        glimpse_start = i
                        break

                if glimpse_start != -1:
                    print(
                        '\n'.join(output_lines[glimpse_start:glimpse_start+15]))

                results.append(
                    {"id": action_id, "status": "PASS", "msg": "Success"})
            else:
                print(f"   └── ❌ FAIL")
                print(f"       {result.stderr.strip().split('\\n')[-1]}")
                results.append(
                    {"id": action_id, "status": "FAIL", "msg": "Exec error"})

        except Exception as e:
            print(f"   └── 🛑 ERROR: {e}")
            results.append({"id": action_id, "status": "ERROR", "msg": str(e)})

    # Final Summary Table
    print(f"\n\n[{'='*60}]")
    print(f" 📊 FINAL EXECUTION SUMMARY")
    print(f"[{'='*60}]")
    print(f"{'Action Name':<30} | {'Status':<10} | {'Output'}")
    print(f"{'-'*30}-|-{'-'*10}-|-{'-'*20}")

    pass_count = 0
    for r in results:
        icon = "🟢" if r['status'] == "PASS" else "🔴"
        print(f"{r['id']:<30} | {icon} {r['status']:<7} | {r['id']}_debug_view.tsv")
        if r['status'] == "PASS":
            pass_count += 1

    print(
        f"\nTotal Actions: {len(results)} | Passed: {pass_count} | Failed: {len(results)-pass_count}")
    print(f"[{'='*60}]\n")
    print("Data is ready in tmp/wrapper/. Please verify the integrity of the 1:1:1 mapping and the Polars output contract. Waiting for @verify.\n")


if __name__ == "__main__":
    run_suite()
