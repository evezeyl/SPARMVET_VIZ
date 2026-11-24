"""The warning of the ids in HOME and in the export: the words, the read state and the click "I have read this" (D-0582, D-0585, D-0613). Headless, no Shiny.

What she decided (D-0582): the person who uses the results MUST read the log of the ids, and the app lets the user upload if he wants to: where there is a panel,
a red warning and a button "I have read this" that blocks nothing; the completion is applied anyway; the click is recorded in the log; with no user the log says
"automatic, no user" and the log travels with the export. Only a person who reads the logs of a static deployment can act on it (D-0585).

PROVISIONAL (an agent's choices, D-0613: the small open points are built the simplest way and listed): which findings raise the warning; the words of every line;
that the click is recorded with the date and the word "read in the app" and nothing that identifies a person (the app has no user identity); that the read state
is kept per recipe and data batch (the same fingerprints read before: the quiet line at once; a changed recipe or new data: the red warning again), and is
kept in the log file itself, so a new session on the same data finds it; that a click that could not be written is said in the warning, never hidden.

# @deps
# provides: function:warning_lines, function:has_warning, function:read_status, function:mark_read, function:export_sentences, function:quiet_line, function:log_place_text, constant:READ_IN_APP, class:ReadStatus
# consumes: app/modules/id_check_run.py (IdCheckRun), libs/utils/src/utils/id_completion.py (added_line_words), libs/utils/src/utils/id_log.py (read_log, record_read, log_path)
# consumed_by: app/handlers/id_warning_handlers.py, app/handlers/export_handlers.py, app/tests/test_id_warning.py
# doc: .claude/knowledge/decision_ledger.md (D-0582, D-0585, D-0613), .claude/rules/ui_implementation_contract.md#7.2
# @end_deps
"""
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import yaml

from app.modules.id_check_run import IdCheckRun
from utils.id_completion import added_line_words
from utils.id_log import AUTOMATIC, READ, LogOutcome, log_path, read_log, record_read

READ_IN_APP = "read in the app"


@dataclass(frozen=True)
class ReadStatus:
    """Whether a person said "I have read this" for this recipe and these data. `when` is the date of the last such click."""
    read: bool
    when: Optional[str] = None
    who: Optional[str] = None


def warning_lines(run: Optional[IdCheckRun]) -> List[str]:
    """What the user must know, one plain line per finding; empty when the ids are equal everywhere (then there is no warning).

    A line per table for: lines added ("missing in original table", with the sentence of the recipe maker), ids of a table that are not in the metadata, lines with
    no usable id and a difference after the completion (a bug of the app). Then the faults of the checks and of the log itself."""
    if run is None:
        return []
    lines: List[str] = []
    if run.report is not None:
        words = added_line_words()
        for t in run.report.tables:
            if t.added:
                lines.append(f"{t.table}: {len(t.added)} {'entity' if len(t.added) == 1 else 'entities'} {words}. The recipe says: {t.meaning.strip()}")
            if t.not_in_metadata:
                lines.append(f"{t.table}: {len(t.not_in_metadata)} id(s) are not in the metadata.")
            if t.no_id_lines:
                lines.append(f"{t.table}: {t.no_id_lines} line(s) have no usable id; they stay as they are and are not completed.")
            if t.after_difference:
                lines.append(f"{t.table}: after the completion this table does not hold the same ids as the others. This is a fault of the app: report it.")
    if run.error:
        lines.append(f"The checks of the ids could not be made: {run.error}")
    if run.log_warning:
        lines.append(run.log_warning)
    return lines


def has_warning(run: Optional[IdCheckRun]) -> bool:
    return bool(warning_lines(run))


def log_place_text(run: Optional[IdCheckRun]) -> str:
    """Where the full list is: the file of the log (when it was written) and that it travels with every export."""
    where = str(run.outcome.path) if run is not None and run.outcome is not None and run.outcome.written and run.outcome.path else None
    place = f"The full list is in the log of the ids: {where}." if where else "The log of the ids could not be written; its text is shown here and is in the export."
    return f"{place} Every export holds it (id_log.yaml)."


def read_status(folder: Path, recipe_id: str, recipe_sha256: str, data_batch_hash: str) -> ReadStatus:
    """The last click "I have read this" of this recipe on these data, found in the log file. A log that is missing or cannot be read says "not read"."""
    try:
        log = read_log(log_path(folder, recipe_id))
    except (OSError, ValueError, yaml.YAMLError):
        return ReadStatus(False)
    mine = [e for e in log["entries"] if isinstance(e, dict) and e.get("kind") == READ
            and e.get("recipe_sha256") == recipe_sha256 and e.get("data_batch_hash") == data_batch_hash]
    if not mine:
        return ReadStatus(False)
    return ReadStatus(True, str(mine[-1].get("when")), str(mine[-1].get("who")))


def mark_read(folder: Path, recipe_id: str, recipe_sha256: str, data_batch_hash: str, when: Optional[str] = None) -> LogOutcome:
    """The click "I have read this": one entry of kind `read` in the log. It never blocks anything; when the folder cannot be written the outcome says so."""
    return record_read(folder, recipe_id, recipe_sha256, data_batch_hash, READ_IN_APP, when)


def date_of(when: Optional[str]) -> str:
    """The day of an ISO date and time (the quiet line shows the day)."""
    return (when or "").split("T")[0]


def quiet_line(status: ReadStatus) -> str:
    return f"Id warnings read on {date_of(status.when)}."


def export_sentences(run: Optional[IdCheckRun], status: ReadStatus) -> List[str]:
    """The sentences of README.txt and report.qmd about the ids: what was found (the app's words and the recipe maker's sentence per table) and whether the
    warning was read in the app or the log is "automatic, no user". Empty when no table of the recipe takes part. Never refuses the export."""
    if run is None or (run.report is None and not run.error):
        return []
    out: List[str] = []
    findings = warning_lines(run)
    if findings:
        out.append("The ids of the tables were not equal; the log of the ids (id_log.yaml) lists them:")
        out += [f"- {line}" for line in findings]
    else:
        out.append("The ids are equal in every table of the recipe; the log of the ids (id_log.yaml) says so.")
        return out
    if status.read:
        out.append(f"The warning of the ids was read in the app on {date_of(status.when)} ({status.who}).")
    else:
        out.append(f"No person has said in the app that the log of the ids was read: it was written automatically ({AUTOMATIC}). "
                   "The person who uses these results must read it.")
    return out
