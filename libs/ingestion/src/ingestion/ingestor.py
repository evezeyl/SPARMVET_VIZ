# @deps
# provides: class:DataIngestor, method:ingest, method:find_file, function:find_dataset_file, function:read_as_declared, function:ingest_file, function:file_kind
# consumes: libs/ingestion/src/ingestion/declared.py
#           libs/utils/src/utils/pipeline_error.py (PipelineError — DIAG-RUNTIME-INGESTION-1)
# consumed_by: app/modules/orchestrator.py (find_dataset_file), app/modules/data_import_check.py (ingest_file, file_kind: the Data Import check is this read), libs/transformer/tests/debug_assembler.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-013, .claude/knowledge/architecture_decisions.md#ADR-094
# @end_deps
import polars as pl
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from utils.errors import IngestionError
from utils.pipeline_error import PipelineError


DATASET_FILE_SUFFIXES = (".tsv", ".parquet")


def find_dataset_file(data_dir: Path, dataset_name: str) -> Optional[Path]:
    """The file of a dataset in a data folder: `<dataset id>.tsv` or `<dataset id>.parquet`, the exact name.

    The one rule by which a dataset is found by its id (production lookup and the folder of an imported bundle).
    No fuzzy search (spec 7.3). WHY an error when both exist: reading one of them silently would let the
    other one be the file the user thinks was read.
    """
    found = [Path(data_dir) / f"{dataset_name}{suffix}" for suffix in DATASET_FILE_SUFFIXES]
    found = [path for path in found if path.is_file()]
    if len(found) > 1:
        raise IngestionError(
            f"Dataset '{dataset_name}' has more than one file in {data_dir}: {', '.join(p.name for p in found)}.",
            tip="Keep one file per dataset id: remove or rename the one that is not the data to read.")
    return found[0] if found else None


def import_declared_columns(lf: pl.LazyFrame, dataset_name: str, fields_data: Dict[str, Any]) -> pl.LazyFrame:
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


def read_as_declared(lf: pl.LazyFrame, dataset_name: str, dataset_schema: Dict[str, Any], file_name: str) -> pl.LazyFrame:
    """What the ingestion does once the file is open as text: import only the declared fields (found by their exact
    `original_name`), then apply `strip`, `null_values` and the declared Polars types. The ONE definition of "this file
    can be read for this dataset": `DataIngestor.ingest` and `ingest_file` both end here (D-0034, DEC24)."""
    from ingestion.declared import apply_declared
    fields = dataset_schema.get("input_fields") or {}
    try:
        if fields:
            lf = import_declared_columns(lf, dataset_name, fields)
        return apply_declared(lf, dataset_name, dataset_schema, fields)
    except IngestionError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise IngestionError(f"Failed to read '{file_name}': {type(exc).__name__}: {str(exc)[:200]}",
                             tip="Check that the file is a valid tab-separated file and that the declared fields match it") from exc


def file_kind(path: Path) -> str:
    """How the ingestion reads a file of a dataset, by its suffix: "parquet" for `.parquet`, else "tsv" (tab-separated text).
    The same rule as the orchestrator's read of the file `locate_dataset_file` names."""
    return "parquet" if Path(path).suffix == ".parquet" else "tsv"


def _unreadable(shown: str, exc: BaseException) -> IngestionError:
    """The plain reason a file cannot be read at all (no header line, a row with more fields than the header, a quote never closed, a byte
    that is not UTF-8): the words of the reader without its class name, and what to check. For the Data Import panel (PROVISIONAL wording)."""
    if type(exc).__name__ == "NoDataError":
        return IngestionError(f"The file '{shown}' is empty: it has no header line and no rows.",
                              tip="Upload a tab-separated file with a header line and the data rows.")
    text = " ".join(str(exc).split("\n\n")[0].split())[:200]
    return IngestionError(f"The file '{shown}' cannot be read in full: {text}.",
                          tip="Check that every row has as many tab-separated fields as the header line, that every quote is closed, "
                              "and that the file is saved as UTF-8 text.")


def ingest_file(path: Path, dataset_name: str, dataset_schema: Dict[str, Any], kind: Optional[str] = None,
                file_name: Optional[str] = None) -> pl.LazyFrame:
    """The table the ingestion reads from THIS file for this dataset, whatever the `source` of the schema says; the WHOLE file is read once.

    Used to check a candidate file before it replaces a dataset's file (the Data Import panel). It is the same read as
    `DataIngestor.ingest` (same text read, same exact headers, same declared types), followed by one full read of the table as the ingestion
    reads it, so that what the engine will meet when it builds (a row with more fields than the header, a quote never closed, a byte that is
    not UTF-8, a value that does not fit its declared type) is met here, before anything is written. What this function does not decide is the
    name or format of the file (`.tsv` or `.parquet`): that is checked by the caller against the file that is stored. `kind` ("tsv" or
    "parquet", default `file_kind(path)`) is how the file will be read where it is stored; `file_name` is the name shown in a message when
    the path is a temporary one. Raises IngestionError with the ingestion's own reason (a failure of the reading itself in plain words, a rule
    of the recipe with the rule's own text); nothing is written. The table is read and dropped: the returned frame is lazy."""
    path = Path(path)
    shown = file_name or path.name
    kind = kind or file_kind(path)
    try:
        if kind == "parquet":
            lf = pl.scan_parquet(path)
        else:
            lf = pl.scan_csv(path, separator="\t", infer_schema=False)
        lf.collect_schema()
    except Exception as exc:  # noqa: BLE001
        raise _unreadable(shown, exc) from exc
    try:
        lf = read_as_declared(lf, dataset_name, dataset_schema, shown)
    except IngestionError as err:
        # a rule of the recipe (headers, types) has no cause and is kept as it is; a failure of the reading has the reader's error as cause
        if err.__cause__ is not None:
            raise _unreadable(shown, err.__cause__) from err.__cause__
        raise
    try:
        lf.collect()
    except Exception as exc:  # noqa: BLE001
        raise _unreadable(shown, exc) from exc
    return lf


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
        """The file of a dataset in the data folder (`find_dataset_file`: exact name, `.tsv` or `.parquet`)."""
        return find_dataset_file(self.data_dir, dataset_name)

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
                if resolved_path.suffix == ".parquet":
                    lf = pl.scan_parquet(resolved_path)
                else:
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

    def ingest(self, dataset_name: str, dataset_schema: Dict[str, Any]) -> Tuple[pl.LazyFrame, Path]:
        """Read the file as text, import only the declared fields, then apply `strip`, `null_values` and the declared
        Polars types (`ingestion.declared`); a value that does not fit fails and names the column and the values
        (spec 7.3, 7.4)."""
        lf, resolved_path = self._open(dataset_name, dataset_schema, as_text=True)
        return read_as_declared(lf, dataset_name, dataset_schema, resolved_path.name), resolved_path


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Manual execution hook for testing.")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    args = parser.parse_args()
    if args.test:
        print(f"Executing {__file__} in test mode.")
