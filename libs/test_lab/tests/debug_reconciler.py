from test_lab.reconciler import KeyReconciler
import polars as pl
import argparse
from pathlib import Path
import sys
import yaml
import re

# Ensure we can import from src
# STRICT BAN: sys.path.append / sys.path.insert are explicitly forbidden. Rely on pip install -e.


def main():
    parser = argparse.ArgumentParser(
        description="Debug script for Key Reconciler logic verification.")
    parser.add_argument("--ref", required=True, help="Path to reference TSV.")
    parser.add_argument("--target", required=True,
                        help="Path to target TSV (with noisy keys).")
    parser.add_argument("--keys", required=True,
                        help="Comma-separated list of column names to reconcile.")
    parser.add_argument(
        "--mode", choices=["exact", "fuzzy"], default="fuzzy", help="Reconciliation mode.")
    parser.add_argument("--regex", help="Manual regex override.")
    parser.add_argument("--output_dir", default="tmp/reconciler",
                        help="Directory to save reconciliation evidence.")

    args = parser.parse_args()

    ref_df = pl.read_csv(args.ref, separator='\t')
    target_df = pl.read_csv(args.target, separator='\t')
    key_cols = args.keys.split(',')

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    reconciler = KeyReconciler()
    report = reconciler.reconcile(
        ref_df, target_df, key_cols, manual_regex=args.regex)

    print("\n" + "="*60)
    print("      RECONCILIATION SUMMARY TABLE")
    print("="*60)
    print(f"| {'Metric':<25} | {'Count':<10} | {'% of Total':<12} |")
    print(f"| {'-'*25} | {'-'*10} | {'-'*12} |")

    for col, results in report.items():
        metrics = results["metrics"]
        total = metrics["total_ref"]

        print(f"| {col.upper():<25} | {'':<10} | {'':<12} |")
        print(f"| {'  Total Reference Keys':<25} | {total:<10} | {'100%':<12} |")
        print(
            f"| {'  Exact Matches':<25} | {metrics['exact']:<10} | {metrics['exact']/total*100:>10.1f}% |")
        print(
            f"| {'  Fuzzy Matches':<25} | {metrics['fuzzy']:<10} | {metrics['fuzzy']/total*100:>10.1f}% |")
        print(
            f"| {'  Ambiguous Matches':<25} | {metrics['ambiguous']:<10} | {metrics['ambiguous']/total*100:>10.1f}% |")
        print(
            f"| {'  Unmatched (Orphans)':<25} | {metrics['orphans']:<10} | {metrics['orphans']/total*100:>10.1f}% |")
        print(
            f"| {'  Suggested Regex':<25} | {results['suggested_regex']:<10} | {'':<12} |")
        print(f"| {'-'*25} | {'-'*10} | {'-'*12} |")

        # 1. AMBIGUITY WARNING
        if results["ambiguities"]:
            print(f"\n⚠️ HIGH PRIORITY WARNING: Ambiguity detected in {col}!")
            conflict_data = []
            for amb in results["ambiguities"]:
                conflict_data.append({
                    "Reference_Key": amb["ref_key"],
                    "Competitors": ", ".join(amb["targets"])
                })
            conflicts_df = pl.DataFrame(conflict_data)
            conflict_file = out_dir / f"conflicts_{col}.tsv"
            conflicts_df.write_csv(conflict_file, separator='\t')
            print(f"  └── conflicts.tsv: {conflict_file.name}")

        # 2. Materialize: full_audit_map.tsv
        full_map_data = []
        regex = results['suggested_regex']
        for tk, info in results["mapping"].items():
            full_map_data.append({
                "Reference_Key": info["anchor"],
                "Target_Key": tk,
                "Match_Type": info["status"],
                "Generated_Regex": regex
            })
        for otk in results["orphans_target"]:
            full_map_data.append({"Reference_Key": "ORPHAN", "Target_Key": otk,
                                 "Match_Type": "ORPHAN (TARGET)", "Generated_Regex": regex})

        full_audit_df = pl.DataFrame(full_map_data)
        audit_file = out_dir / f"full_audit_map_{col}.tsv"
        full_audit_df.write_csv(audit_file, separator='\t')

        # 3. Materialize: Orphans
        orphans_ref_df = pl.DataFrame({col: results["orphans_reference"]})
        ref_orphan_file = out_dir / f"orphans_reference_{col}.tsv"
        orphans_ref_df.write_csv(ref_orphan_file, separator='\t')

        print(f"\n  Audit Materialization for {col}: {audit_file.name}")

    print("\n" + "="*60)


if __name__ == "__main__":
    main()
