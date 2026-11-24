"""The log of the ids: what the checks of the ids found, written automatically, kept apart from the audit log (D-0575, D-0576, D-0581, D-0582, D-0592).

Her words: the log is "separate" (D-0576), "written automatically, in a specific directory" (D-0581), "as simple as: the ids are written differently in the different
output of a pipeline" (D-0592), and "the user / person utilizing the results MUST read that log" (D-0582). In a static deployment only a person who reads the
logs can act on it (D-0585).

One file per recipe in one folder, `<folder>/<recipe id>.id_log.yaml`: `format: 1` and a list `entries`. An entry of kind `checks` holds the report of the
checks (the numbers per table and the unmatched ids, the lines with no usable id), the date, the fingerprints of the recipe and of the data, and who wrote it
(`automatic, no user`). An entry of kind `read` records that a person said "I have read this" (the button is in HOME, `app/modules/id_warning.py` calls `record_read`). An entry of kind `checks` is added when the recipe or the data fingerprint differs from the last `checks` entry of the file: opening the same recipe
on the same data again adds nothing (the log is a record of states, not of visits). PROVISIONAL (an agent's choices, D-0613): the folder, the file name, the keys
and the rule of one entry per state.

When the folder cannot be written (nothing is written, nothing stops), the text of the entry is printed to the console and returned, so that the export and a
warning can show it (the pattern of `SessionManager._probe_writable`, D-0581).

Pure Python (YAML only), no Shiny, no Polars.

# @deps
# provides: function:build_entry, function:write_entry, function:record_read, function:read_log, function:entry_text, function:log_path, class:LogOutcome
# consumes: libs/utils/src/utils/id_completion.py (IdReport)
# consumed_by: app/modules/id_check_run.py, app/modules/id_warning.py, app/handlers/export_handlers.py
# doc: .claude/knowledge/decision_ledger.md (D-0575, D-0576, D-0581, D-0582, D-0592), .claude/design/studies/whole_picture_2026-11/CAUSE_AND_SOLUTIONS_ZEROS.md
# @end_deps
"""
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from utils.id_completion import IdReport, added_line_words

FORMAT = 1
AUTOMATIC = "automatic, no user"
CHECKS = "checks"
READ = "read"
FILE_SUFFIX = ".id_log.yaml"


@dataclass(frozen=True)
class LogOutcome:
    """What `write_entry` did. `written`: the entry is in the file (or was already there, `new` False). `text`: the entry in plain words, always, so that the
    export and a warning can show it when the file could not be written. `problem`: why the file could not be written, or None."""
    written: bool
    new: bool
    path: Optional[Path]
    text: str
    problem: Optional[str] = None


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def log_path(folder: Path, recipe_id: str) -> Path:
    """The file of one recipe: `<folder>/<recipe id>.id_log.yaml`."""
    return Path(folder) / f"{recipe_id}{FILE_SUFFIX}"


def build_entry(report: IdReport, recipe_id: str, recipe_sha256: str, data_batch_hash: str, when: Optional[str] = None, who: str = AUTOMATIC) -> Dict[str, Any]:
    """The entry of kind `checks`: the date, who wrote it, the fingerprints of the recipe and of the data, the report."""
    return {"kind": CHECKS, "when": when or _now(), "who": who, "recipe": recipe_id, "recipe_sha256": recipe_sha256, "data_batch_hash": data_batch_hash,
            "ids": report.as_dict()}


