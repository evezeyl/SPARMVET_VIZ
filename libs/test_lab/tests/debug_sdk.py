from test_lab.aqua_synthesizer import AquaSynthesizer
from test_lab.bootstrapper import ManifestBootstrapper
from test_lab.extractor import XlsxExtractor
import polars as pl
from pathlib import Path
import os
import sys
import yaml

# Ensure we can import from src
# STRICT BAN: sys.path.append / sys.path.insert are explicitly forbidden. Rely on pip install -e.


def create_mock_excel(path: Path):
    """Creates a multi-sheet mock Excel for Stage A testing."""
    import openpyxl
    wb = openpyxl.Workbook()

    # Sheet 1: Metadata
    ws1 = wb.active
    ws1.title = "Metadata"
    ws1.append(["Sample_ID", "Species", "Country"])
    ws1.append(["SAM001", "E. coli", "Norway"])
    ws1.append(["SAM002", "S. enterica", "Denmark"])
    ws1.append(["SAM003", "L. monocytogenes", "Sweden"])

    # Sheet 2: ResFinder
    ws2 = wb.create_sheet("ResFinder Hits")
    ws2.append(["ID", "Gene", "Identity"])
    ws2.append(["SAM001", "tet(A)", 99.5])
    ws2.append(["SAM002", "sul1", 98.2])
    ws2.append(["SAM001", "dfrA1", 100.0])

    wb.save(path)


def create_mock_config(path: Path):
    """Creates extraction config for Stage A."""
    config = {
        "extract_sheets": {
            "Metadata": {
                "target_name": "test_metadata",
                "primary_key": "Sample_ID"
            },
            "ResFinder Hits": {
                "target_name": "test_data_resfinder",
                "primary_key": "ID"
            }
        }
    }
    with open(path, 'w') as f:
        yaml.dump(config, f)


def main():
    print("[1] SETUP: Creating mock assets...")
    tmp_path = Path("tmp/sdk_test")
    tmp_path.mkdir(parents=True, exist_ok=True)

    excel_file = tmp_path / "raw_pipeline.xlsx"
    config_file = tmp_path / "extract_config.yaml"
    extract_dir = tmp_path / "extracted"
    bootstrap_dir = tmp_path / "bootstrapped"
    aqua_dir = tmp_path / "aqua_synthetic"

    create_mock_excel(excel_file)
    create_mock_config(config_file)

    # --- STAGE A: EXTRACTION ---
    print("\n[2] STAGE A: Extraction (XLSX -> TSV)...")
    extractor = XlsxExtractor(project_basename="Project_SDK_Demo")
    extracted_files = extractor.extract(
        excel_path=str(excel_file),
        config_path=str(config_file),
        out_dir=str(extract_dir),
        standardized_id="sample_id"
    )
    for name, path in extracted_files.items():
        print(f"  └── Saved: {name} -> {path}")

    # --- STAGE B: BOOTSTRAPPING ---
    print("\n[3] STAGE B: Bootstrapping (YAML Inference)...")
    bootstrapper = ManifestBootstrapper()
    master_manifest = bootstrapper.bootstrap(
        tsv_paths=list(extracted_files.values()),
        project_id="Project_SDK_Demo",
        out_dir=bootstrap_dir
    )
    print(f"  └── Master Manifest: {master_manifest}")

    # --- STAGE C: AQUA SYNTHESIS ---
    print("\n[4] STAGE C: Aqua Synthesis (Relational Anchoring)...")
    n_samples = 10
    synthesizer = AquaSynthesizer(
        anchor_key_name="sample_id", n_samples=n_samples)
    synthetic_files = synthesizer.synthesize(
        tsv_paths=list(extracted_files.values()),
        out_dir=aqua_dir
    )
    for f in synthetic_files:
        print(f"  └── Created Synthetic: {f}")

    # --- VERIFICATION: RELATIONAL JOIN ---
    print("\n[5] VERIFICATION: Proving Join Integrity...")
    meta_p = next(f for f in synthetic_files if 'metadata' in f.name.lower())
    res_p = next(f for f in synthetic_files if 'resfinder' in f.name.lower())

    df_meta = pl.read_csv(meta_p, separator='\t')
    df_res = pl.read_csv(res_p, separator='\t')

    joined = df_meta.join(df_res, on="sample_id", how="inner")

    print("\nJOIN RESULT GLIMPSE (Metadata <-> ResFinder):")
    print(joined.glimpse())

    print(f"\nJoin success: Found {joined.height} matching relational hits.")
    if joined.height > 0:
        print("✅ RELATIONAL ANCHORING SUCCESSFUL.")
    else:
        print("❌ RELATIONAL ANCHORING FAILED.")


if __name__ == "__main__":
    main()
