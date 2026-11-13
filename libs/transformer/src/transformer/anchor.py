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
from typing import Dict, Optional

import polars as pl


def write_anchor(lf: pl.LazyFrame, path, decision_hash: Optional[str] = None, metadata: Optional[Dict[str, str]] = None) -> pl.LazyFrame:
    """Write the table as Parquet and return a lazy scan of the written file.

    With a `decision_hash` the file carries it (and any extra `metadata`, text to text) in its footer, written by
    Polars itself: a table converted to Arrow and written with pyarrow can hold categorical columns that Polars cannot
    read back (issue #10, 2026-11-06).
    """
    path = str(path)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    if decision_hash:
        lf.collect().write_parquet(path, metadata={"sparmvet_decision_hash": str(decision_hash),
                                                   **{str(k): str(v) for k, v in (metadata or {}).items()}})
    else:
        lf.sink_parquet(path)
    return pl.scan_parquet(path)


def read_anchor(path) -> pl.LazyFrame:
    """A lazy scan of an anchor; a missing file fails and names the path."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Parquet anchor not found: {path}")
    return pl.scan_parquet(path)
