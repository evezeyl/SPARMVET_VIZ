"""Data Import check (HOME, Data Import panel): what a file must be to replace the data file of a dataset.

What the HOME user needs: the panel must not accept a file that the next build cannot read, and must not refuse a file the engine
reads (the file with the recipe's own headers). A file is accepted when BOTH hold: (1) its name has the format of the file that is
stored (`.tsv` for a tab-separated dataset, `.parquet` for a Parquet one; this is a rule of the panel, by name, so a tab-separated
file named `.txt` or `.csv` is refused though the engine could read its content), and (2) the ingestion reads ALL of it for that
dataset (`ingestion.ingestor.ingest_file`: one full read with the engine's own code: exact `original_name` headers, declared types,
`strip`, `null_values`, every row, every declared column). The check is not a second copy of the content rule: it runs the ingestion's
own read on the candidate, BEFORE anything is written, and it writes to the place the orchestrator reads (`DataOrchestrator.file_place`).
When the replaced file is also the file of other tables of the recipe, every one of those tables must read it too. All files of one
Apply are checked first and none is written unless every one passes.

Not decided, so not built (task DATA-IMPORT-OVERWRITE): the overwrite of the recipe's data file with no copy of the old one and
no record of the original file name; this module keeps today's behaviour there (the file is replaced in place).
PROVISIONAL (the coordinator's choices, not decisions of the owner): a recipe imported from a bundle is refused (`IMPORTED_REFUSAL`),
and so is a deployment that finds its data files by table name (`BY_DATASET_ID_REFUSAL`).

Two-Category Law (ADR-045): pure logic, no Shiny; the handler `app/handlers/data_import_handlers.py` only wires it.
Consumed by: app/handlers/data_import_handlers.py. If deleted: the panel has no check and writes nothing.
"""
from __future__ import annotations

# @deps
# provides: function:apply_import, function:check_candidates, function:store_all, function:refresh_replaced, class:Candidate, class:Verdict, class:ImportOutcome, class:DataImportWriteError, constant:IMPORTED_REFUSAL, constant:BY_DATASET_ID_REFUSAL
# consumes: libs/ingestion/src/ingestion/ingestor.py (ingest_file, file_kind), app/modules/orchestrator.py (dataset_schemas, file_place, import_data_dir, discover_by_dataset_id)
# consumed_by: app/handlers/data_import_handlers.py, app/tests/test_data_import_check.py
# doc: .claude/rules/ui_implementation_contract.md#9, .claude/design/recipe_format_spec.md (DEC24, DEC25), D-0034, D-0050
# @end_deps

import os
import shutil
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable

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

# PROVISIONAL (the coordinator's choice, not a decision of the owner; task DATA-IMPORT-OVERWRITE waits for her): a deployment that finds its data
# files by table name (`data_lookup: by_dataset_id`) delivers them from outside (a pipeline), and the panel would overwrite the real file with no
# copy of it. Until the owner decides the overwrite, the panel writes nothing there. Options for the owner: keep this refusal; or allow the
# overwrite and keep the old file and the name of the uploaded one (the open choice of DATA-IMPORT-OVERWRITE).
BY_DATASET_ID_REFUSAL = "The data of this deployment is delivered by the pipeline and cannot be replaced from here."
BY_DATASET_ID_WAY_OUT = "To use other data, ask the person who runs this deployment to supply it."

# PROVISIONAL wording: the refusal of a file whose headers are not the ones the recipe reads. The reason is the ingestion's own first sentence;
# the way out is written for the person who uploads (the ingestion's own text is written for the author of the recipe).
HEADERS_WAY_OUT = ("Correct the column headers of the file so that they are spelled exactly as the expected file headers above "
                   "(upper and lower case count), then upload it again.")

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
    shared: tuple[str, ...] = ()      # the other tables of the recipe that read the same file (each of them reads the candidate too)

    @property
    def ok(self) -> bool:
        return not self.error

    @property
    def tables(self) -> tuple[str, ...]:
        """Every table of the recipe whose data this file replaces: the assigned dataset first, then the ones that share its file."""
        return (self.ds_id, *self.shared)


