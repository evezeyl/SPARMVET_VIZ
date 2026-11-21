"""Data Import check: a file is accepted if and only if the engine's ingestion reads it (HOME, Data Import panel).

What the HOME user needs: the panel must not accept a file that the next build cannot read, nor refuse a file the engine reads
(the file with the recipe's own headers). So the check is not a second copy of the rule: it runs the ingestion's own read
(`ingestion.ingestor.ingest_file`: exact `original_name` headers, declared types, `strip`, `null_values`) on the candidate file,
for that dataset of that recipe, BEFORE anything is written, and it writes to the place the orchestrator reads
(`DataOrchestrator.file_place`). All files of one Apply are checked first and none is written unless every one passes.

Not decided, so not built (task DATA-IMPORT-OVERWRITE): the overwrite of the recipe's data file with no copy of the old one and
no record of the original file name; this module keeps today's behaviour there (the file is replaced in place).
PROVISIONAL (an agent's choice, to be confirmed by the owner): a recipe imported from a bundle is refused, not written to
(see `IMPORTED_REFUSAL`).

Two-Category Law (ADR-045): pure logic, no Shiny; the handler `app/handlers/data_import_handlers.py` only wires it.
Consumed by: app/handlers/data_import_handlers.py. If deleted: the panel has no check and writes nothing.
"""
from __future__ import annotations

# @deps
# provides: function:apply_import, function:check_candidates, function:store_all, class:Candidate, class:Verdict, class:ImportOutcome, class:DataImportWriteError
# consumes: libs/ingestion/src/ingestion/ingestor.py (ingest_file, file_kind), app/modules/orchestrator.py (dataset_schemas, file_place, import_data_dir)
# consumed_by: app/handlers/data_import_handlers.py, app/tests/test_data_import_check.py
# doc: .claude/rules/ui_implementation_contract.md#9, .claude/design/recipe_format_spec.md (DEC24, DEC25), D-0034, D-0050
# @end_deps

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from ingestion.ingestor import file_kind, ingest_file
from utils.errors import SPARMVET_Error

# The reason and the way out are joined by " — "; the panel shows them on two lines (`import_error_block`).
SEPARATOR = " — "

# PROVISIONAL (an agent's choice, not Eve's): the data of a recipe imported from a bundle is only what the bundle carried
# (orchestrator `_read_source`), so Data Import does not write there. Options for the owner: (a) refuse, as now; (b) replace the
# file in the import's data folder with the same overwrite rule as any dataset (it would no longer be what the bundle's hashes
# verified); (c) store an upload in a place of its own that the orchestrator would then have to read, with a record of it.
IMPORTED_REFUSAL = ("This recipe was imported from a bundle and reads its data from the folder of that import ({folder}); "
                    "Data Import cannot replace it here.")
IMPORTED_WAY_OUT = "The data of an import is only what its bundle carried. To use other data, import a bundle that holds it."

_COMMA = {".csv": "a comma-separated file"}
_EXCEL = {".xlsx": "an Excel file", ".xls": "an Excel file"}


@dataclass(frozen=True)
class Candidate:
    """One uploaded file and the dataset the user assigned it to: its name as uploaded, where its temporary copy is, the dataset id ("" when none)."""
    name: str
    tmp_path: Path
    ds_id: str


@dataclass(frozen=True)
class Verdict:
    """The check of one candidate: where it would be stored (`target`, None when there is none) and `error` ("" when the file is accepted)."""
    name: str
    ds_id: str
    tmp_path: Path
    target: Path | None
    error: str

    @property
    def ok(self) -> bool:
        return not self.error


@dataclass(frozen=True)
class ImportOutcome:
    """The result of one Apply: a verdict per file, and the places written (empty when any file was refused: nothing is written then)."""
    verdicts: list[Verdict]
    written: list[Path]

    @property
    def ok(self) -> bool:
        return all(v.ok for v in self.verdicts)


class DataImportWriteError(OSError):
    """A file could not be written; the message says plainly which files are already replaced and which are not."""


def _say(message: str, way_out: str) -> str:
    return f"{message}{SEPARATOR}{way_out}"


def _format_refusal(name: str, target: Path) -> str | None:
    """The refusal of a file whose format the stored file cannot hold, or None when the file has the format of the stored one.
    Converting a file for the user is not decided, so none is done: the user converts it and uploads it again."""
    suffix = Path(name).suffix.lower()
    stored = file_kind(target)
    if suffix == ".tsv" and stored == "tsv":
        return None
    if suffix == ".parquet" and stored == "parquet":
        return None
    if stored == "parquet":
        return _say(f"The file of this dataset is a Parquet file ({target.name}); '{name}' is not, and Data Import does not convert files.",
                    "Upload a Parquet file for this dataset.")
    kinds = {**_COMMA, **_EXCEL}
    if suffix in kinds:
        return _say(f"'{name}' is {kinds[suffix]}. This dataset is read from a tab-separated file ({target.name}), and Data Import does not convert files.",
                    "Convert it to a tab-separated file (.tsv) first, then upload it again.")
    if suffix == ".parquet":
        return _say(f"'{name}' is a Parquet file. This dataset is read from a tab-separated file ({target.name}), and Data Import does not convert files.",
                    "Convert it to a tab-separated file (.tsv) first, then upload it again.")
    return _say(f"'{name}' is not a file type this dataset can be read from. It is read from a tab-separated file ({target.name}).",
                "Upload a tab-separated file (.tsv).")


