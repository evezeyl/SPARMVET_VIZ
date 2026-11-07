import hashlib
import json
from typing import Any, Dict, List

# @deps
# provides: function:generate_config_hash
# consumed_by: app/modules/orchestrator.py, libs/transformer/tests/debug_assembler.py
# @end_deps


def generate_config_hash(config: Any) -> str:
    """
    Generates a deterministic SHA-256 hash for a python object (a data analysis recipe or a step list).
    Useful for detecting if the logic that generated a cache has changed.
    """
    # Deterministic serialization: sort keys, remove whitespace
    try:
        encoded = json.dumps(config, sort_keys=True,
                             indent=None).encode('utf-8')
    except (TypeError, ValueError):
        # Fallback for objects that aren't JSON serializable (like LazyFrames)
        # We just stringify them as a last resort
        encoded = str(config).encode('utf-8')

    return hashlib.sha256(encoded).hexdigest()


def get_parquet_metadata_hash(path: str, key: str = "sparmvet_decision_hash") -> str | None:
    """
    Retrieves a specific metadata key from a Parquet file without reading the data.
    """
    import polars as pl
    try:
        # Polars scan_parquet doesn't directly expose metadata easily in older versions
        # but we can try scan + metadata if available, or use pyarrow
        import pyarrow.parquet as pq
        meta = pq.read_metadata(path)
        # PyArrow metadata is in 'metadata' (key-value)
        if meta.metadata:
            # Metadata keys in pyarrow are bytes
            b_key = key.encode('utf-8')
            if b_key in meta.metadata:
                return meta.metadata[b_key].decode('utf-8')
    except Exception:
        pass
    return None
