from typing import Dict, Any, Union
import polars as pl
import os
from transformer.actions.base import register_action

# @deps
# provides: action:sink_parquet, action:scan_parquet
# consumed_by: app/modules/orchestrator.py (injected into recipe), libs/transformer/tests/debug_assembler.py (injected into recipe)
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

    if not path:
        raise ValueError("Action 'sink_parquet' requires a 'path' parameter.")

    # Ensure parent directory exists
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    if decision_hash:
        # ADR-031: Use Eager write to support custom metadata hashing
        print(
            f"      └── 💾 Materializing Anchor (Tier 1) with Logic Hash: {decision_hash[:8]}... to: {path}")
        df = lf.collect()

        # Polars write_parquet 'custom_metadata' is only in recent versions.
        # Fallback to pyarrow to ensure absolute metadata authority.
        import pyarrow as pa
        import pyarrow.parquet as pq

        table = df.to_arrow()
        existing_meta = table.schema.metadata or {}
        # Metadata keys/values in Arrow must be bytes
        new_meta = {
            **existing_meta,
            b"sparmvet_decision_hash": decision_hash.encode("utf-8")
        }
        table = table.replace_schema_metadata(new_meta)
        pq.write_table(table, path)
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
