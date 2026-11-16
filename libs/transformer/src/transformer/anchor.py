"""Tier 1 and Tier 2 anchors on disk: written and read by the engine, never named in a recipe.

`sink_parquet` and `scan_parquet` used to be recipe actions. A recipe that writes to a path of its choice is a way to
overwrite any file, so they are engine functions now: the orchestrator calls them with paths it builds from the `cache`
location (spec DEC42, section 15).

# @deps
# provides: function:write_anchor, function:read_anchor, function:read_anchor_if_key, function:open_anchor, function:remove_orphan_temporaries
# consumed_by: app/modules/orchestrator.py
# doc: .claude/design/recipe_format_spec.md (DEC42), .claude/knowledge/architecture_decisions.md (ADR-024, ADR-031, ADR-089)
# @end_deps
"""
import os
import re
import tempfile
import time
from typing import Callable, Dict, List, Optional, Tuple

import polars as pl
from polars.exceptions import PanicException

from transformer.join_diagnosis import explain_validation_error
from utils.errors import TransformationError

# A temporary file of a write in progress is named `.<table>.parquet.<random>.tmp`. One older than this is a leftover of a
# writer that was killed (a table written takes seconds; the file is only created when the table is complete in memory).
ORPHAN_AGE_SECONDS = 600
_TEMPORARY_NAME = re.compile(r"^\..+\.parquet\..+\.tmp$")


def remove_orphan_temporaries(folder, table_file_name: Optional[str] = None, max_age: float = ORPHAN_AGE_SECONDS,
                              now: Optional[float] = None) -> List[str]:
    """Delete the temporary files that a killed writer left in a store folder; returns the names removed.

    Only files named like the temporary files of `write_anchor` and older than `max_age` seconds are touched, so the file
    of a write in progress (another process) is never removed. With `table_file_name` only the leftovers of that table.
    A temporary file is a hidden `.tmp` file: nothing that lists `*.parquet` reads it as a table.
    """
    removed: List[str] = []
    if not os.path.isdir(folder):
        return removed
    now = time.time() if now is None else now
    prefix = f".{table_file_name}." if table_file_name else None
    for name in os.listdir(folder):
        if not _TEMPORARY_NAME.match(name) or (prefix and not name.startswith(prefix)):
            continue
        full = os.path.join(folder, name)
        try:
            if now - os.stat(full).st_mtime >= max_age:
                os.unlink(full)
                removed.append(name)
        except FileNotFoundError:
            continue
        except OSError as exc:
            print(f"[anchor] could not remove the leftover temporary file {full}: {exc}")
    return removed


def open_anchor(path) -> Tuple[Dict[str, str], pl.LazyFrame]:
    """(the key-value metadata of the footer, a lazy scan) of ONE open file.

    The key and the content come from the same file, even when another process replaces the file by name right after
    (the open handle keeps the file it opened). Reading the key by name and then scanning by name can give the key of one
    file and the content of the next (STALE-KEY-STORE-1). The handle stays open as long as the scan is alive.
    """
    handle = open(path, "rb")
    try:
        footer = pl.read_parquet_metadata(handle)
        handle.seek(0)
        return dict(footer), pl.scan_parquet(handle)
    except BaseException:
        handle.close()
        raise


def read_anchor_if_key(path, meta_key: str, key: str) -> Optional[pl.LazyFrame]:
    """The stored table when the key in its footer is `key`; None when it is missing, unreadable or has another key.

    Never reused by file name alone (ADR-089): the key is read from the very file that is then scanned.
    """
    try:
        footer, scan = open_anchor(path)
    except (OSError, pl.exceptions.PolarsError):
        return None
    return scan if footer.get(meta_key) == key else None


def write_anchor(lf: pl.LazyFrame, path, decision_hash: Optional[str] = None, metadata: Optional[Dict[str, str]] = None,
                 join_checks: Optional[list] = None, still_valid: Optional[Callable[[], bool]] = None) -> pl.LazyFrame:
    """Write the table as Parquet and return a lazy scan of the written file.

    With a `decision_hash` the file carries it (and any extra `metadata`, text to text) in its footer, written by
    Polars itself: a table converted to Arrow and written with pyarrow can hold categorical columns that Polars cannot
    read back (issue #10, 2026-11-06). The key and the table are one file, so they can never be seen apart.

    The file is written under a temporary name in the same folder and renamed over the target in one step (STALE-KEY-STORE-1):
    another session that reads the stored table sees the old file or the new one, never a half-written one (a reader of a
    file rewritten in place was killed by the operating system, signal SIGBUS). The temporary file is only created when the
    table is complete in memory, and leftovers of killed writers of this table are removed first (`remove_orphan_temporaries`).

    `still_valid` (with a `decision_hash`): called once the file is complete, just before the rename. When it returns False
    the inputs the key was made from changed while the table was built; the table is NOT stored (the key would not say
    what the file holds) and the caller gets the table in memory.

    The returned scan is of the file just written (the same open file the key is read from), or, when another process
    replaced it at once, of the table in memory: it is never the content of another writer.

    `join_checks` (the assembler's `join_checks`) lets a refused `validate` of a join be explained in plain words after Polars raised it.
    """
    path = str(path)
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    remove_orphan_temporaries(folder, os.path.basename(path))
    temporary = None
    try:
        try:
            frame = lf.collect() if decision_hash else None
            handle, temporary = tempfile.mkstemp(prefix=f".{os.path.basename(path)}.", suffix=".tmp", dir=folder)
            os.close(handle)
            if decision_hash:
                frame.write_parquet(temporary, metadata={"sparmvet_decision_hash": str(decision_hash),
                                                         **{str(k): str(v) for k, v in (metadata or {}).items()}})
            else:
                lf.sink_parquet(temporary)
        except pl.exceptions.ComputeError as exc:
            explained = explain_validation_error(exc, join_checks)
            if explained is None:
                raise
            raise explained from exc
        except PanicException as exc:
            # The plan of every step runs here, so this is where a Rust panic of Polars shows. A `PanicException` is a `BaseException`:
            # it passes every `except Exception` of the engine and the app (ADR-104). Only this class is caught; KeyboardInterrupt and SystemExit pass.
            raise TransformationError(
                f"Polars stopped while it computed the table stored at {path}, on the input of one of the steps ({str(exc).strip()[:120]})",
                tip="Check the durations and lists written in the steps of this join and the data they work on; the actions refuse the cases they know "
                    "before Polars runs, so this one is new: report it with the recipe") from exc
        if still_valid is not None and not still_valid():
            return frame.lazy() if frame is not None else pl.scan_parquet(temporary).collect().lazy()
        # mkstemp makes the file private (0600); the stored table keeps the mode of the file it replaces (0644 for a new one).
        os.chmod(temporary, os.stat(path).st_mode & 0o777 if os.path.exists(path) else 0o644)
        with open(temporary, "rb") as written:
            os.fsync(written.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None and os.path.exists(temporary):
            os.unlink(temporary)
    if frame is None:
        return pl.scan_parquet(path)
    try:
        footer, scan = open_anchor(path)
    except (OSError, pl.exceptions.PolarsError):
        return frame.lazy()
    return scan if footer.get("sparmvet_decision_hash") == str(decision_hash) else frame.lazy()


def read_anchor(path) -> pl.LazyFrame:
    """A lazy scan of an anchor; a missing file fails and names the path."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Parquet anchor not found: {path}")
    return pl.scan_parquet(path)
