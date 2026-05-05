# @deps
# provides: XlsxExtractor class (extract) — reads multi-sheet XLSX and writes normalized TSVs
# consumes: polars, pathlib, typing, yaml (stdlib/third-party)
# consumed_by: libs/test_lab/tests/debug_sdk.py
# @end_deps
import polars as pl
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml


class XlsxExtractor:
    """
    Logic for extracting multiple sheets from an XLSX file and normalizing them into TSVs.
    Supports a 'Project Basename' approach for organized output.
    """

    def __init__(self, project_basename: Optional[str] = None):
        self.project_basename = project_basename

    def extract(self, excel_path: str, config_path: str, out_dir: str, standardized_id: str = "id") -> Dict[str, Path]:
        """
        Extracts sheets defined in config_path from excel_path into out_dir.
        If project_basename is set, creates a subfolder within out_dir.
        """
        excel_p = Path(excel_path)
        config_p = Path(config_path)

        # Determine effective output directory
        base_name = self.project_basename or excel_p.stem
        effective_out_dir = Path(out_dir) / base_name
        effective_out_dir.mkdir(parents=True, exist_ok=True)

        # Load config
        with open(config_p, 'r') as f:
            config = yaml.safe_load(f)

        sheets_to_extract = config.get("extract_sheets", {})
        if not sheets_to_extract:
            raise ValueError(
                "No 'extract_sheets' defined in the configuration YAML.")

        # Read Excel
        all_sheets_dict = pl.read_excel(excel_p, sheet_id=0)

        extracted_files = {}
        for original_name, rules in sheets_to_extract.items():
            if original_name not in all_sheets_dict:
                print(f"Warning: Sheet '{original_name}' not found. Skipping.")
                continue

            df = all_sheets_dict[original_name]
            target_name = rules.get(
                "target_name", original_name.lower().replace(" ", "_"))
            original_pkey = rules.get("primary_key")

            if not original_pkey:
                print(
                    f"Warning: No 'primary_key' for '{original_name}'. Skipping.")
                continue

            if original_pkey not in df.columns:
                print(
                    f"Warning: PK '{original_pkey}' not found in '{original_name}'. Skipping.")
                continue

            # Rename and Save
            df = df.rename({original_pkey: standardized_id})
            out_file = effective_out_dir / f"{target_name}.tsv"
            df.write_csv(out_file, separator='\t')
            extracted_files[target_name] = out_file

        return extracted_files
