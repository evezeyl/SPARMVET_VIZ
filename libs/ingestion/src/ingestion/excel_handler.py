#!/usr/bin/env python3
# engine: python-polars (reads Excel sheets into Polars tables)
# libs/ingestion/src/ingestion/excel_handler.py
import argparse
import polars as pl
import yaml
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Extract and standardize multiple sheets from a pipeline Excel report into individual TSVs."
    )
    parser.add_argument("--excel_file", required=True,
                        help="Path to the multi-sheet Excel report.")
    parser.add_argument("--config", required=True,
                        help="Path to the YAML configuration file mapping sheets to primary keys.")
    parser.add_argument("--out_dir", required=False, default="assets/test_data/extracted_sheets",
                        help="Output directory for the extracted TSV files.")
    parser.add_argument("--standardized_pkey", required=False, default="id",
                        help="The standard column name the primary key will be renamed to in the TSV outputs.")
    args = parser.parse_args()

    # 1. Load Configurations
    excel_path = Path(args.excel_file)
    if not excel_path.exists():
        print(f"Error: Excel file '{excel_path}' not found.")
        return

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Config file '{config_path}' not found.")
        return

    with open(config_path, 'r') as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            print(f"Error parsing YAML config: {exc}")
            return

    sheets_to_extract = config.get("extract_sheets", {})
    if not sheets_to_extract:
        print("No 'extract_sheets' defined in the configuration YAML.")
        return

    # 2. Setup Output Directory
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Extracting sheets to: {out_dir}")

    # 3. Read and Process Sheets
    try:
        # We read all sheets using polars.
        all_sheets_dict = pl.read_excel(excel_path, sheet_id=0)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    extracted_count = 0
    missing_sheets = []
    missing_pkeys = []

    for original_sheet_name, rules in sheets_to_extract.items():
        if original_sheet_name not in all_sheets_dict:
            print(
                f"Warning: Sheet '{original_sheet_name}' not found in Excel file. Skipping.")
            missing_sheets.append(original_sheet_name)
            continue

        df = all_sheets_dict[original_sheet_name]

        target_name = rules.get(
            "target_name", original_sheet_name.lower().replace(" ", "_"))
        original_pkey = rules.get("primary_key")

        if not original_pkey:
            print(
                f"Warning: No 'primary_key' defined for sheet '{original_sheet_name}'. Skipping.")
            continue

        if original_pkey not in df.columns:
            print(
                f"Warning: Primary key column '{original_pkey}' not found in sheet '{original_sheet_name}'. Skipping.")
            missing_pkeys.append((original_sheet_name, original_pkey))
            continue

        # Rename the primary key to the standardized key
        df = df.rename({original_pkey: args.standardized_pkey})

        # Write to TSV
        out_file = out_dir / f"{target_name}.tsv"
        df.write_csv(out_file, separator='\t')
        print(
            f"Successfully extracted: '{original_sheet_name}' -> {out_file} ({df.height} rows)")
        extracted_count += 1

    print(f"\nFinished. Extracted {extracted_count} sheets.")


if __name__ == "__main__":
    main()
