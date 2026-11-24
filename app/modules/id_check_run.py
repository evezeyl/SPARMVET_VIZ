"""The checks of the ids for an opened recipe, and their log (D-0581, D-0582, D-0590 to D-0592; PROVISIONAL form, D-0613). Headless, no Shiny.

When HOME opens a recipe it makes the three checks of the ids (`DataOrchestrator.id_report`), writes what they found to the log of the ids, and returns the
findings in plain words. Everything here is a warning: nothing refuses a recipe and nothing stops the opening. The log is written automatically ("automatic, no
user"); the button "I have read this" comes in a later step (`utils.id_log.record_read` is the function it will call).

The folder of the log is `<user_data>/_id_logs` (next to `_sessions`). When it cannot be written the opening goes on, the text of the entry is printed to the
console and returned (`IdCheckRun.log_text`), so that the export and a warning can show it (the pattern of `SessionManager`, D-0581).

# @deps
# provides: function:run_id_checks, function:id_log_folder, function:export_log_text, class:IdCheckRun, constant:ID_LOG_FOLDER
# consumes: app/modules/orchestrator.py (id_report), libs/utils/src/utils/id_completion.py (report_lines), libs/utils/src/utils/id_log.py (build_entry, write_entry, read_log, entry_text, log_path)
# consumed_by: app/handlers/opening_handlers.py, app/handlers/export_handlers.py, app/tests/test_id_checks_log.py
# doc: .claude/knowledge/decision_ledger.md (D-0575, D-0576, D-0581, D-0582, D-0592), .claude/rules/rules_data_analysis_recipe_structure.md#11
# @end_deps
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import yaml

from utils.id_completion import IdReport, report_lines
from utils.id_log import AUTOMATIC, CHECKS, LogOutcome, build_entry, log_path, read_log, write_entry

ID_LOG_FOLDER = "_id_logs"


@dataclass(frozen=True)
class IdCheckRun:
    """What the checks of the ids of one opened recipe gave. `report` is None when no table takes part or when the checks could not be made (`error` says why,
    in plain words). `lines` are the findings in plain words (empty when the ids are equal everywhere). `outcome` is what the log did; `log_text` is the entry in
    plain words, always there when there is a report, for the export and for a warning when `outcome.written` is False."""
    report: Optional[IdReport]
    lines: tuple
    outcome: Optional[LogOutcome]
    error: Optional[str] = None

    @property
    def log_text(self) -> Optional[str]:
        return self.outcome.text if self.outcome is not None else None

    @property
    def log_warning(self) -> Optional[str]:
        """The one plain sentence for a warning when the log could not be written, else None."""
        if self.outcome is None or self.outcome.written:
            return None
        return (f"The log of the ids could not be written ({self.outcome.problem}). Its text is in the console and in the export; "
                "a person who reads the logs of this deployment will not find it in the log folder.")


def id_log_folder(user_data: Path) -> Path:
    """The folder of the logs of the ids: `<user_data>/_id_logs`."""
    return Path(user_data) / ID_LOG_FOLDER


def run_id_checks(orchestrator, recipe_id: str, raw: dict, keys: Any, user_data: Path, when: Optional[str] = None, write: bool = True) -> IdCheckRun:
    """Make the three checks of the ids of a recipe and write the log (`write=False`: only the checks, for the export, which writes its own copy). Never raises: a fault of the checks is returned as `error` (the opening has its own
    way to report a table that cannot be read). `keys` are the keys of the opening (`recipe sha256` and `data batch hash` are the fingerprints of the entry)."""
    try:
        report = orchestrator.id_report(recipe_id, raw)
        if report is None:
            return IdCheckRun(None, (), None)
        entry = build_entry(report, recipe_id, keys.data_analysis_recipe_sha256, keys.data_batch_hash, when=when)
        lines = tuple(report_lines(report))
        # `write_entry` never raises (a folder that cannot be written is returned in the outcome), so the opening cannot be stopped from here
        return IdCheckRun(report, lines, write_entry(id_log_folder(user_data), entry) if write else None)
    except Exception as exc:   # warnings only: what stops the checks is said, never raised (the recipe, the keys and the data may be anything at this point)
        return IdCheckRun(None, (), None, f"the checks of the ids could not be made: {exc}")


def export_log_text(user_data: Path, recipe_id: str, run: IdCheckRun, recipe_sha256: str, data_batch_hash: str, when: Optional[str] = None) -> Optional[str]:
    """The text of the file `id_log.yaml` of an export bundle: the log of this recipe as it is in the user folder (every entry, the ones that say a person read
    it too), and the entry of THIS export's recipe and data when the file does not hold that state yet (the folder could not be written, or this is the first
    export of it). None when no table of the recipe takes part. A log file that cannot be read is replaced by the entry alone, and said in it."""
    if run.report is None:
        return None
    entry = build_entry(run.report, recipe_id, recipe_sha256, data_batch_hash, when=when, who=AUTOMATIC)
    note = None
    try:
        log = read_log(log_path(id_log_folder(user_data), recipe_id))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        log, note = {"format": 1, "entries": []}, f"The log file of the user folder could not be read ({exc}); this file holds the entry of this export only."
    held = [e for e in log["entries"] if isinstance(e, dict) and e.get("kind") == CHECKS
            and e.get("recipe_sha256") == recipe_sha256 and e.get("data_batch_hash") == data_batch_hash]
    if not held:
        log["entries"].append(entry)
    out = {"format": log["format"], "about": ("The log of the ids of this recipe: what the checks of the ids found, and who read it. Written automatically; "
                                               "the person who uses these results must read it (D-0582)."), "entries": log["entries"]}
    if note:
        out["note"] = note
    return yaml.safe_dump(out, sort_keys=False, allow_unicode=True)

