from test_lab.reconciler import KeyReconciler
import polars as pl
import argparse
from pathlib import Path
import sys
import re

# Ensure we can import from src
# STRICT BAN: sys.path.append / sys.path.insert are explicitly forbidden. Rely on pip install -e.


def create_mock_assets(out_dir: Path):
    """Creates test data for x100w2 vs x100w20 verification."""
    ref_file = out_dir / "test_input_ref.tsv"
    target_file = out_dir / "test_input_target.tsv"

    # Reference
    pl.DataFrame({
        "sample_id": ["x100w2", "x100w3", "SAM1", "SAM11"]
    }).write_csv(ref_file, separator='\t')

    # Target (Noisy)
    pl.DataFrame({
        "sample_id": [
            "x100w2_L001.fastq",     # Match x100w2
            # Should NOT match x100w2 (if boundary=True)
            "x100w20_L001.fastq",
            "SAM1_L001.fastq",       # Match SAM1
            "SAM1-re-run.fastq",     # Ambiguous with SAM1
            "SAM11_L001.fastq"       # Match SAM11 (Should NOT match SAM1)
        ]
    }).write_csv(target_file, separator='\t')

    return ref_file, target_file


def main():
    parser = argparse.ArgumentParser(
        description="Debug script for Ambiguity and Boundary logic.")
    parser.add_argument(
        "--ref", help="Path to Reference TSV (optional, will create mock if omitted).")
    parser.add_argument(
        "--target", help="Path to Target TSV (optional, will create mock if omitted).")
    parser.add_argument("--output_dir", default="tmp/reconciler",
                        help="Directory to save audit TSVs.")
    parser.add_argument("--boundary", action="store_true",
                        default=True, help="Enable strict boundary matching.")
    parser.add_argument("--no-boundary", action="store_false",
                        dest="boundary", help="Disable strict boundary matching.")

    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.ref and args.target:
        ref_file = Path(args.ref)
        target_file = Path(args.target)
    else:
        print("[1] SETUP: Creating mock assets for boundary/ambiguity proof...")
        ref_file, target_file = create_mock_assets(out_dir)

    # [2] EXECUTE RECONCILER
    print("\n[2] EXECUTING RECONCILER (Boundary Alignment)...")
    reconciler = KeyReconciler()
    ref_df = pl.read_csv(ref_file, separator='\t')
    target_df = pl.read_csv(target_file, separator='\t')

    report = reconciler.reconcile(
        ref_df, target_df, ["sample_id"], use_boundary=args.boundary)
    res = report["sample_id"]

    print(f"  Boundary Mode: {'ENABLED' if args.boundary else 'DISABLED'}")
    print(f"  Generated Regex: {res['suggested_regex']}")

    # [3] MATERIALIZE AUDIT TSVs
    print("\n[3] MATERIALIZING AUDIT TSVs...")

    # full_audit_map.tsv (renamed to ambiguity_report.tsv as requested)
    report_data = []
    regex = res['suggested_regex']
    for tk, info in res["mapping"].items():
        report_data.append({
            "Reference_Key": info["anchor"],
            "Target_Key": tk,
            "Match_Type": info["status"],
            "Generated_Regex": regex
        })
    for otk in res["orphans_target"]:
        report_data.append({"Reference_Key": "ORPHAN", "Target_Key": otk,
                           "Match_Type": "ORPHAN", "Generated_Regex": regex})

    audit_file = out_dir / "ambiguity_report.tsv"
    pl.DataFrame(report_data).write_csv(audit_file, separator='\t')

    # conflicts.tsv
    conflict_data = []
    for amb in res["ambiguities"]:
        conflict_data.append({
            "Reference_Key": amb["ref_key"],
            "Competitors": ", ".join(amb["targets"])
        })
    conflict_file = out_dir / "conflicts.tsv"
    pl.DataFrame(conflict_data).write_csv(conflict_file, separator='\t')

    # [4] CONSOLE OUTPUT
    print("\n" + "="*55)
    print("      AMBIGUITY & BOUNDARY PROOF")
    print("="*55)
    print(f"Metrics: {res['metrics']}")

    if res["ambiguities"]:
        print("\n⚠️ AMBIGUITIES FOUND (Check conflicts.tsv):")
        for amb in res["ambiguities"]:
            print(
                f"  - '{amb['ref_key']}' matches competitors: {amb['targets']}")

    # Proof: x100w2 vs x100w20
    mapping = {v['anchor']: k for k, v in res['mapping'].items()
               if v['status'] != 'ORPHAN'}
    matched_for_x100w2 = [
        k for k, v in res['mapping'].items() if v['anchor'] == 'x100w2']

    print("\nLOGIC PROOF (x100w2 vs x100w20):")
    print(f"  Reference ID: 'x100w2'")
    print(f"  Targets Found: {matched_for_x100w2}")

    is_safe = "x100w20_L001.fastq" not in matched_for_x100w2
    if is_safe and args.boundary:
        print("  ✅ SUCCESS: 'x100w2' correctly ignored 'x100w20_L001.fastq' (Safe Match).")
    elif not is_safe:
        print(
            "  ❌ WARNING: 'x100w2' incorrectly matched 'x100w20_L001.fastq' (Over-match).")

    print("\nMATERIALIZED FILES:")
    print(f"  └── {audit_file.resolve()}")
    print(f"  └── {conflict_file.resolve()}")
    print("="*55)


if __name__ == "__main__":
    main()