@dataclass(frozen=True)
class ImportOutcome:
    """The result of one Apply: a verdict per file, the places written (empty when any file was refused: nothing is written then),
    the tables whose file was replaced (what the caller must refresh) and `write_error`, the plain message when a file could not be
    written ("" otherwise; `written` then holds the places already replaced, which are not undone)."""
    verdicts: list[Verdict]
    written: list[Path]
    tables_written: list[str] = field(default_factory=list)
    write_error: str = ""

    @property
    def ok(self) -> bool:
        return all(v.ok for v in self.verdicts)


class DataImportWriteError(OSError):
    """A file could not be written; the message says plainly which files are already replaced and which are not.
    `replaced` holds the places already replaced (empty when nothing was)."""

    def __init__(self, message: str, replaced: Iterable[Path] = ()):
        super().__init__(message)
        self.replaced = list(replaced)


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
    """The plain reason of the ingestion (its message and its way out), in the form the panel shows on two lines.
    For headers the file lacks the message is the ingestion's own, the way out is the one for the person who uploads (`HEADERS_WAY_OUT`)."""
    evidence = getattr(getattr(exc, "pipeline_error", None), "evidence", None)
    if isinstance(evidence, dict) and "missing" in evidence:
        return str(exc) + SEPARATOR + HEADERS_WAY_OUT
    tip = getattr(exc, "tip", "") if isinstance(exc, SPARMVET_Error) else ""
    return str(exc) + (SEPARATOR + tip if tip else "")


def _split(reason: str) -> tuple[str, str]:
    message, _, way_out = reason.partition(SEPARATOR)
    return message, way_out


def _target_of(orchestrator: Any, recipe_id: str, ds_id: str, schemas: dict) -> Path | None:
    """The place of a dataset's file, or None when it has none or cannot be told (the reason is given where the place is needed)."""
    if ds_id not in schemas or orchestrator.discover_by_dataset_id:
        return None
    try:
        place = orchestrator.file_place(recipe_id, ds_id, schemas[ds_id])
    except SPARMVET_Error:
        return None
    return place.resolve() if place is not None else None


def check_candidates(orchestrator: Any, recipe_id: str, candidates: Iterable[Candidate]) -> list[Verdict]:
    """Check every candidate before anything is written; one Verdict per candidate, in the same order.

    A candidate is accepted when (1) it is assigned to a dataset of the recipe, (2) the recipe is not one imported from a bundle and the deployment
    does not deliver its data by table name, (3) it has the format of the file the orchestrator reads for that dataset, (4) no other candidate of the
    same Apply is assigned to that dataset or to another table that reads the same file, (5) the ingestion reads all of it for that dataset
    (`ingest_file`: the exact `original_name` headers, the declared types, every row), and (6) every other table of the recipe that reads the same file
    reads it too."""
    candidates = list(candidates)
    try:
        schemas = orchestrator.dataset_schemas(recipe_id)
    except SPARMVET_Error as exc:
        # the recipe itself cannot be read: no file can be checked against it, and none is written
        return [Verdict(c.name, c.ds_id, c.tmp_path, None, _reason(exc)) for c in candidates]
    assigned = Counter(c.ds_id for c in candidates if c.ds_id)
    places = [_target_of(orchestrator, recipe_id, c.ds_id, schemas) for c in candidates]
    by_place: dict[Path, list[str]] = {}
    for c, place in zip(candidates, places):
        if place is not None and c.ds_id:
            by_place.setdefault(place, []).append(c.ds_id)
    return [_check_one(orchestrator, recipe_id, c, schemas, assigned, by_place, places[i]) for i, c in enumerate(candidates)]