def _reason(exc: BaseException) -> str:
    """The plain reason of the ingestion (its message and its way out), in the form the panel shows on two lines."""
    tip = getattr(exc, "tip", "") if isinstance(exc, SPARMVET_Error) else ""
    return str(exc) + (SEPARATOR + tip if tip else "")


def check_candidates(orchestrator: Any, recipe_id: str, candidates: Iterable[Candidate]) -> list[Verdict]:
    """Check every candidate before anything is written; one Verdict per candidate, in the same order.

    A candidate is accepted when (1) it is assigned to a dataset of the recipe, (2) the recipe is not one imported from a bundle,
    (3) it has the format of the file the orchestrator reads for that dataset, (4) no other candidate of the same Apply is assigned to
    the same dataset, and (5) the ingestion reads it for that dataset (`ingest_file`: the exact `original_name` headers, the declared types)."""
    candidates = list(candidates)
    try:
        schemas = orchestrator.dataset_schemas(recipe_id)
    except SPARMVET_Error as exc:
        # the recipe itself cannot be read: no file can be checked against it, and none is written
        return [Verdict(c.name, c.ds_id, c.tmp_path, None, _reason(exc)) for c in candidates]
    assigned: dict[str, int] = {}
    for c in candidates:
        if c.ds_id:
            assigned[c.ds_id] = assigned.get(c.ds_id, 0) + 1
    verdicts: list[Verdict] = []
    for c in candidates:
        verdicts.append(_check_one(orchestrator, recipe_id, c, schemas, assigned))
    return verdicts


def _check_one(orchestrator: Any, recipe_id: str, c: Candidate, schemas: dict, assigned: dict[str, int]) -> Verdict:
    def refused(error: str, target: Path | None = None) -> Verdict:
        return Verdict(c.name, c.ds_id, c.tmp_path, target, error)

    if not c.ds_id:
        return refused(_say("No dataset selected.", "Choose the dataset this file replaces."))
    if c.ds_id not in schemas:
        return refused(_say(f"The data analysis recipe '{recipe_id}' has no dataset '{c.ds_id}'.", "Choose one of the datasets of the recipe."))
    if assigned.get(c.ds_id, 0) > 1:
        return refused(_say(f"More than one of the files is assigned to the dataset '{c.ds_id}'.", "Assign each dataset one file."))
    schema = schemas[c.ds_id]
    try:
        target = orchestrator.file_place(recipe_id, c.ds_id, schema)
    except SPARMVET_Error as exc:
        return refused(_reason(exc))
    if target is None:
        folder = orchestrator.import_data_dir(recipe_id)
        return refused(_say(IMPORTED_REFUSAL.format(folder=folder), IMPORTED_WAY_OUT))
    wrong_format = _format_refusal(c.name, target)
    if wrong_format:
        return refused(wrong_format, target)
    try:
        ingest_file(c.tmp_path, c.ds_id, schema, kind=file_kind(target), file_name=c.name)
    except Exception as exc:  # noqa: BLE001 - the ingestion's own reason, whatever its type, goes to the user
        return refused(_reason(exc), target)
    return Verdict(c.name, c.ds_id, c.tmp_path, target, "")


def store_all(verdicts: Iterable[Verdict]) -> list[Path]:
    """Write every accepted file to its place, only when every verdict is accepted; returns the places written.

    Each file is first copied next to its place and the copies are put in place only when all copies exist, so a file that cannot
    be copied (disk, permission) leaves every dataset as it was. Today's overwrite is kept: the old file is replaced in place
    (no copy of it, no record of the original name: task DATA-IMPORT-OVERWRITE waits for the owner)."""
    verdicts = list(verdicts)
    if not verdicts:
        return []
    bad = [v.name for v in verdicts if not v.ok or v.target is None]
    if bad:
        raise ValueError(f"store_all is only called when every file is accepted; not accepted: {bad}")
    staged: list[tuple[Verdict, Path]] = []
    try:
        for v in verdicts:
            v.target.parent.mkdir(parents=True, exist_ok=True)
            stage = v.target.with_name(v.target.name + ".import-tmp")
            shutil.copyfile(v.tmp_path, stage)
            staged.append((v, stage))
    except OSError as exc:
        for _, stage in staged:
            stage.unlink(missing_ok=True)
        raise DataImportWriteError(f"Nothing was imported: could not write '{v.name}' to {v.target}: {exc}") from exc
    done: list[Path] = []
    try:
        for v, stage in staged:
            os.replace(stage, v.target)
            done.append(v.target)
    except OSError as exc:
        for _, stage in staged:
            stage.unlink(missing_ok=True)
        replaced = ", ".join(str(p) for p in done) or "none"
        raise DataImportWriteError(f"The import stopped at '{v.name}' ({v.target}): {exc}. Files already replaced: {replaced}.") from exc
    return done


def apply_import(orchestrator: Any, recipe_id: str, candidates: Iterable[Candidate]) -> ImportOutcome:
    """One Apply of the Data Import panel: check every file, and write them all only if every one is accepted.

    Raises DataImportWriteError when an accepted file cannot be written (the message says what is already replaced)."""
    verdicts = check_candidates(orchestrator, recipe_id, candidates)
    if not all(v.ok for v in verdicts):
        return ImportOutcome(verdicts, [])
    return ImportOutcome(verdicts, store_all(verdicts))