def entry_text(entry: Dict[str, Any]) -> str:
    """One entry in plain words (for the console, the export and a warning). PROVISIONAL wording (the owner reads it)."""
    if entry["kind"] == READ:
        return f"{entry['when']}: {entry['who']} has read the log of the ids of '{entry['recipe']}' (recipe {entry['recipe_sha256'][:12]}, data {entry['data_batch_hash'][:12]})."
    ids = entry["ids"]
    head = [f"Log of the ids of '{entry['recipe']}', {entry['when']}, written by: {entry['who']}.",
            f"Recipe {entry['recipe_sha256'][:12]}, data {entry['data_batch_hash'][:12]}. Ids in the union of all the tables: {ids['ids_in_the_union']}. "
            f"Metadata: {'yes' if ids['has_metadata'] else 'none'}. Check of the equal sets after the completion: {ids['check_3']}."]
    for t in ids["tables"]:
        parts = [f"{t['table']} ({t['kind']}): {t['rows']} line(s), {t['distinct_ids']} distinct id(s)"]
        if t["lines_with_no_usable_id"]:
            parts.append(f"{t['lines_with_no_usable_id']} line(s) with no usable id (numbers: {', '.join(str(n) for n in t.get('lines_with_no_usable_id_numbers', []))})")
        if t["ids_added"]["count"]:
            parts.append(f"{t['ids_added']['count']} line(s) added, marked \"{t.get('added_line_words', added_line_words())}\" in {t['marker']}: {', '.join(t['ids_added']['ids'])}. "
                         f"What an added line means for {t['table']}, in the words of the recipe maker: {t['meaning'].strip().rstrip('.')}")
        c1, c2 = t.get("check_1_ids_not_in_the_metadata"), t.get("check_2_metadata_ids_not_in_this_table")
        if c1 and c1["count"]:
            parts.append(f"{c1['count']} id(s) not in the metadata")
        if c2 and c2["count"]:
            parts.append(f"{c2['count']} id(s) of the metadata not in this table")
        c3 = t.get("check_3_difference_after_the_completion")
        if c3 and c3["count"]:
            parts.append(f"BUG OF THE APP: {c3['count']} id(s) differ after the completion: {', '.join(c3['ids'])}")
        head.append("  " + "; ".join(parts) + ".")
    return "\n".join(head)


def read_log(path: Path) -> Dict[str, Any]:
    """The log file as data; an empty log when the file does not exist. A file with another format number, or that is not a log, is refused with a plain error
    (never read as if it were this format)."""
    path = Path(path)
    if not path.exists():
        return {"format": FORMAT, "entries": []}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("format") != FORMAT or not isinstance(data.get("entries"), list):
        raise ValueError(f"The log of the ids {path} is not a log of format {FORMAT}: it is left as it is and nothing is added to it.")
    return data


def _write_atomic(path: Path, data: Dict[str, Any]) -> None:
    """Write the file whole or not at all (a partial log could be read as an empty one)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".id_log_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=True)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _same_state(entry: Dict[str, Any], last: Optional[Dict[str, Any]]) -> bool:
    return bool(last) and last.get("recipe_sha256") == entry["recipe_sha256"] and last.get("data_batch_hash") == entry["data_batch_hash"]


def write_entry(folder: Path, entry: Dict[str, Any]) -> LogOutcome:
    """Add the entry of kind `checks` to the log of its recipe, unless the last `checks` entry says the same state (same recipe, same data): then nothing is
    added (`new` False, `written` True). When the folder cannot be written: the text is printed to the console and returned, `written` False, nothing raised."""
    text = entry_text(entry)
    path = log_path(folder, entry["recipe"])
    try:
        log = read_log(path)
        checks = [e for e in log["entries"] if isinstance(e, dict) and e.get("kind") == CHECKS]
        if _same_state(entry, checks[-1] if checks else None):
            return LogOutcome(True, False, path, text)
        log["entries"].append(entry)
        _write_atomic(path, log)
        return LogOutcome(True, True, path, text)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        problem = f"The log of the ids could not be written to {path}: {exc}"
        print(f"[ids] {problem}\n{text}")
        return LogOutcome(False, False, None, text, problem)


def record_read(folder: Path, recipe_id: str, recipe_sha256: str, data_batch_hash: str, who: str, when: Optional[str] = None) -> LogOutcome:
    """Record that a person has read the log of the ids of this recipe and data ("I have read this"). The button in HOME calls it. `who`
    is what the person gave (initials or a name); it must not be empty or be the word of the automatic entries."""
    if not who or not who.strip() or who.strip() == AUTOMATIC:
        raise ValueError("A record that the log was read needs the name or the initials of the person who read it.")
    entry = {"kind": READ, "when": when or _now(), "who": who.strip(), "recipe": recipe_id, "recipe_sha256": recipe_sha256, "data_batch_hash": data_batch_hash}
    text = entry_text(entry)
    path = log_path(folder, recipe_id)
    try:
        log = read_log(path)
        log["entries"].append(entry)
        _write_atomic(path, log)
        return LogOutcome(True, True, path, text)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        problem = f"The record that the log was read could not be written to {path}: {exc}"
        print(f"[ids] {problem}")
        return LogOutcome(False, False, None, text, problem)

