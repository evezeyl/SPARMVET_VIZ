# @deps
# provides: class:DataIngestor, method:ingest, method:find_file
# consumes: libs/ingestion/src/ingestion/declared.py
#           libs/utils/src/utils/pipeline_error.py (PipelineError — DIAG-RUNTIME-INGESTION-1)
# consumed_by: app/modules/orchestrator.py, libs/transformer/tests/debug_assembler.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-013, .claude/knowledge/architecture_decisions.md#ADR-094
# @end_deps
import polars as pl
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
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
        The file of a dataset in the data folder: `<dataset id>.tsv`, the exact name (no fuzzy search; spec 7.3).
        """
        exact_match = self.data_dir / f"{dataset_name}.tsv"
        return exact_match if exact_match.exists() else None

    def _open(self, dataset_name: str, dataset_schema: Dict[str, Any], as_text: bool = False) -> Tuple[pl.LazyFrame, Path]:
        """Locate the file of a dataset and open it lazily; with `as_text` every column is a String (no inference)."""
        # ADR-013+: Support explicit source blocks for multi-source alignment
        source = dataset_schema.get("source", {})
        source_type = source.get("type")
        source_path = source.get("path")

        if source_type == "local_tsv" and source_path:
            resolved_path = Path(source_path)
            lf = pl.scan_csv(resolved_path, separator="\t", infer_schema=not as_text)
        elif source_type == "local_parquet" and source_path:
            resolved_path = Path(source_path)
            lf = pl.scan_parquet(resolved_path)
        else:
            # Fallback to legacy discovery in self.data_dir
            resolved_path = self.find_file(dataset_name)
            if resolved_path and resolved_path.exists():
                lf = pl.scan_csv(resolved_path, separator="\t", infer_schema=not as_text)
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

        return lf, resolved_path

    def _import_declared_columns(self, lf: pl.LazyFrame, dataset_name: str, fields_data: Dict[str, Any]) -> pl.LazyFrame:
        """Strict import: only the declared fields enter, found by their exact `original_name`, renamed to the slug."""
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

        return lf

    def ingest(self, dataset_name: str, dataset_schema: Dict[str, Any]) -> Tuple[pl.LazyFrame, Path]:
        """Read the file as text, import only the declared fields, then apply `strip`, `null_values` and the declared
        Polars types (`ingestion.declared`); a value that does not fit fails and names the column and the values
        (spec 7.3, 7.4)."""
        from ingestion.declared import apply_declared
        lf, resolved_path = self._open(dataset_name, dataset_schema, as_text=True)
        fields = dataset_schema.get("input_fields") or {}
        try:
            if fields:
                lf = self._import_declared_columns(lf, dataset_name, fields)
            return apply_declared(lf, dataset_name, dataset_schema, fields), resolved_path
        except IngestionError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise IngestionError(f"Failed to read '{resolved_path.name}': {type(exc).__name__}: {str(exc)[:200]}",
                                 tip="Check that the file is a valid tab-separated file and that the declared fields match it") from exc


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Manual execution hook for testing.")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    args = parser.parse_args()
    if args.test:
        print(f"Executing {__file__} in test mode.")