def _check_one(orchestrator: Any, recipe_id: str, c: Candidate, schemas: dict, assigned: Counter, by_place: dict[Path, list[str]],
               place: Path | None) -> Verdict:
    def refused(error: str, target: Path | None = None) -> Verdict:
        return Verdict(c.name, c.ds_id, c.tmp_path, target, error)

    if not c.ds_id:
        return refused(_say("No dataset selected.", "Choose the dataset this file replaces."))
    if c.ds_id not in schemas:
        return refused(_say(f"The data analysis recipe '{recipe_id}' has no dataset '{c.ds_id}'.", "Choose one of the datasets of the recipe."))
    if assigned[c.ds_id] > 1:
        return refused(_say(f"More than one of the files is assigned to the dataset '{c.ds_id}'.", "Assign each dataset one file."))
    schema = schemas[c.ds_id]
    if orchestrator.discover_by_dataset_id and orchestrator.import_data_dir(recipe_id) is None:
        return refused(_say(BY_DATASET_ID_REFUSAL, BY_DATASET_ID_WAY_OUT))
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
    if place is not None and len(by_place[place]) > 1:
        return refused(_say(f"The datasets {', '.join(repr(d) for d in sorted(by_place[place]))} are read from the same data file ({target.name}), "
                            "and more than one of the files of this Apply is assigned to them.",
                            "Upload one file for them: they share one data file."), target)
    kind = file_kind(target)
    try:
        ingest_file(c.tmp_path, c.ds_id, schema, kind=kind, file_name=c.name)
    except Exception as exc:  # noqa: BLE001 - the ingestion's own reason, whatever its type, goes to the user
        return refused(_reason(exc), target)
    shared = tuple(other for other in sorted(schemas) if other != c.ds_id and _target_of(orchestrator, recipe_id, other, schemas) == target.resolve())
    for other in shared:
        try:
            ingest_file(c.tmp_path, other, schemas[other], kind=kind, file_name=c.name)
        except Exception as exc:  # noqa: BLE001
            message, way_out = _split(_reason(exc))
            return refused(_say(f"This file is also the data file of the table '{other}', and '{other}' cannot read it: {message}", way_out), target)
    return Verdict(c.name, c.ds_id, c.tmp_path, target, "", shared)


def store_all(verdicts: Iterable[Verdict]) -> list[Path]:
    """Write every accepted file to its place, only when every verdict is accepted; returns the places written.

    Each file is first copied next to its place and the copies are put in place only when all copies exist, so a file that cannot
    be copied (disk, permission) leaves every dataset as it was, and a copy that fails midway is removed. Today's overwrite is kept: the old file
    is replaced in place (no copy of it, no record of the original name: task DATA-IMPORT-OVERWRITE waits for the owner). When a replace fails
    after others succeeded, those stay replaced: the error names them and carries them in `replaced`."""
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
            staged.append((v, stage))          # listed before the copy: a copy that fails midway leaves a partial file that is removed below
            shutil.copyfile(v.tmp_path, stage)
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
        raise DataImportWriteError(f"The import stopped at '{v.name}' ({v.target}): {exc}. Files already replaced: {replaced}.", done) from exc
    return done


def apply_import(orchestrator: Any, recipe_id: str, candidates: Iterable[Candidate]) -> ImportOutcome:
    """One Apply of the Data Import panel: check every file, and write them all only if every one is accepted.

    A file that cannot be written does not raise: the outcome carries `write_error` (what is replaced and what is not) and the places
    already replaced in `written`, with their tables in `tables_written`, so that the caller refreshes what changed."""
    verdicts = check_candidates(orchestrator, recipe_id, candidates)
    if not all(v.ok for v in verdicts):
        return ImportOutcome(verdicts, [])
    try:
        written = store_all(verdicts)
        error = ""
    except DataImportWriteError as exc:
        written, error = exc.replaced, str(exc)
    tables = [t for v in verdicts if v.target in written for t in v.tables]
    return ImportOutcome(verdicts, written, tables, error)


def refresh_replaced(outcome: ImportOutcome, recipe_id: str, anchor_dir: Path, set_cached_asset: Callable[..., Any]) -> bool:
    """Drop what the app kept of every table whose file was replaced (its stored anchor, its cached table), also when a later file of the
    same Apply could not be written. Returns True when anything was replaced, i.e. when the plots must be refreshed."""
    for ds_id in outcome.tables_written:
        stored = anchor_dir / f"{ds_id}.parquet"
        if stored.exists():
            stored.unlink()
        set_cached_asset(recipe_id, ds_id, "anchor", "lf", None)
    return bool(outcome.written)
