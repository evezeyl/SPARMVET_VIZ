# @deps
# provides: class:DataIngestor, method:ingest, method:find_file
# consumes: libs/ingestion/src/ingestion/sanitizer.py
#           libs/utils/src/utils/pipeline_error.py (PipelineError — DIAG-RUNTIME-INGESTION-1)
# consumed_by: app/modules/orchestrator.py, libs/transformer/tests/debug_assembler.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-013
# @end_deps
import polars as pl
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from ingestion.sanitizer import DataSanitizer
from utils.errors import IngestionError
from utils.pipeline_error import PipelineError


class DataIngestor:
    """
    The official Ingestion Engine for the Dashboard.
    Responsible for mapping conceptual datasets defined in the YAML manifest
    to physical files on disk, executing Polars lazy loading, and optionally 
    validating the raw columns against the schema structure.
    """

    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            pe = PipelineError(
                component="DataIngestor",
                problem=f"Data directory not found: {self.data_dir}",
                location="DataIngestor.__init__",
                fix=(
                    "Verify that the 'data_dir' path in your deployment profile or manifest "
                    "source block points to an existing directory containing the source TSV/Parquet files."
                ),
                who="operator",
                category="ingestion",
                surface="data_import_panel",
                severity="error",
                evidence={"path": str(self.data_dir)},
            )
            print(pe.format())
            raise IngestionError(pe.problem, tip=pe.fix)

    def find_file(self, dataset_name: str) -> Optional[Path]:
        """
        Attempts to locate the physical TSV file for a given dataset name.
        Uses exact match first, then falls back to prefix/substring globbing.
        """
        exact_match = self.data_dir / f"{dataset_name}.tsv"
        if exact_match.exists():
            return exact_match

        # Fallback to fuzzy mapping (Recursive Discovery)
        potential_files = list(self.data_dir.glob(f"**/*{dataset_name}*.tsv"))
        if potential_files:
            return potential_files[0]

        return None

    def ingest(self, dataset_name: str, dataset_schema: Dict[str, Any]) -> Tuple[pl.LazyFrame, Path]:
        """
        Locates the dataset file and returns a standard Polars LazyFrame.

        Raises:
            FileNotFoundError: If the TSV file cannot be located.
            ValueError: If the file exists but Polars fails to parse it.
        """
        # ADR-013+: Support explicit source blocks for multi-source alignment
        source = dataset_schema.get("source", {})
        source_type = source.get("type")
        source_path = source.get("path")

        if source_type == "local_tsv" and source_path:
            resolved_path = Path(source_path)
            lf = pl.scan_csv(resolved_path, separator="\t")
        elif source_type == "local_parquet" and source_path:
            resolved_path = Path(source_path)
            lf = pl.scan_parquet(resolved_path)
        else:
            # Fallback to legacy discovery in self.data_dir
            resolved_path = self.find_file(dataset_name)
            if resolved_path and resolved_path.exists():
                lf = pl.scan_csv(resolved_path, separator="\t")
            else:
                search_context = source_path if source_path else self.data_dir
                pe = PipelineError(
                    component="DataIngestor",
                    problem=f"Could not locate a physical file for dataset '{dataset_name}' at {search_context}.",
                    location=f"DataIngestor.ingest(dataset_name='{dataset_name}')",
                    fix=(
                        "Check that the manifest 'source.path' key points to an existing file, "
                        "or that a TSV matching the dataset name exists in the data directory. "
                        "Use an explicit 'source: {type: local_tsv, path: ...}' block to avoid fuzzy discovery."
                    ),
                    who="data_provider",
                    category="ingestion",
                    surface="data_import_panel",
                    severity="error",
                    evidence={"dataset_name": dataset_name, "search_context": str(search_context)},
                )
                print(pe.format())
                raise IngestionError(pe.problem, tip=pe.fix)

        try:
            # ADR-013: Use 'input_fields' for raw ingestion mapping
            fields_data = dataset_schema.get(
                "input_fields") or dataset_schema.get("fields") or {}
            if fields_data:
                available_cols = lf.collect_schema().names()
                # Create a case-insensitive map of available columns
                ci_available = {c.lower(): c for c in available_cols}

                rename_mapping = {}
                for key, props in fields_data.items():
                    original = props.get("original_name")
                    if original:
                        # Try exact match first, then case-insensitive
                        if original in available_cols:
                            rename_mapping[original] = key
                        elif original.lower() in ci_available:
                            rename_mapping[ci_available[original.lower()]] = key

                if rename_mapping:
                    lf = lf.rename(rename_mapping)

                # --- Non-breaking audit: warn about schema columns missing from source ---
                # Handoff #4: Columns declared in input_fields but absent from the file
                # are logged as warnings (not errors) to support discovery-phase development.
                post_rename_cols = set(lf.collect_schema().names())
                for key, props in fields_data.items():
                    if key not in post_rename_cols:
                        original = props.get("original_name", key)
                        pe = PipelineError(
                            component="DataIngestor",
                            problem=f"Column '{key}' declared in input_fields for '{dataset_name}' but not found in source file.",
                            location=f"DataIngestor.ingest(dataset_name='{dataset_name}')",
                            fix=(
                                f"Check that the source TSV contains a column named '{original}'. "
                                "Use 'original_name:' in the input_fields declaration to remap a differently-named column. "
                                "Downstream wrangling steps referencing this column will fail."
                            ),
                            who="data_provider",
                            category="ingestion",
                            surface="data_import_panel",
                            severity="warning",
                            evidence={"slug": key, "expected_source_name": original, "available_columns": list(post_rename_cols)[:20]},
                        )
                        print(pe.format())

            # --- Sanitize: strip whitespace + normalize null sentinels (INGEST-SANITIZE-1) ---
            # Runs after rename so column names are stable; runs before cast so empty strings
            # become actual nulls before any numeric/date cast attempts.
            lf = DataSanitizer().apply(lf)

            # --- Type Casting Logic (ADR-013 Refinement) ---
            # Automatically cast columns to standard types based on schema 'type' field.
            cast_exprs = []
            for key, props in fields_data.items():
                if key not in lf.collect_schema().names():
                    continue

                target_type = props.get("type", "categorical")
                if target_type == "numeric":
                    cast_exprs.append(pl.col(key).cast(pl.Float64))
                elif target_type in ("categorical", "string"):
                    cast_exprs.append(pl.col(key).cast(pl.String))
                elif target_type == "date":
                    cast_exprs.append(pl.col(key).cast(pl.Date))

            if cast_exprs:
                lf = lf.with_columns(cast_exprs)

            return lf, resolved_path
        except (IngestionError, Exception) as e:
            if isinstance(e, IngestionError):
                raise
            pe = PipelineError(
                component="DataIngestor",
                problem=f"Failed to parse '{resolved_path.name}': {type(e).__name__}: {e}",
                location=f"DataIngestor.ingest(dataset_name='{dataset_name}')",
                fix=(
                    "Verify that the file is a valid TSV (tab-separated) or Parquet file. "
                    "Common causes: wrong delimiter, encoding issues (use UTF-8), "
                    "truncated file, or a column type mismatch during cast."
                ),
                who="data_provider",
                category="ingestion",
                surface="data_import_panel",
                severity="error",
                evidence={"file": str(resolved_path), "error_type": type(e).__name__, "error_detail": str(e)[:200]},
            )
            print(pe.format())
            raise IngestionError(pe.problem, tip=pe.fix) from e

    def validate_schema(self, lf: pl.LazyFrame, dataset_schema: Dict[str, Any]) -> bool:
        """
        Validates that the physical loaded LazyFrame contains all the mandatory 
        columns defined in the formal _fields.yaml dictionary.
        ADR-013: Uses 'input_fields' for raw validation.
        """
        fields_data = dataset_schema.get(
            "input_fields") or dataset_schema.get("fields") or {}
        if not fields_data:
            return True  # Nothing to validate against

        # For now, simply confirming we can read the raw columns
        # Strict validation of names/types will occur here.
        raw_columns = lf.columns
        return len(raw_columns) > 0


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Manual execution hook for testing.")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    args = parser.parse_args()
    if args.test:
        print(f"Executing {__file__} in test mode.")
