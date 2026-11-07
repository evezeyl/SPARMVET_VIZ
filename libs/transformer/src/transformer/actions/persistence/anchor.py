from typing import Dict, Any, Union
import polars as pl
import os
from transformer.actions.base import register_action

# @deps
# provides: action:sink_parquet, action:scan_parquet
# consumed_by: app/modules/orchestrator.py (injected into step list), libs/transformer/tests/debug_assembler.py (injected into step list)
# doc: .claude/rules/rules_data_engine.md
# @end_deps


@register_action("sink_parquet")
def action_sink_parquet(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Tier 1 Persistence Action (ADR-024).
    Sinks the query to disk as a Parquet file for long-term session anchoring.
    Returns a new LazyFrame scanning the written file.
    Includes ADR-024 refinement for Decision Metadata Hashing.
    """
    path = spec.get("path")
    decision_hash = spec.get("decision_hash")
    # ADR-089: extra Parquet metadata (str -> str), e.g. the chained stage key. Only written
    # on the metadata path, so it requires decision_hash to be set.
    extra_metadata = spec.get("metadata") or {}

    if not path:
        raise ValueError("Action 'sink_parquet' requires a 'path' parameter.")

    # Ensure parent directory exists
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    if decision_hash:
        # ADR-031: Use Eager write to support custom metadata hashing
        print(
            f"      └── Materializing Anchor (Tier 1) with Logic Hash: {decision_hash[:8]}... to: {path}")
        df = lf.collect()

        # Written by Polars itself, with the metadata in the file: a table converted to Arrow and
        # written with pyarrow can hold categorical columns that Polars cannot read back
        # ("Decoding ByteArray Plain-encoded optional parquet pages not yet supported"), found
        # on the real Tier 2 of the ST22 dummy project (issue #10, 2026-11-06).
        meta = {
            "sparmvet_decision_hash": str(decision_hash),
            **{str(k): str(v) for k, v in extra_metadata.items()},
        }
        df.write_parquet(path, metadata=meta)
    else:
        # Standard streaming sink
        print(f"      └── 💾 Materializing Anchor (Tier 1) to: {path}")
        lf.sink_parquet(path)

    return pl.scan_parquet(path)


@register_action("scan_parquet")
def action_scan_parquet(lf: Union[None, pl.LazyFrame], spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Scanner for existing Parquet anchors. 
    Can be used as a starting action if 'lf' is None.
    """
    path = spec.get("path")
    if not path:
        raise ValueError("Action 'scan_parquet' requires a 'path' parameter.")

    if not os.path.exists(path):
        raise FileNotFoundError(f"Parquet anchor not found: {path}")

    return pl.scan_parquet(path)
