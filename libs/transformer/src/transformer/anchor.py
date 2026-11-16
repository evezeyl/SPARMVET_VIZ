"""Tier 1 and Tier 2 anchors on disk: written and read by the engine, never named in a recipe.

`sink_parquet` and `scan_parquet` used to be recipe actions. A recipe that writes to a path of its choice is a way to
overwrite any file, so they are engine functions now: the orchestrator calls them with paths it builds from the `cache`
location (spec DEC42, section 15).

# @deps
# provides: function:write_anchor, function:read_anchor
# consumed_by: app/modules/orchestrator.py
# doc: .claude/design/recipe_format_spec.md (DEC42), .claude/knowledge/architecture_decisions.md (ADR-024, ADR-031, ADR-089)
# @end_deps
"""
import os
import tempfile
from typing import Callable, Dict, Optional

import polars as pl
from polars.exceptions import PanicException

from transformer.join_diagnosis import explain_validation_error
from utils.errors import TransformationError


def write_anchor(lf: pl.LazyFrame, path, decision_hash: Optional[str] = None, metadata: Optional[Dict[str, str]] = None,
                 join_checks: Optional[list] = None, still_valid: Optional[Callable[[], bool]] = None) -> pl.LazyFrame:
    """Write the table as Parquet and return a lazy scan of the written file.

    With a `decision_hash` the file carries it (and any extra `metadata`, text to text) in its footer, written by
    Polars itself: a table converted to Arrow and written with pyarrow can hold categorical columns that Polars cannot
    read back (issue #10, 2026-11-06). The key and the table are one file, so they can never be seen apart.

    The file is written under a temporary name in the same folder and renamed over the target in one step (STALE-KEY-STORE-1):
    another session that reads the stored table sees the old file or the new one, never a half-written one (a reader of a
    file rewritten in place was killed by the operating system, signal SIGBUS).

    `still_valid` (with a `decision_hash`): called once the file is complete, just before the rename. When it returns False
    the inputs the key was made from changed while the table was built; the table is NOT stored (the key would not say
    what the file holds) and the caller gets the table in memory.

    `join_checks` (the assembler's `join_checks`) lets a refused `validate` of a join be explained in plain words after Polars raised it.
    """
    path = str(path)
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{os.path.basename(path)}.", suffix=".tmp", dir=folder)
    os.close(handle)
    try:
        frame = None
        try:
            if decision_hash:
                frame = lf.collect()
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
    return pl.scan_parquet(path)


def read_anchor(path) -> pl.LazyFrame:
    """A lazy scan of an anchor; a missing file fails and names the path."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Parquet anchor not found: {path}")
    return pl.scan_parquet(path)
