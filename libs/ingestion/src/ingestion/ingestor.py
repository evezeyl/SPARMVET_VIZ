# @deps
# provides: class:DataIngestor, method:ingest, method:find_file
# consumes: libs/ingestion/src/ingestion/sanitizer.py
#           libs/utils/src/utils/pipeline_error.py (PipelineError — DIAG-RUNTIME-INGESTION-1)
# consumed_by: app/modules/orchestrator.py, libs/transformer/tests/debug_assembler.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-013, .claude/knowledge/architecture_decisions.md#ADR-094
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
    Responsible for mapping conceptual datasets defined in the YAML data analysis recipe
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
                    "Verify that the 'data_dir' path in your deployment or data analysis recipe "
                    "source block points to an existing directory containing the source TSV/Parquet files."
                ),
                who="operator",
                category="ingestion",
                surface="data_import_panel",
                severity="error",
                evidence={"path": str(self.data_dir)},
            )
            print(pe.format())
            raise IngestionError(pe.problem, tip=pe.fix, pipeline_error=pe)

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
                        "Check that the data analysis recipe 'source.path' key points to an existing file, "
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
                raise IngestionError(pe.problem, tip=pe.fix, pipeline_error=pe)

        try:
            # ADR-013: Use 'input_fields' for raw ingestion mapping
            fields_data = dataset_schema.get(
                "input_fields") or dataset_schema.get("fields") or {}
            if fields_data:
                # Strict import (Eve 2026-11-13, spec O22): only the declared fields enter. A declared field is
                # found by its exact `original_name` (the slug when none is given); one the file lacks fails.
                available_cols = lf.collect_schema().names()
                wanted = {}   # slug -> header expected in the file
                for key, props in fields_data.items():
                    wanted[key] = (props or {}).get("original_name") or key
                absent = {slug: header for slug, header in wanted.items() if header not in available_cols}
                if absent:
                    pe = PipelineError(
                        component="DataIngestor",
                        problem=(f"Column(s) {sorted(absent)} declared in input_fields for '{dataset_name}' not found in the "
                                 f"source file (expected file headers: {sorted(absent.values())})."),
                        location=f"DataIngestor.ingest(dataset_name='{dataset_name}')",
                        fix=(
                            "The file header must match original_name exactly (spelling and case); the slug is used "
                            "when no original_name is given. Correct original_name, or remove the declaration."
                        ),
                        who="data_provider",
                        category="ingestion",
                        surface="data_import_panel",
                        severity="error",
                        evidence={"missing": {s: h for s, h in absent.items()}, "available_columns": available_cols[:30]},
                    )
                    print(pe.format())
                    raise IngestionError(pe.problem, tip=pe.fix, pipeline_error=pe)

                headers = set(wanted.values())
                left_out = [c for c in available_cols if c not in headers]
                # select first, then rename: an undeclared file column that already carries a slug cannot collide
                lf = lf.select([c for c in available_cols if c in headers])
                rename_mapping = {header: slug for slug, header in wanted.items() if header != slug}
                if rename_mapping:
                    lf = lf.rename(rename_mapping)
                if left_out:
                    pe = PipelineError(
                        component="DataIngestor",
                        problem=(f"{len(left_out)} file columns of '{dataset_name}' are not declared in input_fields "
                                 f"and were not imported: {left_out}."),
                        location=f"DataIngestor.ingest(dataset_name='{dataset_name}')",
                        fix="Declare a column in input_fields to import it; nothing else is needed if it is not used.",
                        who="data_analysis_recipe_author",
                        category="ingestion",
                        surface="data_import_panel",
                        severity="warning",
                        evidence={"not_imported": left_out},
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
            raise IngestionError(pe.problem, tip=pe.fix, pipeline_error=pe) from e


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Manual execution hook for testing.")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    args = parser.parse_args()
    if args.test:
        print(f"Executing {__file__} in test mode.")
